import json
import boto3
import os

# Initialize Bedrock Runtime client
bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')

# Model ID for Amazon Nova Lite
MODEL_ID = 'us.amazon.nova-lite-v1:0'

def lambda_handler(event, context):
    """
    Lambda function to handle chatbot requests using Amazon Bedrock Nova Lite
    """
    
    try:
        # Parse the incoming request
        body = json.loads(event.get('body', '{}'))
        user_message = body.get('message', '')
        
        if not user_message:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'POST, OPTIONS'
                },
                'body': json.dumps({
                    'error': 'No message provided'
                })
            }
        
        # Create the system prompt for architecture advice
        system_prompt = """You are an expert AWS Solutions Architect. Your role is to provide clear, 
practical AWS architecture recommendations based on user requirements.

For each request:
1. Provide a brief architecture summary
2. List recommended AWS services with specific reasons
3. Explain key tradeoffs and considerations
4. Keep responses concise but informative (300-500 words)
5. Use bullet points for clarity

Focus on real-world, production-ready architectures."""

        # Prepare the request for Bedrock
        request_body = {
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "text": f"{system_prompt}\n\nUser Request: {user_message}"
                        }
                    ]
                }
            ],
            "inferenceConfig": {
                "maxTokens": 1000,
                "temperature": 0.7,
                "topP": 0.9
            }
        }
        
        # Call Bedrock Nova Lite
        response = bedrock_runtime.converse(
            modelId=MODEL_ID,
            messages=request_body['messages'],
            inferenceConfig=request_body['inferenceConfig']
        )
        
        # Extract the response text
        response_text = response['output']['message']['content'][0]['text']
        
        # Return successful response
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST, OPTIONS'
            },
            'body': json.dumps({
                'response': response_text
            })
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST, OPTIONS'
            },
            'body': json.dumps({
                'error': 'Internal server error',
                'message': str(e)
            })
        }
