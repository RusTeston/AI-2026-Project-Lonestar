import json
import os
import boto3

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')

TABLE_NAME = os.environ['TABLE_NAME']
BUCKET_NAME = os.environ['BUCKET_NAME']
MODEL_ID = 'us.amazon.nova-lite-v1:0'

SYSTEM_PROMPT = """You are an expert AWS Solutions Architect who reviews infrastructure templates against the AWS Well-Architected Framework. Analyze the provided CloudFormation or SAM template and return findings.

For each finding, evaluate against these 6 WAF pillars:
- Operational Excellence: Monitoring, logging, automation, IaC practices
- Security: IAM least privilege, encryption, network controls, secrets management
- Reliability: Multi-AZ, backups, fault tolerance, recovery procedures
- Performance Efficiency: Right-sizing, caching, scaling configuration
- Cost Optimization: Right-sizing, lifecycle policies, on-demand vs provisioned
- Sustainability: Resource efficiency, managed services usage

Return ONLY valid JSON in this exact format (no markdown, no code fences):
{
  "summary": "Brief overall assessment in 1-2 sentences",
  "findings": [
    {
      "pillar": "Security",
      "severity": "HIGH",
      "title": "Short title",
      "description": "What the issue is",
      "recommendation": "How to fix it"
    }
  ]
}

Rules:
- severity must be one of: CRITICAL, HIGH, MEDIUM, LOW, INFO
- Sort findings by severity (CRITICAL first, INFO last)
- Include positive findings as INFO severity
- Be specific — reference actual resource names from the template
- Limit to 10 most important findings"""

def handler(event, context):
    for record in event['Records']:
        msg = json.loads(record['body'])
        job_id = msg['jobId']
        table = dynamodb.Table(TABLE_NAME)

        try:
            table.put_item(Item={'jobId': job_id, 'status': 'ANALYZING'})

            obj = s3.get_object(Bucket=BUCKET_NAME, Key=f'templates/{job_id}.yaml')
            template_text = obj['Body'].read().decode('utf-8')

            result = bedrock.invoke_model(
                modelId=MODEL_ID,
                contentType='application/json',
                accept='application/json',
                body=json.dumps({
                    'schemaVersion': 'messages-v1',
                    'system': [{'text': SYSTEM_PROMPT}],
                    'messages': [
                        {
                            'role': 'user',
                            'content': [{'text': f'Review this template:\n\n{template_text}'}]
                        }
                    ],
                    'inferenceConfig': {
                        'maxTokens': 2048,
                        'temperature': 0.2
                    }
                })
            )

            response_body = json.loads(result['body'].read())
            ai_text = response_body['output']['message']['content'][0]['text']

            # Parse the AI response as JSON
            try:
                findings = json.loads(ai_text)
            except json.JSONDecodeError:
                # Try to extract JSON from response if wrapped in text
                start = ai_text.find('{')
                end = ai_text.rfind('}') + 1
                if start >= 0 and end > start:
                    findings = json.loads(ai_text[start:end])
                else:
                    findings = {'summary': 'Analysis complete but response parsing failed.', 'findings': []}

            table.put_item(Item={
                'jobId': job_id,
                'status': 'COMPLETE',
                'results': json.dumps(findings)
            })

        except Exception as e:
            print(f'Error analyzing {job_id}: {e}')
            table.put_item(Item={
                'jobId': job_id,
                'status': 'FAILED',
                'error': str(e)
            })
