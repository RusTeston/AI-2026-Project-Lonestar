#!/bin/bash
set -e

BUCKET_NAME="ai-superhero-transformer-p6"
REGION="us-east-1"
ACCOUNT_ID="901779867920"

echo "=== Deploying Project 6: Superhero Transformer ==="

echo "Step 1: Creating S3 bucket..."
aws s3 mb s3://${BUCKET_NAME} --region ${REGION} 2>/dev/null || echo "Bucket already exists"

aws s3 website s3://${BUCKET_NAME} --index-document index.html

aws s3api put-bucket-cors --bucket ${BUCKET_NAME} --cors-configuration '{
  "CORSRules": [{
    "AllowedHeaders": ["*"],
    "AllowedMethods": ["GET", "PUT", "POST", "HEAD"],
    "AllowedOrigins": ["*"],
    "ExposeHeaders": ["ETag"],
    "MaxAgeSeconds": 3000
  }]
}'

aws s3api put-public-access-block --bucket ${BUCKET_NAME} \
  --public-access-block-configuration \
  BlockPublicAcls=false,IgnorePublicAcls=false,BlockPublicPolicy=false,RestrictPublicBuckets=false

aws s3api put-bucket-policy --bucket ${BUCKET_NAME} --policy "{
  \"Version\": \"2012-10-17\",
  \"Statement\": [{
    \"Sid\": \"PublicReadGetObject\",
    \"Effect\": \"Allow\",
    \"Principal\": \"*\",
    \"Action\": \"s3:GetObject\",
    \"Resource\": \"arn:aws:s3:::${BUCKET_NAME}/*\"
  }]
}"

echo "✓ S3 bucket configured"

echo "Step 2: Creating IAM roles..."

cat > /tmp/trust-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {"Service": "lambda.amazonaws.com"},
    "Action": "sts:AssumeRole"
  }]
}
EOF

aws iam create-role \
  --role-name SuperheroProcessorRole \
  --assume-role-policy-document file:///tmp/trust-policy.json \
  2>/dev/null || echo "Processor role exists"

aws iam attach-role-policy \
  --role-name SuperheroProcessorRole \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

aws iam attach-role-policy \
  --role-name SuperheroProcessorRole \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess

aws iam attach-role-policy \
  --role-name SuperheroProcessorRole \
  --policy-arn arn:aws:iam::aws:policy/AmazonBedrockFullAccess

aws iam create-role \
  --role-name SuperheroAPIRole \
  --assume-role-policy-document file:///tmp/trust-policy.json \
  2>/dev/null || echo "API role exists"

aws iam attach-role-policy \
  --role-name SuperheroAPIRole \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

aws iam attach-role-policy \
  --role-name SuperheroAPIRole \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess

echo "✓ IAM roles created (waiting 10s)"
sleep 10

echo "Step 3: Deploying Processor Lambda..."
cd backend
zip -q processor.zip processor_lambda.py

aws lambda create-function \
  --function-name SuperheroProcessor \
  --runtime python3.9 \
  --role arn:aws:iam::${ACCOUNT_ID}:role/SuperheroProcessorRole \
  --handler processor_lambda.lambda_handler \
  --zip-file fileb://processor.zip \
  --timeout 60 \
  --memory-size 1024 \
  --environment Variables="{BUCKET_NAME=${BUCKET_NAME}}" \
  --region ${REGION} \
  2>/dev/null || aws lambda update-function-code \
  --function-name SuperheroProcessor \
  --zip-file fileb://processor.zip \
  --region ${REGION}

echo "✓ Processor Lambda deployed"

echo "Step 4: Deploying API Lambda..."
zip -q api.zip api_lambda.py

aws lambda create-function \
  --function-name SuperheroAPI \
  --runtime python3.9 \
  --role arn:aws:iam::${ACCOUNT_ID}:role/SuperheroAPIRole \
  --handler api_lambda.lambda_handler \
  --zip-file fileb://api.zip \
  --timeout 30 \
  --memory-size 256 \
  --environment Variables="{BUCKET_NAME=${BUCKET_NAME}}" \
  --region ${REGION} \
  2>/dev/null || aws lambda update-function-code \
  --function-name SuperheroAPI \
  --zip-file fileb://api.zip \
  --region ${REGION}

echo "✓ API Lambda deployed"

echo "Step 5: Creating Function URL..."
API_URL=$(aws lambda create-function-url-config \
  --function-name SuperheroAPI \
  --auth-type NONE \
  --cors AllowOrigins='*',AllowMethods='GET,POST',AllowHeaders='*',MaxAge=300 \
  --region ${REGION} \
  --query 'FunctionUrl' \
  --output text 2>/dev/null || aws lambda get-function-url-config \
  --function-name SuperheroAPI \
  --region ${REGION} \
  --query 'FunctionUrl' \
  --output text)

aws lambda add-permission \
  --function-name SuperheroAPI \
  --statement-id FunctionURLAllowPublicAccess \
  --action lambda:InvokeFunctionUrl \
  --principal '*' \
  --function-url-auth-type NONE \
  --region ${REGION} \
  2>/dev/null || echo "Permission exists"

echo "✓ Function URL: ${API_URL}"

echo "Step 6: Configuring S3 event notification..."

aws lambda add-permission \
  --function-name SuperheroProcessor \
  --statement-id S3InvokeFunction \
  --action lambda:InvokeFunction \
  --principal s3.amazonaws.com \
  --source-arn arn:aws:s3:::${BUCKET_NAME} \
  --region ${REGION} \
  2>/dev/null || echo "S3 permission exists"

aws s3api put-bucket-notification-configuration \
  --bucket ${BUCKET_NAME} \
  --notification-configuration "{
    \"LambdaFunctionConfigurations\": [{
      \"LambdaFunctionArn\": \"arn:aws:lambda:${REGION}:${ACCOUNT_ID}:function:SuperheroProcessor\",
      \"Events\": [\"s3:ObjectCreated:*\"],
      \"Filter\": {
        \"Key\": {
          \"FilterRules\": [{\"Name\": \"prefix\", \"Value\": \"uploads/\"}]
        }
      }
    }]
  }"

echo "✓ S3 event notification configured"

cd ..

echo "Step 7: Updating frontend..."
sed -i.bak "s|API_URL_PLACEHOLDER|${API_URL}|g" frontend/app.js
rm -f frontend/app.js.bak

echo "Step 8: Deploying frontend..."
aws s3 cp frontend/ s3://ai-2026-project-lonestar/projects/06-superhero-transformer/ --recursive --exclude ".*"

echo ""
echo "=== Deployment Complete ==="
echo "API URL: ${API_URL}"
echo "Website: http://ai-2026-project-lonestar.s3-website-us-east-1.amazonaws.com/projects/06-superhero-transformer/index.html"
echo ""
