# AI Project: Lone Star — Deployment Manifest

**Last Updated**: March 25, 2026

---

## 📦 Deployed Projects

### Project 1: AI Chatbot ✅ LIVE
- **Live URL**: https://ai.rus-teston.com/projects/01-ai-chatbot/index.html
- **Backend**: Lambda + API Gateway + Bedrock Nova Lite
- **API Endpoint**: https://ri802yjmt0.execute-api.us-east-1.amazonaws.com/prod/chat
- **Deployment**: Manual (bash scripts)

### Project 2: Agentic RAG 🚧 Not Deployed
- **Status**: Planning phase

### Project 3: Language Translator ✅ LIVE
- **Live URL**: https://ai.rus-teston.com/projects/03-language-translator/index.html
- **Backend**: Lambda + AWS Translate
- **Lambda Function URL**: https://3usd2qizpvp57tsk6b4qkifnym0lnkdi.lambda-url.us-east-1.on.aws/
- **Deployment**: Manual (bash scripts)

### Project 4: Document Intelligence ✅ LIVE
- **Live URL**: https://ai.rus-teston.com/projects/04-document-intelligence/index.html
- **Backend**: Lambda Function URL × 2 + Textract + Bedrock Nova Lite
- **Deployment**: Manual (bash scripts)

### Project 5: Text-to-Speech Reader ✅ LIVE
- **Live URL**: https://ai.rus-teston.com/projects/05-text-to-speech/index.html
- **Backend**: Lambda Function URL × 2 + Polly + Textract
- **Deployment**: Manual (bash scripts)

### Project 6: Cost Optimization Advisor ✅ LIVE
- **Live URL**: https://ai.rus-teston.com/projects/06-cost-optimizer/index.html
- **Backend**: EventBridge Scheduler + Lambda × 4 + Bedrock Nova Lite + SES + Cost Explorer
- **SAM Stack**: `project-06-cost-optimizer`
- **Deployment**: SAM/IaC

### Project 7: Architecture Reviewer ✅ LIVE
- **Live URL**: https://ai.rus-teston.com/projects/07-architecture-reviewer/index.html
- **Backend**: API Gateway + Lambda × 3 + SQS + S3 + DynamoDB + Bedrock Nova Lite
- **SAM Stack**: `project-07-architecture-reviewer`
- **Deployment**: SAM/IaC

### Project 8: AI Log Analyzer ✅ LIVE
- **Live URL**: https://ai.rus-teston.com/projects/08-log-analyzer/index.html
- **Backend**: Lambda Function URL × 2 + Bedrock Nova Lite
- **Deployment**: Manual (bash scripts)

### Project 9: Failover Orchestrator ✅ LIVE
- **Live URL**: https://ai.rus-teston.com/projects/09-failover-orchestrator/index.html
- **Backend**: EventBridge Scheduler + Step Functions + Lambda × 5 + Bedrock Nova Lite + DynamoDB + API Gateway
- **SAM Stack**: `project-09-failover-orchestrator`
- **Deployment**: SAM/IaC

---

## 🏗️ Infrastructure Inventory

### Website Hosting
- **S3 Bucket**: `ai-2026-project-lonestar` (static website hosting enabled)
- **CloudFront Distribution**: `E6LY7PZWUOBBP` (`d309r1vnuulj1s.cloudfront.net`)
- **Custom Domain**: `https://ai.rus-teston.com`
- **ACM Certificate**: `arn:aws:acm:us-east-1:901779867920:certificate/44d125cf-bff3-4651-bd17-7b553a05be4c`
- **DNS**: Route 53 alias record in `rus-teston.com` hosted zone (`Z00478791SCIWJ5ZZ3U3T`)
- **Security Headers**: Response headers policy `d409f843-33ea-453e-a8f7-2fb44e4804ef` (HSTS, CSP, X-Frame, XSS Protection, Content-Type-Options)
- **TLS**: 1.2+ minimum, SNI, PriceClass_100

### CI/CD Pipeline
- **GitHub Repo**: https://github.com/RusTeston/AI-2026-Project-Lonestar
- **GitHub Actions**: Auto-deploy on push to main (paths: `website/**`, `projects/*/frontend/**`)
- **OIDC Federation**: Secure AWS authentication (no stored credentials)
- **IAM Role**: `GitHubActions-Deploy`
  - S3: PutObject/GetObject/DeleteObject/ListBucket on `ai-2026-project-lonestar` and `rus-portfolio-prod`
  - Lambda: UpdateFunctionCode in us-east-1
  - CloudFront: CreateInvalidation on `E3IA5ZUL2HT0NT` and `E6LY7PZWUOBBP`
- **Pipeline Steps**: Checkout → OIDC Auth → Deploy landing page → Deploy error page → Deploy project frontends → Invalidate CloudFront cache

### AI Services
| Service | Projects |
|---------|----------|
| Bedrock Nova Lite (`us.amazon.nova-lite-v1:0`) | 1, 4, 6, 7, 8, 9 |
| AWS Translate | 3 |
| Amazon Polly | 5 |
| AWS Textract | 4, 5 |

---

## 🎨 Frontend Features
- **Project Summary Modals**: All 8 project pages have clickable project labels that open a summary modal overlay
- **Light theme** (Projects 1, 3, 4, 5, 8): White modal with blue headings
- **Dark theme** (Projects 6, 7, 9): Dark modal matching page accent colors
- **Error page**: Space-themed 404 page at `/error.html`

---

## 💰 Estimated Monthly Cost
| Project | Estimate |
|---------|----------|
| Project 1: AI Chatbot | ~$4/month |
| Project 3: Language Translator | ~$8/month |
| Projects 4, 5, 8: Event-driven | ~$5-12/month each |
| Projects 6, 7, 9: SAM projects | ~$1-2/month each |
| CloudFront (PriceClass_100) | ~$0-1/month |
| **Total** | ~$30-50/month |

---

*This manifest tracks all deployments and infrastructure for AI Project: Lone Star.*
