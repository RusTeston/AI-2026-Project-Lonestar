import json
import os
import time
import urllib.request
import boto3
from datetime import datetime

TABLE_NAME = os.environ['TABLE_NAME']
ENDPOINT_URL = os.environ.get('ENDPOINT_URL', '')
STATE_MACHINE_ARN = os.environ.get('STATE_MACHINE_ARN', '')

ddb = boto3.resource('dynamodb').Table(TABLE_NAME)
sfn = boto3.client('stepfunctions')


def handler(event, context):
    """Scheduled health check — hits simulated endpoint, stores result, triggers Step Functions on failure."""
    timestamp = datetime.utcnow().isoformat() + 'Z'
    ttl = int(time.time()) + 86400  # 24h TTL

    # Check endpoint
    result = _check_endpoint()

    # Store health check result
    ddb.put_item(Item={
        'pk': 'HEALTHCHECK',
        'sk': timestamp,
        'status': result['status'],
        'status_code': result['status_code'],
        'latency_ms': result['latency_ms'],
        'error': result.get('error', ''),
        'ttl': ttl
    })

    # Update current status
    ddb.put_item(Item={
        'pk': 'CONFIG',
        'sk': 'current_status',
        'status': result['status'],
        'last_check': timestamp,
        'latency_ms': result['latency_ms']
    })

    # If unhealthy, trigger Step Functions
    if result['status'] == 'unhealthy':
        sfn.start_execution(
            stateMachineArn=STATE_MACHINE_ARN,
            input=json.dumps({
                'trigger': 'scheduled_health_check',
                'timestamp': timestamp,
                'health_result': result
            })
        )

    return result


def _check_endpoint():
    """Hit the simulated endpoint and measure response."""
    if not ENDPOINT_URL:
        return {'status': 'unhealthy', 'status_code': 0, 'latency_ms': 0, 'error': 'No endpoint configured'}

    start = time.time()
    try:
        req = urllib.request.Request(ENDPOINT_URL, method='GET')
        resp = urllib.request.urlopen(req, timeout=10)
        latency = int((time.time() - start) * 1000)
        status_code = resp.getcode()
        return {
            'status': 'healthy' if status_code == 200 else 'unhealthy',
            'status_code': status_code,
            'latency_ms': latency
        }
    except Exception as e:
        latency = int((time.time() - start) * 1000)
        return {
            'status': 'unhealthy',
            'status_code': 0,
            'latency_ms': latency,
            'error': str(e)
        }


def status_handler(event, context):
    """API handler — returns current health status and recent checks."""
    # Get current status
    try:
        resp = ddb.get_item(Key={'pk': 'CONFIG', 'sk': 'current_status'})
        current = resp.get('Item', {'status': 'unknown'})
        current.pop('pk', None)
        current.pop('sk', None)
    except Exception:
        current = {'status': 'unknown'}

    # Get last 10 health checks
    recent = _get_recent_checks(10)

    # Get active incident if any
    incident = _get_active_incident()

    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
        'body': json.dumps({
            'current': current,
            'recent_checks': recent,
            'active_incident': incident
        }, default=str)
    }


def history_handler(event, context):
    """API handler — returns incident history."""
    resp = ddb.query(
        KeyConditionExpression=boto3.dynamodb.conditions.Key('pk').eq('INCIDENT'),
        ScanIndexForward=False,
        Limit=20
    )
    incidents = resp.get('Items', [])
    for i in incidents:
        i.pop('pk', None)

    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
        'body': json.dumps({'incidents': incidents}, default=str)
    }


def _get_recent_checks(limit):
    """Query last N health checks from DynamoDB."""
    resp = ddb.query(
        KeyConditionExpression=boto3.dynamodb.conditions.Key('pk').eq('HEALTHCHECK'),
        ScanIndexForward=False,
        Limit=limit
    )
    items = resp.get('Items', [])
    for item in items:
        item.pop('pk', None)
        item['timestamp'] = item.pop('sk', '')
    return items


def _get_active_incident():
    """Check for active (unresolved) incident."""
    try:
        resp = ddb.get_item(Key={'pk': 'CONFIG', 'sk': 'active_incident'})
        item = resp.get('Item')
        if item:
            item.pop('pk', None)
            item.pop('sk', None)
            return item
    except Exception:
        pass
    return None
