import json
import boto3
import os

# Initialize AWS Translate client
translate_client = boto3.client('translate', region_name='us-east-1')

def lambda_handler(event, context):
    """
    Lambda function to translate text using AWS Translate
    """
    
    try:
        # Parse the incoming request
        body = json.loads(event.get('body', '{}'))
        text = body.get('text', '')
        source_language = body.get('sourceLanguage', 'auto')
        target_language = body.get('targetLanguage', '')
        
        # Validate input
        if not text:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'No text provided'
                })
            }
        
        if not target_language:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'No target language provided'
                })
            }
        
        # Check text length (AWS Translate limit is 10,000 bytes)
        if len(text.encode('utf-8')) > 10000:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'Text too long. Maximum 10,000 bytes.'
                })
            }
        
        # Call AWS Translate
        if source_language == 'auto':
            # Auto-detect source language
            response = translate_client.translate_text(
                Text=text,
                SourceLanguageCode='auto',
                TargetLanguageCode=target_language
            )
        else:
            # Use specified source language
            response = translate_client.translate_text(
                Text=text,
                SourceLanguageCode=source_language,
                TargetLanguageCode=target_language
            )
        
        # Extract results
        translated_text = response['TranslatedText']
        detected_source_language = response.get('SourceLanguageCode', source_language)
        
        # Return successful response
        return {
            'statusCode': 200,
            'body': json.dumps({
                'translatedText': translated_text,
                'sourceLanguage': detected_source_language,
                'targetLanguage': target_language,
                'originalText': text
            })
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Translation failed',
                'message': str(e)
            })
        }

