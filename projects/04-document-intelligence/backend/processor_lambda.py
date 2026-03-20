import json
import os
import boto3
from datetime import datetime
from urllib.parse import unquote_plus

# AWS clients
s3 = boto3.client('s3')
textract = boto3.client('textract')
bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')

BUCKET_NAME = os.environ['BUCKET_NAME']

def lambda_handler(event, context):
    """Process document uploaded to S3"""
    
    # Get S3 object info from event
    record = event['Records'][0]
    bucket = record['s3']['bucket']['name']
    key = unquote_plus(record['s3']['object']['key'])
    
    print(f"Processing: s3://{bucket}/{key}")
    
    # Extract filename
    filename = key.split('/')[-1]
    
    try:
        # Step 1: Extract text with Textract
        print("Extracting text with Textract...")
        textract_response = textract.detect_document_text(
            Document={'S3Object': {'Bucket': bucket, 'Name': key}}
        )
        
        # Combine all text blocks
        extracted_text = ' '.join([
            block['Text'] 
            for block in textract_response['Blocks'] 
            if block['BlockType'] == 'LINE'
        ])
        
        print(f"Extracted {len(extracted_text)} characters")
        
        # Step 2: Analyze with Bedrock
        print("Analyzing with Bedrock...")
        analysis = analyze_with_bedrock(extracted_text)
        
        # Step 3: Prepare results
        result = {
            'filename': filename,
            'document_type': analysis.get('document_type', 'Unknown'),
            'summary': analysis.get('summary', ''),
            'key_fields': analysis.get('key_fields', {}),
            'extracted_text': extracted_text,
            'processed_at': datetime.utcnow().isoformat() + 'Z'
        }
        
        # Step 4: Save results to S3
        result_key = f"results/{filename}.json"
        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=result_key,
            Body=json.dumps(result),
            ContentType='application/json'
        )
        
        print(f"Results saved to {result_key}")
        
        return {'statusCode': 200, 'body': 'Success'}
        
    except Exception as e:
        print(f"Error: {str(e)}")
        
        # Check if it's an unsupported PDF error
        error_message = str(e)
        if 'UnsupportedDocumentException' in error_message:
            user_message = "This PDF cannot be processed. It may have password protection, digital signatures, or security features that Textract doesn't support. Try converting it to an image (PNG/JPEG) or use a simpler PDF."
        else:
            user_message = error_message
        
        # Save error result
        error_result = {
            'filename': filename,
            'error': user_message,
            'processed_at': datetime.utcnow().isoformat() + 'Z'
        }
        
        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=f"results/{filename}.error.json",
            Body=json.dumps(error_result),
            ContentType='application/json'
        )
        
        raise

def analyze_with_bedrock(text):
    """Analyze document text with Bedrock"""
    
    # Limit text to first 4000 characters for analysis
    text_sample = text[:4000]
    
    prompt = f"""Analyze this document and provide:
1. Document type (invoice, receipt, report, letter, certificate, form, or other)
2. Brief summary (2-3 sentences)
3. Key fields as JSON object (extract dates, amounts, names, addresses, etc.)

Document text:
{text_sample}

Respond ONLY with valid JSON in this exact format:
{{
  "document_type": "type here",
  "summary": "summary here",
  "key_fields": {{"field_name": "value"}}
}}"""
    
    response = bedrock.invoke_model(
        modelId='us.amazon.nova-lite-v1:0',
        body=json.dumps({
            'messages': [{'role': 'user', 'content': [{'text': prompt}]}],
            'inferenceConfig': {'temperature': 0.3, 'maxTokens': 1000}
        })
    )
    
    result = json.loads(response['body'].read())
    content = result['output']['message']['content'][0]['text']
    
    # Extract JSON from response
    start = content.find('{')
    end = content.rfind('}') + 1
    
    if start >= 0 and end > start:
        return json.loads(content[start:end])
    
    return {
        'document_type': 'Unknown',
        'summary': 'Unable to analyze document',
        'key_fields': {}
    }
