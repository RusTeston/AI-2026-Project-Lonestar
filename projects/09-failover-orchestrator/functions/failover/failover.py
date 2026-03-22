import json
import os
import time
import urllib.request
import boto3
from datetime import datetime

TABLE_NAME = os.environ['TABLE_NAME']
SLACK_WEBHOOK_URL = os.environ.get('SLACK_WEBHOOK_URL', '')

ddb = boto3.resource('dynamodb').Table(TABLE_NAME)


def handler(event, context):
    """Simulate multi-region failover: Route 53 update, resource warming, incident logging, Slack notification."""
    timestamp = datetime.utcnow().isoformat() + 'Z'
    verdict = event.get('verdict', {})

    # Build incident timeline
    timeline = []

    # Step 1: Detect
    timeline.append({
        'time': timestamp,
        'action': 'FAILURE_DETECTED',
        'detail': 'Primary region health check failures confirmed by AI analysis'
    })

    # Step 2: Simulate Route 53 failover
    time.sleep(1)
    timeline.append({
        'time': datetime.utcnow().isoformat() + 'Z',
        'action': 'ROUTE53_UPDATE [SIMULATED]',
        'detail': 'DNS record updated: rus-app.example.com → us-west-2 standby endpoint (TTL: 60s)'
    })

    # Step 3: Simulate standby resource warming
    time.sleep(1)
    timeline.append({
        'time': datetime.utcnow().isoformat() + 'Z',
        'action': 'RESOURCE_WARMING [SIMULATED]',
        'detail': 'Standby region us-west-2: ECS tasks scaled from 0→2, RDS replica promoted, ElastiCache warmed'
    })

    # Step 4: Simulate health verification of standby
    time.sleep(1)
    timeline.append({
        'time': datetime.utcnow().isoformat() + 'Z',
        'action': 'STANDBY_VERIFIED [SIMULATED]',
        'detail': 'Standby region us-west-2 health check passed — 200 OK, latency 45ms'
    })

    # Step 5: Failover complete
    timeline.append({
        'time': datetime.utcnow().isoformat() + 'Z',
        'action': 'FAILOVER_COMPLETE [SIMULATED]',
        'detail': 'Traffic now routing to us-west-2. Estimated RTO: ~4 minutes. RPO: 0 (read replicas).'
    })

    # Store incident in DynamoDB
    incident = {
        'pk': 'INCIDENT',
        'sk': timestamp,
        'status': 'resolved',
        'verdict': verdict,
        'timeline': timeline,
        'failover_region': 'us-west-2',
        'simulated': True,
        'ttl': int(time.time()) + 604800  # 7 day TTL
    }
    ddb.put_item(Item=incident)

    # Mark active incident
    ddb.put_item(Item={
        'pk': 'CONFIG',
        'sk': 'active_incident',
        'incident_id': timestamp,
        'status': 'resolved',
        'failover_region': 'us-west-2',
        'simulated': True
    })

    # Post to Slack if configured
    if SLACK_WEBHOOK_URL:
        _post_slack(verdict, timeline)

    return {
        'action': 'failover_executed',
        'simulated': True,
        'incident_id': timestamp,
        'timeline_steps': len(timeline),
        'slack_notified': bool(SLACK_WEBHOOK_URL)
    }


def _post_slack(verdict, timeline):
    """Post incident timeline to Slack via incoming webhook."""
    timeline_text = '\n'.join(
        f"• `{t['time'][:19]}` *{t['action']}*\n  {t['detail']}" for t in timeline
    )

    payload = {
        'blocks': [
            {
                'type': 'header',
                'text': {'type': 'plain_text', 'text': '🚨 FAILOVER EXECUTED [SIMULATED]'}
            },
            {
                'type': 'section',
                'text': {
                    'type': 'mrkdwn',
                    'text': f"*AI Verdict:* {verdict.get('reasoning', 'N/A')}\n*Confidence:* {verdict.get('confidence', 'N/A')}"
                }
            },
            {'type': 'divider'},
            {
                'type': 'section',
                'text': {'type': 'mrkdwn', 'text': f"*Incident Timeline:*\n{timeline_text}"}
            },
            {
                'type': 'context',
                'elements': [{'type': 'mrkdwn', 'text': '_This is a simulated failover from Project 09 — Failover Orchestrator_'}]
            }
        ]
    }

    try:
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(SLACK_WEBHOOK_URL, data=data, headers={'Content-Type': 'application/json'})
        urllib.request.urlopen(req, timeout=10)
    except Exception as e:
        print(f'Slack notification failed: {e}')
