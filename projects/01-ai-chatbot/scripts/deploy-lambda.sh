#!/bin/bash

# Deployment script for Cloud Architecture Advisor Lambda Function
set -e

echo "=========================================="
echo "Cloud Architecture Advisor - Lambda Deployment"
echo "=========================================="
echo ""

# Configuration
FUNCTION_NAME="CloudArchitectureAdvisor"
REGION="us-east-1"
RUNTIME="python3.12"
HANDLER="lambda_function.lambda_handler"
ROLE_NAME="CloudArchitectureAdvisorRole"

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI is not installed. Please install it first."
    exit 1
fi

echo "Step 1: Creating IAM role for Lambda..."
echo "----------------------------------------"

# Create IAM role if it doesn't exist
if ! aws iam get-role --role-name $ROLE_NAME 2>/dev/null; then
    echo "Creating IAM role..."
    
    # Create trust policy
    cat > /tmp/trust-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

    aws iam create-role \
        --role-name $ROLE_NAME \
        --assume-role-policy-document file:///tmp/trust-policy.json
    
    # Attach basic Lambda execution policy
    aws iam attach-role-policy \
        --role-name $ROLE_NAME \
        --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
    
    # Create and attach Bedrock policy
    cat > /tmp/bedrock-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream"
      ],
      "Resource": "arn:aws:bedrock:us-east-1::foundation-model/us.amazon.nova-lite-v1:0"
    }
  ]
}
EOF

    aws iam put-role-policy \
        --role-name $ROLE_NAME \
        --policy-name BedrockAccess \
        --policy-document file:///tmp/bedrock-policy.json
    
    echo "✅ IAM role created. Waiting 10 seconds for propagation..."
    sleep 10
else
    echo "✅ IAM role already exists"
fi

# Get role ARN
ROLE_ARN=$(aws iam get-role --role-name $ROLE_NAME --query 'Role.Arn' --output text)
echo "Role ARN: $ROLE_ARN"
echo ""

echo "Step 2: Packaging Lambda function..."
echo "----------------------------------------"

# Create deployment package
cd ../backend
zip -r ../scripts/lambda-deployment.zip lambda_function.py
cd ../scripts

echo "✅ Lambda package created"
echo ""

echo "Step 3: Deploying Lambda function..."
echo "----------------------------------------"

# Check if function exists
if aws lambda get-function --function-name $FUNCTION_NAME --region $REGION 2>/dev/null; then
    echo "Updating existing function..."
    aws lambda update-function-code \
        --function-name $FUNCTION_NAME \
        --zip-file fileb://lambda-deployment.zip \
        --region $REGION
    
    echo "✅ Lambda function updated"
else
    echo "Creating new function..."
    aws lambda create-function \
        --function-name $FUNCTION_NAME \
        --runtime $RUNTIME \
        --role $ROLE_ARN \
        --handler $HANDLER \
        --zip-file fileb://lambda-deployment.zip \
        --timeout 30 \
        --memory-size 256 \
        --region $REGION
    
    echo "✅ Lambda function created"
fi

echo ""
echo "=========================================="
echo "✅ LAMBDA DEPLOYMENT COMPLETE!"
echo "=========================================="
echo ""
echo "Function Name: $FUNCTION_NAME"
echo "Region: $REGION"
echo ""
echo "Next: Run deploy-api-gateway.sh to create the API endpoint"
echo ""

# Clean up
rm -f lambda-deployment.zip
rm -f /tmp/trust-policy.json
rm -f /tmp/bedrock-policy.json
echo "✅ Temporary files cleaned up"
