import json
import os
import boto3
import base64
from datetime import datetime
from urllib.parse import unquote_plus

s3 = boto3.client('s3')
bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')

BUCKET_NAME = os.environ['BUCKET_NAME']

def lambda_handler(event, context):
    """Process uploaded photo and transform into superhero"""
    
    record = event['Records'][0]
    bucket = record['s3']['bucket']['name']
    key = unquote_plus(record['s3']['object']['key'])
    
    print(f"Processing: s3://{bucket}/{key}")
    
    filename = key.split('/')[-1]
    
    # Parse original filename (format: timestamp_originalname)
    parts = filename.split('_', 1)
    original_name = parts[1] if len(parts) >= 2 else filename
    
    try:
        # Step 1: Read image from S3
        print("Reading image from S3...")
        response = s3.get_object(Bucket=bucket, Key=key)
        image_bytes = response['Body'].read()
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        print(f"Image size: {len(image_bytes)} bytes")
        
        # Step 2: Transform with Bedrock Titan Image Generator
        print("Transforming with Bedrock Titan Image Generator...")
        
        body = json.dumps({
            "taskType": "IMAGE_VARIATION",
            "imageVariationParams": {
                "text": "Create a unique comic book superhero character inspired by this image. The superhero should have an original costume design with bold colors, a cape, and a unique emblem. Draw in professional comic book illustration style with clean lines, vibrant colors, and dramatic lighting. Full body character design on a simple background.",
                "images": [image_base64],
                "similarityStrength": 0.2
            },
            "imageGenerationConfig": {
                "numberOfImages": 1,
                "height": 1024,
                "width": 1024,
                "cfgScale": 8.0
            }
        })
        
        bedrock_response = bedrock.invoke_model(
            modelId='amazon.titan-image-generator-v2:0',
            body=body
        )
        
        result = json.loads(bedrock_response['body'].read())
        
        # Step 3: Save superhero image to S3
        print("Saving superhero image...")
        superhero_base64 = result['images'][0]
        superhero_bytes = base64.b64decode(superhero_base64)
        
        superhero_key = f"results/{original_name}.png"
        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=superhero_key,
            Body=superhero_bytes,
            ContentType='image/png'
        )
        
        print(f"Superhero image saved: {superhero_key}")
        
        # Step 4: Save metadata
        metadata = {
            'filename': original_name,
            'superhero_image': f"{original_name}.png",
            'superhero_url': f"https://{BUCKET_NAME}.s3.amazonaws.com/{superhero_key}",
            'original_url': f"https://{BUCKET_NAME}.s3.amazonaws.com/{key}",
            'processed_at': datetime.utcnow().isoformat() + 'Z',
            'status': 'success'
        }
        
        metadata_key = f"results/{original_name}.json"
        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=metadata_key,
            Body=json.dumps(metadata),
            ContentType='application/json'
        )
        
        print(f"Metadata saved: {metadata_key}")
        
        return {'statusCode': 200, 'body': 'Success'}
        
    except Exception as e:
        print(f"Error: {str(e)}")
        
        error_metadata = {
            'filename': original_name,
            'error': str(e),
            'processed_at': datetime.utcnow().isoformat() + 'Z',
            'status': 'error'
        }
        
        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=f"results/{original_name}.error.json",
            Body=json.dumps(error_metadata),
            ContentType='application/json'
        )
        
        raise
