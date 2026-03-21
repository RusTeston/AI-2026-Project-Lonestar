import json
import os
import uuid
import boto3

s3 = boto3.client('s3')
sqs = boto3.client('sqs')

def handler(event, context):
    try:
        body = json.loads(event.get('body', '{}'))
        template_text = body.get('template', '').strip()

        if not template_text:
            return response(400, {'error': 'No template provided'})

        if len(template_text) > 51200:
            return response(400, {'error': 'Template exceeds 50KB limit'})

        job_id = str(uuid.uuid4())

        s3.put_object(
            Bucket=os.environ['BUCKET_NAME'],
            Key=f'templates/{job_id}.yaml',
            Body=template_text.encode('utf-8')
        )

        sqs.send_message(
            QueueUrl=os.environ['QUEUE_URL'],
            MessageBody=json.dumps({'jobId': job_id})
        )

        return response(200, {'jobId': job_id, 'status': 'QUEUED'})

    except json.JSONDecodeError:
        return response(400, {'error': 'Invalid JSON'})
    except Exception as e:
        print(f'Error: {e}')
        return response(500, {'error': 'Internal server error'})

def response(code, body):
    return {
        'statusCode': code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps(body)
    }
