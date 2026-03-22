import json
import os
import boto3

TABLE_NAME = os.environ['TABLE_NAME']
ddb = boto3.resource('dynamodb').Table(TABLE_NAME)

def handler(event, context):
    """Simulated primary region endpoint. Returns healthy or unhealthy based on DynamoDB flag."""
    try:
        resp = ddb.get_item(Key={'pk': 'CONFIG', 'sk': 'endpoint_status'})
        status = resp.get('Item', {}).get('status', 'healthy')
    except Exception:
        status = 'healthy'

    if status == 'unhealthy':
        return {
            'statusCode': 503,
            'body': json.dumps({'status': 'unhealthy', 'region': 'us-east-1', 'simulated': True})
        }

    return {
        'statusCode': 200,
        'body': json.dumps({'status': 'healthy', 'region': 'us-east-1', 'simulated': True})
    }


def toggle_handler(event, context):
    """API handler to toggle simulated endpoint between healthy/unhealthy."""
    body = json.loads(event.get('body') or '{}')
    new_status = body.get('status', 'unhealthy')

    if new_status not in ('healthy', 'unhealthy'):
        return {
            'statusCode': 400,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'status must be healthy or unhealthy'})
        }

    ddb.put_item(Item={'pk': 'CONFIG', 'sk': 'endpoint_status', 'status': new_status})

    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
        'body': json.dumps({'status': new_status, 'message': f'Endpoint set to {new_status}'})
    }
