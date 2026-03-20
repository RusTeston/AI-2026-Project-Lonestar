import json
import os
import boto3
from datetime import datetime

s3 = boto3.client('s3')

BUCKET_NAME = os.environ['BUCKET_NAME']

def lambda_handler(event, context):
    """Handle API requests"""
    
    path = event.get('rawPath', '/')
    method = event.get('requestContext', {}).get('http', {}).get('method', 'GET')
    
    print(f"{method} {path}")
    
    # Handle double slashes
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
    """Handle direct file upload"""
    import base64
    
    params = event.get('queryStringParameters', {}) or {}
    filename = params.get('filename')
    
    if not filename:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'filename parameter required'})
        }
    
    # Get file data from body - Lambda Function URLs base64 encode binary data
    body = event.get('body', '')
    is_base64 = event.get('isBase64Encoded', False)
    
    # Lambda Function URLs ALWAYS base64 encode binary uploads
    if is_base64 or body:
        try:
            file_data = base64.b64decode(body)
        except:
            file_data = body.encode('utf-8') if isinstance(body, str) else body
    else:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'No file data received'})
        }
    
    # Generate unique filename
    timestamp = int(datetime.utcnow().timestamp() * 1000)
    unique_filename = f"{timestamp}_{filename}"
    key = f"uploads/{unique_filename}"
    
    # Upload to S3 with proper content type
    content_type = 'application/pdf' if filename.lower().endswith('.pdf') else 'image/png' if filename.lower().endswith('.png') else 'image/jpeg'
    
    s3.put_object(
        Bucket=BUCKET_NAME,
        Key=key,
        Body=file_data,
        ContentType=content_type
    )
    
    print(f"File uploaded: {key} ({len(file_data)} bytes)")
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'filename': unique_filename,
            'message': 'Upload successful'
        })
    }

def get_result(event):
    """Get processing result for a file"""
    
    params = event.get('queryStringParameters', {}) or {}
    filename = params.get('filename')
    
    if not filename:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'filename parameter required'})
        }
    
    # Check for result
    result_key = f"results/{filename}.json"
    error_key = f"results/{filename}.error.json"
    
    try:
        # Try to get successful result
        response = s3.get_object(Bucket=BUCKET_NAME, Key=result_key)
        result = json.loads(response['Body'].read())
        
        return {
            'statusCode': 200,
            'body': json.dumps(result)
        }
    except s3.exceptions.NoSuchKey:
        # Check for error result
        try:
            response = s3.get_object(Bucket=BUCKET_NAME, Key=error_key)
            error = json.loads(response['Body'].read())
            
            return {
                'statusCode': 500,
                'body': json.dumps(error)
            }
        except s3.exceptions.NoSuchKey:
            # Still processing
            return {
                'statusCode': 202,
                'body': json.dumps({'status': 'processing'})
            }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
