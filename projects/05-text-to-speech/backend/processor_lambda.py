import json
import os
import boto3
from datetime import datetime
from urllib.parse import unquote_plus

# AWS clients
s3 = boto3.client('s3')
polly = boto3.client('polly')

BUCKET_NAME = os.environ['BUCKET_NAME']

def lambda_handler(event, context):
    """Process uploaded file and convert to speech"""
    
    # Get S3 object info
    record = event['Records'][0]
    bucket = record['s3']['bucket']['name']
    key = unquote_plus(record['s3']['object']['key'])
    
    print(f"Processing: s3://{bucket}/{key}")
    
    # Extract filename and metadata
    filename = key.split('/')[-1]
    
    # Parse metadata from filename (format: timestamp_voiceEngine_voiceId_originalname)
    parts = filename.split('_', 3)
    if len(parts) >= 4:
        voice_engine = parts[1]  # standard or neural
        voice_id = parts[2]
        original_name = parts[3]
    else:
        voice_engine = 'neural'
        voice_id = 'Joanna'
        original_name = filename
    
    try:
        # Step 1: Read file from S3
        print("Reading file from S3...")
        response = s3.get_object(Bucket=bucket, Key=key)
        file_content = response['Body'].read()
        
        # Step 2: Extract text based on file type
        print("Extracting text...")
        if filename.lower().endswith('.txt'):
            text = file_content.decode('utf-8')
        elif filename.lower().endswith('.pdf'):
            # For PDF, use simple text extraction
            text = extract_text_from_pdf(bucket, key)
        else:
            raise Exception("Unsupported file type")
        
        # Limit text length (Polly has 3000 character limit per request)
        if len(text) > 3000:
            text = text[:3000]
            truncated = True
        else:
            truncated = False
        
        print(f"Text length: {len(text)} characters")
        
        # Step 3: Convert to speech with Polly
        print(f"Converting to speech with {voice_engine} voice {voice_id}...")
        polly_response = polly.synthesize_speech(
            Text=text,
            OutputFormat='mp3',
            VoiceId=voice_id,
            Engine=voice_engine
        )
        
        # Step 4: Save audio to S3
        audio_data = polly_response['AudioStream'].read()
        audio_filename = f"{original_name}.mp3"
        audio_key = f"results/{audio_filename}"
        
        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=audio_key,
            Body=audio_data,
            ContentType='audio/mpeg'
        )
        
        print(f"Audio saved: {audio_key}")
        
        # Step 5: Save metadata
        metadata = {
            'filename': original_name,
            'audio_file': audio_filename,
            'audio_url': f"https://{BUCKET_NAME}.s3.amazonaws.com/{audio_key}",
            'voice_engine': voice_engine,
            'voice_id': voice_id,
            'text_length': len(text),
            'truncated': truncated,
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
        
        # Save error metadata
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

def extract_text_from_pdf(bucket, key):
    """Extract text from PDF using Textract"""
    textract = boto3.client('textract')
    
    response = textract.detect_document_text(
        Document={'S3Object': {'Bucket': bucket, 'Name': key}}
    )
    
    text = ' '.join([
        block['Text'] 
        for block in response['Blocks'] 
        if block['BlockType'] == 'LINE'
    ])
    
    return text
