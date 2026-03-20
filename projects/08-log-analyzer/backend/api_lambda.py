import json
import os
import boto3
import base64
from datetime import datetime

s3 = boto3.client('s3')

BUCKET_NAME = os.environ['BUCKET_NAME']
ALLOWED_EXTENSIONS = {'.log', '.txt', '.csv', '.json'}

def lambda_handler(event, context):
    """Handle API requests"""
    
    path = event.get('rawPath', '/')
    method = event.get('requestContext', {}).get('http', {}).get('method', 'GET')
    
    print(f"{method} {path}")
    
    # Handle double slashes from Function URL
    if path.startswith('//'):
        path = path[1:]
    
    if method == 'POST' and path == '/upload':
        return handle_upload(event)
    elif method == 'GET' and path == '/result':
        return get_result(event)
    else:
        return {
            'statusCode': 200,
            'body': json.dumps({'status': 'API ready', 'path': path, 'method': method})
        }


def handle_upload(event):
    """Handle log file upload"""
    
    params = event.get('queryStringParameters', {}) or {}
    filename = params.get('filename')
    
    if not filename:
        return {'statusCode': 400, 'body': json.dumps({'error': 'filename parameter required'})}
    
    # Validate file extension
    ext = '.' + filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    if ext not in ALLOWED_EXTENSIONS:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': f'Unsupported file type. Allowed: {", ".join(sorted(ALLOWED_EXTENSIONS))}'})
        }
    
    # Get file data
    body = event.get('body', '')
    is_base64 = event.get('isBase64Encoded', False)
    
    if is_base64 or body:
        try:
            file_data = base64.b64decode(body)
        except:
            file_data = body.encode('utf-8') if isinstance(body, str) else body
    else:
        return {'statusCode': 400, 'body': json.dumps({'error': 'No file data received'})}
    
    # Upload to S3
    timestamp = int(datetime.utcnow().timestamp() * 1000)
    unique_filename = f"{timestamp}_{filename}"
    key = f"uploads/{unique_filename}"
    
    content_type = 'text/plain'
    if ext == '.json':
        content_type = 'application/json'
    elif ext == '.csv':
        content_type = 'text/csv'
    
    s3.put_object(
        Bucket=BUCKET_NAME,
        Key=key,
        Body=file_data,
        ContentType=content_type
    )
    
    print(f"Uploaded: {key} ({len(file_data)} bytes)")
    
    return {
        'statusCode': 200,
        'body': json.dumps({'filename': unique_filename, 'message': 'Upload successful'})
    }


def get_result(event):
    """Get analysis result"""
    
    params = event.get('queryStringParameters', {}) or {}
    filename = params.get('filename')
    
    if not filename:
        return {'statusCode': 400, 'body': json.dumps({'error': 'filename parameter required'})}
    
    result_key = f"results/{filename}.json"
    error_key = f"results/{filename}.error.json"
    
    try:
        response = s3.get_object(Bucket=BUCKET_NAME, Key=result_key)
        result = json.loads(response['Body'].read())
        return {'statusCode': 200, 'body': json.dumps(result)}
    except s3.exceptions.NoSuchKey:
        try:
            response = s3.get_object(Bucket=BUCKET_NAME, Key=error_key)
            error = json.loads(response['Body'].read())
            return {'statusCode': 500, 'body': json.dumps(error)}
        except s3.exceptions.NoSuchKey:
            return {'statusCode': 202, 'body': json.dumps({'status': 'processing'})}
    except Exception as e:
        return {'statusCode': 500, 'body': json.dumps({'error': str(e)})}
