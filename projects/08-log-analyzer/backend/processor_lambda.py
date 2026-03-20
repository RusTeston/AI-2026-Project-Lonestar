import json
import os
import boto3
from datetime import datetime
from urllib.parse import unquote_plus

s3 = boto3.client('s3')
bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')

BUCKET_NAME = os.environ['BUCKET_NAME']

def lambda_handler(event, context):
    """Process log file uploaded to S3"""
    
    record = event['Records'][0]
    bucket = record['s3']['bucket']['name']
    key = unquote_plus(record['s3']['object']['key'])
    
    print(f"Processing: s3://{bucket}/{key}")
    
    filename = key.split('/')[-1]
    
    try:
        # Read log file
        response = s3.get_object(Bucket=bucket, Key=key)
        log_content = response['Body'].read().decode('utf-8', errors='replace')
        
        print(f"Read {len(log_content)} characters")
        
        # Analyze with Bedrock
        analysis = analyze_logs(log_content, filename)
        
        # Save results
        result = {
            'filename': filename,
            'analysis': analysis,
            'log_size': len(log_content),
            'processed_at': datetime.utcnow().isoformat() + 'Z'
        }
        
        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=f"results/{filename}.json",
            Body=json.dumps(result),
            ContentType='application/json'
        )
        
        print(f"Results saved for {filename}")
        return {'statusCode': 200, 'body': 'Success'}
        
    except Exception as e:
        print(f"Error: {str(e)}")
        
        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=f"results/{filename}.error.json",
            Body=json.dumps({
                'filename': filename,
                'error': str(e),
                'processed_at': datetime.utcnow().isoformat() + 'Z'
            }),
            ContentType='application/json'
        )
        raise


def analyze_logs(log_content, filename):
    """Analyze log content with Bedrock Nova Lite"""
    
    # Send up to 15000 chars for thorough analysis
    log_sample = log_content[:15000]
    
    prompt = f"""You are an expert log analyst and systems engineer. Analyze the following log file thoroughly and provide a comprehensive, actionable report.

Log file name: {filename}
Log content:
{log_sample}

Provide your analysis in the following JSON format. Be detailed and specific - reference actual log entries, timestamps, and error messages you find:

{{
  "log_type": "Type of log (e.g., application server, web server, database, system, cloud service, CI/CD, etc.)",
  "severity": "Overall severity: CRITICAL, HIGH, MEDIUM, LOW, or INFO",
  "summary": "2-3 sentence executive summary of what this log shows and the most important findings",
  "errors": [
    {{
      "error": "Exact error message or pattern found",
      "count": "Number of occurrences (or 1 if single)",
      "severity": "CRITICAL/HIGH/MEDIUM/LOW",
      "line_reference": "Line number or timestamp where this appears",
      "root_cause": "Detailed explanation of what is causing this error",
      "fix": "Specific, step-by-step instructions to fix this issue"
    }}
  ],
  "warnings": [
    {{
      "warning": "Warning message or pattern",
      "count": "Number of occurrences",
      "impact": "What could happen if this is ignored"
    }}
  ],
  "patterns": [
    {{
      "pattern": "Description of recurring pattern detected",
      "frequency": "How often it occurs",
      "significance": "Why this pattern matters"
    }}
  ],
  "timeline": "Brief chronological narrative of what happened in this log - what started, what failed, what recovered",
  "recommended_actions": [
    {{
      "priority": "1 (highest) through N",
      "action": "Specific action to take",
      "reason": "Why this action is important",
      "commands": "Any specific commands, config changes, or code fixes to run (if applicable)"
    }}
  ],
  "prevention_tips": [
    "Specific tip to prevent these issues from recurring"
  ]
}}

Respond ONLY with valid JSON. Be thorough and specific - generic advice is not helpful. Reference actual entries from the log."""

    response = bedrock.invoke_model(
        modelId='us.amazon.nova-lite-v1:0',
        body=json.dumps({
            'messages': [{'role': 'user', 'content': [{'text': prompt}]}],
            'inferenceConfig': {'temperature': 0.3, 'maxTokens': 4000}
        })
    )
    
    result = json.loads(response['body'].read())
    content = result['output']['message']['content'][0]['text']
    
    # Extract JSON from response
    start = content.find('{')
    end = content.rfind('}') + 1
    
    if start >= 0 and end > start:
        return json.loads(content[start:end])
    
    return {
        'log_type': 'Unknown',
        'severity': 'UNKNOWN',
        'summary': 'Unable to analyze log file',
        'errors': [],
        'warnings': [],
        'patterns': [],
        'timeline': '',
        'recommended_actions': [],
        'prevention_tips': []
    }
