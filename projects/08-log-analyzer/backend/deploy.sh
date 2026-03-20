#!/bin/bash
set -e

REGION="us-east-1"
ACCOUNT_ID="901779867920"
BUCKET_NAME="ai-log-analyzer-p8"
PROCESSOR_FUNCTION="ai-log-analyzer-processor"
API_FUNCTION="ai-log-analyzer-api"
ROLE_NAME="ai-log-analyzer-role"

echo "=== Project 8: AI Log Analyzer - Deployment ==="

# Step 1: Create S3 bucket
echo "Step 1: Creating S3 bucket..."
aws s3 mb s3://$BUCKET_NAME --region $REGION 2>/dev/null || echo "Bucket already exists"

# Step 2: Create IAM role
echo "Step 2: Creating IAM role..."
TRUST_POLICY='{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {"Service": "lambda.amazonaws.com"},
    "Action": "sts:AssumeRole"
  }]
}'

aws iam create-role \
  --role-name $ROLE_NAME \
  --assume-role-policy-document "$TRUST_POLICY" \
  2>/dev/null || echo "Role already exists"

# Attach policies
POLICY='{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:GetObject", "s3:PutObject"],
      "Resource": "arn:aws:s3:::'"$BUCKET_NAME"'/*"
    },
    {
      "Effect": "Allow",
      "Action": ["s3:ListBucket"],
      "Resource": "arn:aws:s3:::'"$BUCKET_NAME"'"
    },
    {
      "Effect": "Allow",
      "Action": ["bedrock:InvokeModel"],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": ["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"],
      "Resource": "arn:aws:logs:*:*:*"
    }
  ]
}'

aws iam put-role-policy \
  --role-name $ROLE_NAME \
  --policy-name "${ROLE_NAME}-policy" \
  --policy-document "$POLICY"

ROLE_ARN="arn:aws:iam::${ACCOUNT_ID}:role/${ROLE_NAME}"
echo "Waiting for role propagation..."
sleep 10

# Step 3: Deploy Processor Lambda
echo "Step 3: Deploying Processor Lambda..."
cd /tmp
cp /Users/rusteston/Desktop/AI-2026-Project-Lonestar/projects/08-log-analyzer/backend/processor_lambda.py lambda_function.py
zip -j processor.zip lambda_function.py
rm lambda_function.py

aws lambda create-function \
  --function-name $PROCESSOR_FUNCTION \
  --runtime python3.12 \
  --handler lambda_function.lambda_handler \
  --role $ROLE_ARN \
  --zip-file fileb://processor.zip \
  --timeout 60 \
  --memory-size 256 \
  --environment "Variables={BUCKET_NAME=$BUCKET_NAME}" \
  --region $REGION \
  2>/dev/null || \
aws lambda update-function-code \
  --function-name $PROCESSOR_FUNCTION \
  --zip-file fileb://processor.zip \
  --region $REGION

rm processor.zip

# Step 4: Deploy API Lambda
echo "Step 4: Deploying API Lambda..."
cp /Users/rusteston/Desktop/AI-2026-Project-Lonestar/projects/08-log-analyzer/backend/api_lambda.py lambda_function.py
zip -j api.zip lambda_function.py
rm lambda_function.py

aws lambda create-function \
  --function-name $API_FUNCTION \
  --runtime python3.12 \
  --handler lambda_function.lambda_handler \
  --role $ROLE_ARN \
  --zip-file fileb://api.zip \
  --timeout 30 \
  --memory-size 128 \
  --environment "Variables={BUCKET_NAME=$BUCKET_NAME}" \
  --region $REGION \
  2>/dev/null || \
aws lambda update-function-code \
  --function-name $API_FUNCTION \
  --zip-file fileb://api.zip \
  --region $REGION

rm api.zip

# Step 5: Create Function URL
echo "Step 5: Creating Function URL..."
FUNCTION_URL=$(aws lambda get-function-url-config \
  --function-name $API_FUNCTION \
  --region $REGION \
  --query 'FunctionUrl' --output text 2>/dev/null || \
aws lambda create-function-url-config \
  --function-name $API_FUNCTION \
  --auth-type NONE \
  --cors '{
    "AllowOrigins": ["*"],
    "AllowMethods": ["GET", "POST"],
    "AllowHeaders": ["*"]
  }' \
  --region $REGION \
  --query 'FunctionUrl' --output text)

# Ensure public access
aws lambda add-permission \
  --function-name $API_FUNCTION \
  --statement-id FunctionURLPublicAccess \
  --action lambda:InvokeFunctionUrl \
  --principal "*" \
  --function-url-auth-type NONE \
  --region $REGION \
  2>/dev/null || true

echo "Function URL: $FUNCTION_URL"

# Step 6: Add S3 event notification
echo "Step 6: Configuring S3 event notification..."

# Grant S3 permission to invoke processor
aws lambda add-permission \
  --function-name $PROCESSOR_FUNCTION \
  --statement-id S3InvokePermission \
  --action lambda:InvokeFunction \
  --principal s3.amazonaws.com \
  --source-arn "arn:aws:s3:::$BUCKET_NAME" \
  --region $REGION \
  2>/dev/null || true

PROCESSOR_ARN=$(aws lambda get-function \
  --function-name $PROCESSOR_FUNCTION \
  --region $REGION \
  --query 'Configuration.FunctionArn' --output text)

NOTIFICATION='{
  "LambdaFunctionConfigurations": [{
    "LambdaFunctionArn": "'"$PROCESSOR_ARN"'",
    "Events": ["s3:ObjectCreated:*"],
    "Filter": {
      "Key": {
        "FilterRules": [{"Name": "prefix", "Value": "uploads/"}]
      }
    }
  }]
}'

aws s3api put-bucket-notification-configuration \
  --bucket $BUCKET_NAME \
  --notification-configuration "$NOTIFICATION"

echo ""
echo "=== Deployment Complete ==="
echo "S3 Bucket: $BUCKET_NAME"
echo "Processor Lambda: $PROCESSOR_FUNCTION"
echo "API Lambda: $API_FUNCTION"
echo "Function URL: $FUNCTION_URL"
echo ""
echo "Next: Create frontend and deploy to s3://ai-2026-project-lonestar/projects/08-log-analyzer/"
