import json
import os
import boto3

s3 = boto3.client('s3')
bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')

BUCKET = os.environ['BUCKET_NAME']
MODEL_ID = 'us.amazon.nova-lite-v1:0'

SYSTEM_PROMPT = """You are an AWS Cost Optimization expert. Analyze these AWS account findings and generate a cost optimization report.

For each finding:
- Explain WHY it's wasteful in plain English
- Estimate monthly savings in USD
- Provide the exact remediation action

Return ONLY valid JSON (no markdown, no code fences):
{
  "summary": "1-2 sentence overall assessment with total estimated monthly savings",
  "total_estimated_savings": 0.00,
  "findings": [
    {
      "category": "EBS|EC2|RDS|S3|Lambda|General",
      "severity": "CRITICAL|HIGH|MEDIUM|LOW|INFO",
      "title": "Short title",
      "description": "Plain English explanation of the waste",
      "estimated_monthly_savings": 0.00,
      "remediation": "Exact steps to fix"
    }
  ]
}

Rules:
- Sort by estimated_monthly_savings descending
- Be specific with resource IDs
- If no issues found in a category, include an INFO finding noting good practices
- Limit to 15 most impactful findings"""


def handler(event, context):
    scan_id = event['scanId']

    try:
        obj = s3.get_object(Bucket=BUCKET, Key=f'scans/{scan_id}/raw.json')
        findings = json.loads(obj['Body'].read().decode('utf-8'))

        result = bedrock.invoke_model(
            modelId=MODEL_ID,
            contentType='application/json',
            accept='application/json',
            body=json.dumps({
                'schemaVersion': 'messages-v1',
                'system': [{'text': SYSTEM_PROMPT}],
                'messages': [{'role': 'user', 'content': [{'text': f'Analyze these findings:\n\n{json.dumps(findings)}'}]}],
                'inferenceConfig': {'maxTokens': 3000, 'temperature': 0.2}
            })
        )

        body = json.loads(result['body'].read())
        ai_text = body['output']['message']['content'][0]['text']

        try:
            report = json.loads(ai_text)
        except json.JSONDecodeError:
            start = ai_text.find('{')
            end = ai_text.rfind('}') + 1
            if start >= 0 and end > start:
                report = json.loads(ai_text[start:end])
            else:
                report = {'summary': 'Analysis complete but parsing failed.', 'findings': []}

        s3.put_object(
            Bucket=BUCKET,
            Key=f'scans/{scan_id}/report.json',
            Body=json.dumps(report).encode('utf-8')
        )

        # Chain to notify
        notify_fn = os.environ.get('NOTIFY_FUNCTION')
        if notify_fn:
            boto3.client('lambda').invoke(
                FunctionName=notify_fn,
                InvocationType='Event',
                Payload=json.dumps({'scanId': scan_id})
            )

    except Exception as e:
        print(f'Error analyzing scan {scan_id}: {e}')
        raise
