import json
import os
import boto3

s3 = boto3.client('s3')
ses = boto3.client('ses', region_name='us-east-1')

BUCKET = os.environ['BUCKET_NAME']
EMAIL = os.environ['NOTIFICATION_EMAIL']

SEVERITY_COLORS = {
    'CRITICAL': '#991b1b',
    'HIGH': '#9a3412',
    'MEDIUM': '#854d0e',
    'LOW': '#1e3a5f',
    'INFO': '#14532d'
}


def handler(event, context):
    scan_id = event['scanId']

    try:
        obj = s3.get_object(Bucket=BUCKET, Key=f'scans/{scan_id}/report.json')
        report = json.loads(obj['Body'].read().decode('utf-8'))

        html = build_email_html(report, scan_id)

        ses.send_email(
            Source=EMAIL,
            Destination={'ToAddresses': [EMAIL]},
            Message={
                'Subject': {'Data': f'AWS Cost Optimization Report — {scan_id}'},
                'Body': {'Html': {'Data': html}}
            }
        )

        print(f'Email sent for scan {scan_id}')

    except Exception as e:
        print(f'Error sending notification for {scan_id}: {e}')
        raise


def build_email_html(report, scan_id):
    summary = report.get('summary', 'No summary available.')
    total = report.get('total_estimated_savings', 0)
    findings = report.get('findings', [])

    findings_html = ''
    for f in findings:
        color = SEVERITY_COLORS.get(f.get('severity', 'INFO'), '#333')
        savings = f.get('estimated_monthly_savings', 0)
        findings_html += f'''
        <div style="background:#f8f9fa;border-left:4px solid {color};padding:16px;margin-bottom:12px;border-radius:4px;">
            <div style="margin-bottom:6px;">
                <span style="background:{color};color:white;padding:2px 8px;border-radius:3px;font-size:12px;font-weight:bold;">{f.get('severity','')}</span>
                <span style="color:#666;font-size:13px;margin-left:8px;">{f.get('category','')}</span>
                {f'<span style="float:right;color:#059669;font-weight:bold;">~${savings:.2f}/mo</span>' if savings > 0 else ''}
            </div>
            <div style="font-weight:600;font-size:15px;margin-bottom:4px;">{f.get('title','')}</div>
            <div style="color:#555;font-size:14px;margin-bottom:6px;">{f.get('description','')}</div>
            <div style="color:#0369a1;font-size:13px;border-top:1px solid #e0e0e0;padding-top:6px;">
                <strong>Fix:</strong> {f.get('remediation','')}
            </div>
        </div>'''

    return f'''<!DOCTYPE html>
<html>
<body style="font-family:Arial,sans-serif;max-width:700px;margin:0 auto;padding:20px;background:#ffffff;">
    <div style="background:linear-gradient(135deg,#071029,#052a4d);color:white;padding:24px;border-radius:8px 8px 0 0;">
        <h1 style="margin:0;font-size:22px;">AWS Cost Optimization Report</h1>
        <p style="margin:6px 0 0;opacity:0.8;font-size:14px;">Scan ID: {scan_id}</p>
    </div>
    <div style="background:#ecfdf5;border:1px solid #059669;padding:16px;margin:16px 0;border-radius:6px;">
        <div style="font-size:14px;color:#065f46;">{summary}</div>
        <div style="font-size:24px;font-weight:bold;color:#059669;margin-top:8px;">
            Estimated Savings: ${total:.2f}/month
        </div>
    </div>
    <h2 style="font-size:18px;color:#1e293b;margin-bottom:12px;">Findings ({len(findings)})</h2>
    {findings_html}
    <div style="text-align:center;color:#94a3b8;font-size:12px;margin-top:24px;padding-top:16px;border-top:1px solid #e2e8f0;">
        AI-Powered Cost Optimization Advisor — Project 06 | Powered by Amazon Bedrock
    </div>
</body>
</html>'''
