import json
import os
import boto3

dynamodb = boto3.resource('dynamodb')
TABLE_NAME = os.environ['TABLE_NAME']

def handler(event, context):
    job_id = event.get('pathParameters', {}).get('jobId', '')

    if not job_id:
        return response(400, {'error': 'Missing jobId'})

    try:
        table = dynamodb.Table(TABLE_NAME)
        item = table.get_item(Key={'jobId': job_id})

        if 'Item' not in item:
            return response(404, {'error': 'Job not found'})

        record = item['Item']
        status = record.get('status', 'UNKNOWN')

        if status == 'COMPLETE':
            results = json.loads(record.get('results', '{}'))
            return response(200, {'jobId': job_id, 'status': status, 'results': results})
        elif status == 'FAILED':
            return response(200, {'jobId': job_id, 'status': status, 'error': record.get('error', 'Unknown error')})
        else:
            return response(200, {'jobId': job_id, 'status': status})

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
