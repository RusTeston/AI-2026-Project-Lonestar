#!/bin/bash

# S3 Bucket Setup for Project Lonestar
BUCKET_NAME="ai-2026-project-lonestar"
REGION="us-east-1"

echo "Checking availability for bucket: $BUCKET_NAME"
echo "================================================"

# Check if bucket exists
if aws s3api head-bucket --bucket "$BUCKET_NAME" 2>/dev/null; then
    echo "✅ Bucket already exists and you own it"
    echo "Proceeding with configuration..."
else
    # Try to create the bucket
    echo "Creating bucket: $BUCKET_NAME"
    if [ "$REGION" = "us-east-1" ]; then
        aws s3api create-bucket --bucket "$BUCKET_NAME" --region "$REGION"
    else
        aws s3api create-bucket --bucket "$BUCKET_NAME" --region "$REGION" \
            --create-bucket-configuration LocationConstraint="$REGION"
    fi
    
    if [ $? -eq 0 ]; then
        echo "✅ Bucket created successfully"
    else
        echo "❌ Failed to create bucket (may be taken by another account)"
        exit 1
    fi
fi

echo ""
echo "Configuring static website hosting..."
aws s3 website "s3://$BUCKET_NAME/" --index-document index.html --error-document error.html

echo ""
echo "Setting bucket policy for public read access..."
cat > /tmp/bucket-policy.json <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::$BUCKET_NAME/*"
        }
    ]
}
EOF

aws s3api put-bucket-policy --bucket "$BUCKET_NAME" --policy file:///tmp/bucket-policy.json

echo ""
echo "Disabling block public access..."
aws s3api put-public-access-block \
    --bucket "$BUCKET_NAME" \
    --public-access-block-configuration \
    "BlockPublicAcls=false,IgnorePublicAcls=false,BlockPublicPolicy=false,RestrictPublicBuckets=false"

echo ""
echo "✅ Setup complete!"
echo ""
echo "Bucket Details:"
echo "  Name: $BUCKET_NAME"
echo "  Region: $REGION"
echo "  Website Endpoint: http://$BUCKET_NAME.s3-website-$REGION.amazonaws.com"
echo ""
echo "Next steps:"
echo "  1. Upload your website files to the bucket"
echo "  2. Set up CloudFront distribution (optional)"
echo "  3. Configure custom domain with Route 53"

rm /tmp/bucket-policy.json
