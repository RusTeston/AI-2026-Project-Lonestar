import json
import os
import boto3
from decimal import Decimal

TABLE_NAME = os.environ['TABLE_NAME']
MODEL_ID = 'us.amazon.nova-lite-v1:0'

ddb = boto3.resource('dynamodb').Table(TABLE_NAME)
bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')


def handler(event, context):
    """Gather health check evidence and ask Bedrock to reason about whether failover is warranted."""
    # Get last 5 health checks
    checks = _get_recent_checks(5)

    if not checks:
        return {
            'failover_warranted': False,
            'confidence': 'low',
            'reasoning': 'No health check data available to evaluate.'
        }

    # Build evidence summary
    evidence = _build_evidence(checks)

    # Ask Bedrock to reason over the evidence
    verdict = _get_bedrock_verdict(evidence)

    return verdict


def _get_recent_checks(limit):
    resp = ddb.query(
        KeyConditionExpression=boto3.dynamodb.conditions.Key('pk').eq('HEALTHCHECK'),
        ScanIndexForward=False,
        Limit=limit
    )
    return resp.get('Items', [])


def _build_evidence(checks):
    total = len(checks)
    failures = sum(1 for c in checks if c['status'] == 'unhealthy')
    failure_rate = (failures / total) * 100 if total > 0 else 0

    # Detect trend: are failures consecutive and recent?
    consecutive_failures = 0
    for c in checks:  # already sorted newest-first
        if c['status'] == 'unhealthy':
            consecutive_failures += 1
        else:
            break

    # Format check details
    check_details = []
    for c in checks:
        check_details.append({
            'timestamp': c.get('sk', ''),
            'status': c['status'],
            'status_code': int(c.get('status_code', 0)),
            'latency_ms': int(c.get('latency_ms', 0)),
            'error': c.get('error', '')
        })

    return {
        'total_checks': total,
        'failures': failures,
        'failure_rate_pct': failure_rate,
        'consecutive_failures': consecutive_failures,
        'trend': 'degrading' if consecutive_failures >= 3 else 'unstable' if failures > 0 else 'stable',
        'checks': check_details
    }


def _get_bedrock_verdict(evidence):
    prompt = f"""You are an AWS Site Reliability Engineer evaluating whether a multi-region failover should be triggered.

Analyze the following health check evidence from the primary region endpoint and return a JSON verdict.

EVIDENCE:
{json.dumps(evidence, indent=2)}

RULES:
- If 4+ of the last 5 checks are unhealthy AND consecutive failures >= 3, failover is warranted with HIGH confidence.
- If 3 of the last 5 checks are unhealthy with consecutive failures >= 2, failover MAY be warranted with MEDIUM confidence.
- If only 1-2 checks are unhealthy, this is likely a transient blip — failover is NOT warranted, LOW confidence.
- If all checks are healthy, failover is NOT warranted.
- Consider latency spikes (>5000ms) as degradation signals even if status is healthy.

Return ONLY valid JSON in this exact format, no other text:
{{"failover_warranted": true/false, "confidence": "high"/"medium"/"low", "reasoning": "your analysis here"}}"""

    body = json.dumps({
        'messages': [{'role': 'user', 'content': [{'text': prompt}]}],
        'inferenceConfig': {'maxTokens': 300, 'temperature': 0.1}
    })

    resp = bedrock.invoke_model(modelId=MODEL_ID, contentType='application/json', accept='application/json', body=body)
    result = json.loads(resp['body'].read())
    text = result['output']['message']['content'][0]['text'].strip()

    # Parse JSON from response
    try:
        # Handle markdown code blocks
        if '```' in text:
            text = text.split('```')[1]
            if text.startswith('json'):
                text = text[4:]
            text = text.strip()
        verdict = json.loads(text)
        # Validate required fields
        if not all(k in verdict for k in ('failover_warranted', 'confidence', 'reasoning')):
            raise ValueError('Missing fields')
        # Normalize confidence to lowercase
        verdict['confidence'] = verdict['confidence'].lower()
        return verdict
    except Exception:
        return {
            'failover_warranted': False,
            'confidence': 'low',
            'reasoning': f'Failed to parse Bedrock response: {text[:200]}'
        }
