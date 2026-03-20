#!/bin/bash

# Deployment script for Language Translator Lambda Function
set -e

echo "=========================================="
echo "Language Translator - Lambda Deployment"
echo "=========================================="
echo ""

# Configuration
FUNCTION_NAME="LanguageTranslator"
REGION="us-east-1"
RUNTIME="python3.12"
HANDLER="lambda_function.lambda_handler"
ROLE_NAME="LanguageTranslatorRole"

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
    
    # Create and attach Translate policy
    cat > /tmp/translate-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "translate:TranslateText"
      ],
      "Resource": "*"
    }
  ]
}
EOF

    aws iam put-role-policy \
        --role-name $ROLE_NAME \
        --policy-name TranslateAccess \
        --policy-document file:///tmp/translate-policy.json
    
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
        --memory-size 128 \
        --region $REGION
    
    echo "✅ Lambda function created"
fi

echo ""
echo "Step 4: Creating Lambda Function URL..."
echo "----------------------------------------"

# Check if function URL exists
FUNCTION_URL=$(aws lambda get-function-url-config --function-name $FUNCTION_NAME --region $REGION --query 'FunctionUrl' --output text 2>/dev/null || echo "")

if [ -z "$FUNCTION_URL" ]; then
    echo "Creating Function URL..."
    FUNCTION_URL=$(aws lambda create-function-url-config \
        --function-name $FUNCTION_NAME \
        --auth-type NONE \
        --cors '{
            "AllowOrigins": ["*"],
            "AllowMethods": ["POST", "OPTIONS"],
            "AllowHeaders": ["Content-Type"],
            "MaxAge": 86400
        }' \
        --region $REGION \
        --query 'FunctionUrl' \
        --output text)
    
    # Add permission for public access
    aws lambda add-permission \
        --function-name $FUNCTION_NAME \
        --statement-id FunctionURLAllowPublicAccess \
        --action lambda:InvokeFunctionUrl \
        --principal "*" \
        --function-url-auth-type NONE \
        --region $REGION 2>/dev/null || echo "Permission already exists"
    
    echo "✅ Function URL created"
else
    echo "✅ Function URL already exists"
fi

echo ""
echo "=========================================="
echo "✅ LAMBDA DEPLOYMENT COMPLETE!"
echo "=========================================="
echo ""
echo "Function Name: $FUNCTION_NAME"
echo "Region: $REGION"
echo "Function URL: $FUNCTION_URL"
echo ""
echo "Next: Update frontend/app.js with this URL"
echo ""

# Clean up
rm -f lambda-deployment.zip
rm -f /tmp/trust-policy.json
rm -f /tmp/translate-policy.json
echo "✅ Temporary files cleaned up"
