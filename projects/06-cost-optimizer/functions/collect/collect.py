import json
import os
import boto3
from datetime import datetime, timedelta

s3 = boto3.client('s3')
ce = boto3.client('ce')
ec2 = boto3.client('ec2')
rds = boto3.client('rds')
s3_client = boto3.client('s3')
lambda_client = boto3.client('lambda')
cw = boto3.client('cloudwatch')
bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')

BUCKET = os.environ['BUCKET_NAME']
MODEL_ID = 'us.amazon.nova-lite-v1:0'


def handler(event, context):
    """Weekly scheduled scan — collect, analyze, then trigger notify."""
    scan_id = datetime.utcnow().strftime('%Y%m%d-%H%M%S')
    findings = collect_findings()

    s3.put_object(
        Bucket=BUCKET,
        Key=f'scans/{scan_id}/raw.json',
        Body=json.dumps(findings, default=str).encode('utf-8')
    )

    # Chain to analyze function
    analyze_fn = os.environ.get('ANALYZE_FUNCTION')
    if analyze_fn:
        boto3.client('lambda').invoke(
            FunctionName=analyze_fn,
            InvocationType='Event',
            Payload=json.dumps({'scanId': scan_id})
        )

    return {'statusCode': 200, 'scanId': scan_id}


def on_demand_handler(event, context):
    """On-demand scan via API Gateway — collect + analyze inline, return results."""
    try:
        findings = collect_findings()
        report = analyze_findings(findings)
        return response(200, {'status': 'COMPLETE', 'results': report})
    except Exception as e:
        print(f'Error: {e}')
        return response(500, {'error': str(e)})


def collect_findings():
    findings = {
        'timestamp': datetime.utcnow().isoformat(),
        'cost_summary': get_cost_summary(),
        'unattached_ebs': get_unattached_ebs(),
        'idle_ec2': get_idle_ec2(),
        'idle_rds': get_idle_rds(),
        's3_no_lifecycle': get_s3_no_lifecycle(),
        'oversized_lambdas': get_oversized_lambdas()
    }
    return findings


def get_cost_summary():
    end = datetime.utcnow().date()
    start = end - timedelta(days=30)
    try:
        result = ce.get_cost_and_usage(
            TimePeriod={'Start': str(start), 'End': str(end)},
            Granularity='MONTHLY',
            Metrics=['UnblendedCost'],
            GroupBy=[{'Type': 'DIMENSION', 'Key': 'SERVICE'}]
        )
        services = []
        for period in result.get('ResultsByTime', []):
            for group in period.get('Groups', []):
                amount = float(group['Metrics']['UnblendedCost']['Amount'])
                if amount > 0.01:
                    services.append({
                        'service': group['Keys'][0],
                        'cost': round(amount, 2)
                    })
        services.sort(key=lambda x: x['cost'], reverse=True)
        return services
    except Exception as e:
        return [{'error': str(e)}]


def get_unattached_ebs():
    try:
        volumes = ec2.describe_volumes(
            Filters=[{'Name': 'status', 'Values': ['available']}]
        )
        results = []
        for vol in volumes.get('Volumes', []):
            results.append({
                'volume_id': vol['VolumeId'],
                'size_gb': vol['Size'],
                'type': vol['VolumeType'],
                'created': vol['CreateTime'].isoformat()
            })
        return results
    except Exception as e:
        return [{'error': str(e)}]


def get_idle_ec2():
    try:
        instances = ec2.describe_instances(
            Filters=[{'Name': 'instance-state-name', 'Values': ['running']}]
        )
        results = []
        end = datetime.utcnow()
        start = end - timedelta(days=7)

        for res in instances.get('Reservations', []):
            for inst in res.get('Instances', []):
                inst_id = inst['InstanceId']
                inst_type = inst['InstanceType']
                try:
                    cpu = cw.get_metric_statistics(
                        Namespace='AWS/EC2',
                        MetricName='CPUUtilization',
                        Dimensions=[{'Name': 'InstanceId', 'Value': inst_id}],
                        StartTime=start, EndTime=end,
                        Period=86400, Statistics=['Average']
                    )
                    avg_cpu = 0
                    if cpu['Datapoints']:
                        avg_cpu = round(sum(d['Average'] for d in cpu['Datapoints']) / len(cpu['Datapoints']), 2)
                    if avg_cpu < 5:
                        results.append({
                            'instance_id': inst_id,
                            'type': inst_type,
                            'avg_cpu_7d': avg_cpu
                        })
                except Exception:
                    pass
        return results
    except Exception as e:
        return [{'error': str(e)}]


def get_idle_rds():
    try:
        dbs = rds.describe_db_instances()
        results = []
        end = datetime.utcnow()
        start = end - timedelta(days=7)

        for db in dbs.get('DBInstances', []):
            db_id = db['DBInstanceIdentifier']
            db_class = db['DBInstanceClass']
            try:
                conns = cw.get_metric_statistics(
                    Namespace='AWS/RDS',
                    MetricName='DatabaseConnections',
                    Dimensions=[{'Name': 'DBInstanceIdentifier', 'Value': db_id}],
                    StartTime=start, EndTime=end,
                    Period=86400, Statistics=['Average']
                )
                avg_conns = 0
                if conns['Datapoints']:
                    avg_conns = round(sum(d['Average'] for d in conns['Datapoints']) / len(conns['Datapoints']), 2)
                if avg_conns < 1:
                    results.append({
                        'db_id': db_id,
                        'class': db_class,
                        'avg_connections_7d': avg_conns,
                        'multi_az': db.get('MultiAZ', False)
                    })
            except Exception:
                pass
        return results
    except Exception as e:
        return [{'error': str(e)}]


def get_s3_no_lifecycle():
    try:
        buckets = s3_client.list_buckets()
        results = []
        for bucket in buckets.get('Buckets', []):
            name = bucket['Name']
            try:
                s3_client.get_bucket_lifecycle_configuration(Bucket=name)
            except s3_client.exceptions.ClientError as e:
                if 'NoSuchLifecycleConfiguration' in str(e):
                    results.append({'bucket': name})
        return results
    except Exception as e:
        return [{'error': str(e)}]


def get_oversized_lambdas():
    try:
        functions = lambda_client.list_functions()
        results = []
        for fn in functions.get('Functions', []):
            mem = fn.get('MemorySize', 128)
            if mem >= 512:
                results.append({
                    'function_name': fn['FunctionName'],
                    'memory_mb': mem,
                    'runtime': fn.get('Runtime', 'unknown'),
                    'timeout': fn.get('Timeout', 0)
                })
        return results
    except Exception as e:
        return [{'error': str(e)}]


def analyze_findings(findings):
    prompt = """You are an AWS Cost Optimization expert. Analyze these AWS account findings and generate a cost optimization report.

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

    result = bedrock.invoke_model(
        modelId=MODEL_ID,
        contentType='application/json',
        accept='application/json',
        body=json.dumps({
            'schemaVersion': 'messages-v1',
            'system': [{'text': prompt}],
            'messages': [{'role': 'user', 'content': [{'text': f'Analyze these findings:\n\n{json.dumps(findings, default=str)}'}]}],
            'inferenceConfig': {'maxTokens': 3000, 'temperature': 0.2}
        })
    )

    body = json.loads(result['body'].read())
    ai_text = body['output']['message']['content'][0]['text']

    try:
        return json.loads(ai_text)
    except json.JSONDecodeError:
        start = ai_text.find('{')
        end = ai_text.rfind('}') + 1
        if start >= 0 and end > start:
            return json.loads(ai_text[start:end])
        return {'summary': 'Analysis complete but parsing failed.', 'findings': []}


def response(code, body):
    return {
        'statusCode': code,
        'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
        'body': json.dumps(body, default=str)
    }
