#!/bin/bash

# API Gateway deployment script
set -e

echo "=========================================="
echo "API Gateway Deployment"
echo "=========================================="
echo ""

# Configuration
FUNCTION_NAME="CloudArchitectureAdvisor"
API_NAME="CloudArchitectureAdvisorAPI"
REGION="us-east-1"

# Check if API exists
API_ID=$(aws apigateway get-rest-apis --region $REGION --query "items[?name=='$API_NAME'].id" --output text)

if [ -z "$API_ID" ]; then
    echo "Creating new API Gateway..."
    API_ID=$(aws apigateway create-rest-api \
        --name $API_NAME \
        --description "API for Cloud Architecture Advisor Chatbot" \
        --region $REGION \
        --query 'id' \
        --output text)
    echo "✅ API Gateway created: $API_ID"
else
    echo "✅ API Gateway already exists: $API_ID"
fi

# Get root resource ID
ROOT_ID=$(aws apigateway get-resources \
    --rest-api-id $API_ID \
    --region $REGION \
    --query 'items[?path==`/`].id' \
    --output text)

# Create /chat resource if it doesn't exist
RESOURCE_ID=$(aws apigateway get-resources \
    --rest-api-id $API_ID \
    --region $REGION \
    --query "items[?path=='/chat'].id" \
    --output text)

if [ -z "$RESOURCE_ID" ]; then
    RESOURCE_ID=$(aws apigateway create-resource \
        --rest-api-id $API_ID \
        --parent-id $ROOT_ID \
        --path-part chat \
        --region $REGION \
        --query 'id' \
        --output text)
    echo "✅ /chat resource created"
fi

# Create POST method
aws apigateway put-method \
    --rest-api-id $API_ID \
    --resource-id $RESOURCE_ID \
    --http-method POST \
    --authorization-type NONE \
    --region $REGION 2>/dev/null || echo "POST method already exists"

# Set up Lambda integration
LAMBDA_ARN="arn:aws:lambda:$REGION:$(aws sts get-caller-identity --query Account --output text):function:$FUNCTION_NAME"

aws apigateway put-integration \
    --rest-api-id $API_ID \
    --resource-id $RESOURCE_ID \
    --http-method POST \
    --type AWS_PROXY \
    --integration-http-method POST \
    --uri "arn:aws:apigateway:$REGION:lambda:path/2015-03-31/functions/$LAMBDA_ARN/invocations" \
    --region $REGION 2>/dev/null || echo "Integration already exists"

# Add Lambda permission for API Gateway
aws lambda add-permission \
    --function-name $FUNCTION_NAME \
    --statement-id apigateway-invoke \
    --action lambda:InvokeFunction \
    --principal apigateway.amazonaws.com \
    --source-arn "arn:aws:execute-api:$REGION:$(aws sts get-caller-identity --query Account --output text):$API_ID/*/*" \
    --region $REGION 2>/dev/null || echo "Permission already exists"

# Enable CORS
aws apigateway put-method \
    --rest-api-id $API_ID \
    --resource-id $RESOURCE_ID \
    --http-method OPTIONS \
    --authorization-type NONE \
    --region $REGION 2>/dev/null || echo "OPTIONS method already exists"

aws apigateway put-method-response \
    --rest-api-id $API_ID \
    --resource-id $RESOURCE_ID \
    --http-method OPTIONS \
    --status-code 200 \
    --response-parameters '{"method.response.header.Access-Control-Allow-Headers":false,"method.response.header.Access-Control-Allow-Methods":false,"method.response.header.Access-Control-Allow-Origin":false}' \
    --region $REGION 2>/dev/null || echo "OPTIONS response already exists"

aws apigateway put-integration \
    --rest-api-id $API_ID \
    --resource-id $RESOURCE_ID \
    --http-method OPTIONS \
    --type MOCK \
    --request-templates '{"application/json":"{\"statusCode\": 200}"}' \
    --region $REGION 2>/dev/null || echo "OPTIONS integration already exists"

aws apigateway put-integration-response \
    --rest-api-id $API_ID \
    --resource-id $RESOURCE_ID \
    --http-method OPTIONS \
    --status-code 200 \
    --response-parameters '{"method.response.header.Access-Control-Allow-Headers":"'"'"'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'"'"'","method.response.header.Access-Control-Allow-Methods":"'"'"'POST,OPTIONS'"'"'","method.response.header.Access-Control-Allow-Origin":"'"'"'*'"'"'"}' \
    --region $REGION 2>/dev/null || echo "OPTIONS integration response already exists"

# Deploy API
aws apigateway create-deployment \
    --rest-api-id $API_ID \
    --stage-name prod \
    --region $REGION

echo "✅ API Gateway deployed"
echo ""

# Get API endpoint
API_ENDPOINT="https://$API_ID.execute-api.$REGION.amazonaws.com/prod/chat"

echo "=========================================="
echo "✅ API GATEWAY DEPLOYMENT COMPLETE!"
echo "=========================================="
echo ""
echo "API Endpoint: $API_ENDPOINT"
echo ""
echo "Next steps:"
echo "1. Update frontend/app.js with this endpoint"
echo "2. Test the API using curl or Postman"
echo "3. Upload frontend to S3"
