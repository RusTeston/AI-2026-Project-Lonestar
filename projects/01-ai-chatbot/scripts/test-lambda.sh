#!/bin/bash

# Test script for Lambda function
echo "=========================================="
echo "Testing Lambda Function"
echo "=========================================="
echo ""

FUNCTION_NAME="CloudArchitectureAdvisor"
REGION="us-east-1"

# Test payload
cat > /tmp/test-payload.json <<EOF
{
  "body": "{\"message\": \"I need to build a scalable e-commerce website with high availability\"}"
}
EOF

echo "Invoking Lambda function..."
echo ""

aws lambda invoke \
    --function-name $FUNCTION_NAME \
    --region $REGION \
    --payload file:///tmp/test-payload.json \
    /tmp/response.json

echo ""
echo "Response:"
cat /tmp/response.json | python3 -m json.tool

# Clean up
rm -f /tmp/test-payload.json /tmp/response.json
