# Project 1: Cloud Architecture Advisor Chatbot

**AI-Powered AWS Architecture Recommendations**  
**Status**: ✅ LIVE - OPERATIONAL  
**Model**: Amazon Bedrock Nova Lite  
**Deployment Date**: March 11, 2026

**Live URL**: http://ai-2026-project-lonestar.s3-website-us-east-1.amazonaws.com/projects/01-ai-chatbot/index.html

---

## 🎯 Project Overview

An AI chatbot that provides AWS architecture recommendations based on user requirements. Users describe their application needs, and the chatbot responds with detailed architecture advice including recommended services, reasoning, and tradeoffs.

---

## 🏗️ Architecture

```
User Browser
    ↓
Static Website (S3)
    ↓
API Gateway (REST)
    ↓
Lambda Function (Python)
    ↓
Amazon Bedrock (Nova Lite)
```

**AWS Services Used:**
- **Amazon S3**: Static website hosting
- **API Gateway**: REST API endpoint
- **AWS Lambda**: Backend processing
- **Amazon Bedrock**: AI inference (Nova Lite model)
- **IAM**: Role and permissions management

---

## 📁 Project Structure

```
01-ai-chatbot/
├── frontend/
│   ├── index.html          # Chat interface
│   ├── styles.css          # Styling
│   └── app.js              # Frontend logic
├── backend/
│   ├── lambda_function.py  # Lambda handler
│   └── requirements.txt    # Python dependencies
├── scripts/
│   ├── deploy-lambda.sh    # Deploy Lambda function
│   ├── deploy-api-gateway.sh  # Deploy API Gateway
│   └── test-lambda.sh      # Test Lambda function
├── docs/
│   └── DEPLOYMENT.md       # Deployment instructions
└── README.md               # This file
```

---

## 🚀 Deployment Steps

### ✅ DEPLOYED - Current Live Configuration

**Backend Infrastructure:**
- Lambda Function: `CloudArchitectureAdvisor`
- API Gateway: `CloudArchitectureAdvisorAPI` (ID: ri802yjmt0)
- API Endpoint: https://ri802yjmt0.execute-api.us-east-1.amazonaws.com/prod/chat
- IAM Role: `CloudArchitectureAdvisorRole`
- Region: us-east-1

**Frontend:**
- S3 Location: s3://ai-2026-project-lonestar/projects/01-ai-chatbot/
- Live URL: http://ai-2026-project-lonestar.s3-website-us-east-1.amazonaws.com/projects/01-ai-chatbot/index.html

### Deployment Instructions (For Future Updates)

### Prerequisites
- AWS CLI configured with appropriate credentials
- Access to Amazon Bedrock (Nova Lite model enabled)
- Bash shell environment

### Step 1: Deploy Lambda Function
```bash
cd scripts
chmod +x deploy-lambda.sh
./deploy-lambda.sh
```

This creates:
- IAM role with Bedrock permissions
- Lambda function with Python 3.12 runtime
- CloudWatch Logs for monitoring

### Step 2: Deploy API Gateway
```bash
chmod +x deploy-api-gateway.sh
./deploy-api-gateway.sh
```

This creates:
- REST API with /chat endpoint
- CORS configuration
- Lambda integration
- Production stage deployment

### Step 3: Update Frontend
Copy the API endpoint from deployment output and update `frontend/app.js`:
```javascript
const API_ENDPOINT = 'https://YOUR_API_ID.execute-api.us-east-1.amazonaws.com/prod/chat';
```

### Step 4: Test Locally
Open `frontend/index.html` in a browser to test the chat interface.

### Step 5: Deploy to S3
```bash
aws s3 sync frontend/ s3://ai-2026-project-lonestar/projects/01-ai-chatbot/ --exclude "*.md"
```

---

## 🧪 Testing

### Test Lambda Function Directly
```bash
chmod +x test-lambda.sh
./test-lambda.sh
```

### Test API Endpoint
```bash
curl -X POST https://YOUR_API_ID.execute-api.us-east-1.amazonaws.com/prod/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "I need a scalable web application"}'
```

### Test Frontend Locally
1. Open `frontend/index.html` in browser
2. Enter a test message
3. Verify response from Bedrock

---

## 💡 Features

**Live Features:**
- ✅ Real-time chat interface
- ✅ AWS architecture recommendations powered by Nova Lite
- ✅ Service-specific reasoning
- ✅ Tradeoff analysis
- ✅ Clean, professional UI with Texas flag theme
- ✅ Mobile responsive design
- ✅ Markdown formatting (headings, bold, bullets)
- ✅ Loading animations
- ✅ Error handling

**Future Enhancements (Project 2):**
- 🔄 RAG with AWS documentation
- 🔄 Bedrock Knowledge Base integration
- 🔄 Architecture diagram generation
- 🔄 Cost estimation
- 🔄 Multi-turn conversations

---

## 🔧 Configuration

**Lambda Settings:**
- Runtime: Python 3.12
- Memory: 256 MB
- Timeout: 30 seconds
- Handler: lambda_function.lambda_handler

**Bedrock Settings:**
- Model: us.amazon.nova-lite-v1:0
- Max Tokens: 1000
- Temperature: 0.7
- Top P: 0.9

---

## 📊 Cost Estimate

**Actual Monthly Costs (March 2026):**
- Lambda: ~$0.20 (based on usage)
- API Gateway: ~$3.50
- Bedrock (Nova Lite): ~$0.50
- S3: ~$0.10
- **Total: ~$4.30/month**

**Note**: Costs may vary based on actual usage patterns.

---

## 🎓 Learning Outcomes

This project demonstrates:
- ✅ Full-stack AWS development
- ✅ Serverless architecture patterns
- ✅ AI/ML integration with Bedrock
- ✅ RESTful API design
- ✅ Frontend-backend integration
- ✅ Infrastructure as Code practices
- ✅ AWS security best practices

---

## 📝 Notes

- Nova Lite is optimized for speed and cost-efficiency
- CORS is enabled for cross-origin requests
- All responses include proper error handling
- Lambda logs are available in CloudWatch

---

*Part of AI Project: Lone Star portfolio*
