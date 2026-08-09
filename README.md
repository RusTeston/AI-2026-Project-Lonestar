# AI Project: Lone Star

**AI Portfolio and Project Showcase**  
**Project Start**: March 11, 2026  
**Latest Updates**: August 9, 2026  
**Status**: ✅ LIVE - OPERATIONAL - CI/CD ENABLED

---

## 🎯 Project Overview

AI Project: Lone Star is a portfolio website showcasing AI development projects and initiatives. The site demonstrates hands-on exploration of artificial intelligence through practical implementations and real-world applications.

**Live Site**: https://ai.rus-teston.com

---

## 📁 Project Structure

### **documentation/** - Project Documentation
- `PROJECT-LONESTAR-AGREEMENT.md` - Deployment and project agreements
- `CLOUDFRONT-MIGRATION-CHECKLIST.md` - CloudFront setup checklist
- `DEPLOYMENT-MANIFEST.md` - Deployment tracking
- `FOLLOW-UP-ARCHITECTURE-SECURITY-IAC.md` - Tracked improvements
- `PROJECT-1-DEPLOYMENT-RECORD.md` - AI Chatbot deployment record
- `PROJECT-3-PLAN.md` - Language Translator planning
- `PROJECT-SUMMARIES.md` - All project summaries

### **scripts/** - Automation Scripts
- `create-lonestar-bucket.sh` - S3 bucket creation and configuration script

### **website/** - Live Website Files
- `index.html` - Main portfolio page
- **projects/11-architecture-studio/** - Architecture Diagram Studio
- **projects/12-aws-translator/** - On-Prem to AWS Translator
- **projects/13-architecture-catalog/** - AWS Architecture Catalog
- **projects/14-aws-service-reference/** - AWS Service Reference
- **projects/15-course-spec-builder/** - Course Spec Builder


---

## 🚀 Current Projects

### **Live Projects**
1. **AI Chatbot** - ✅ LIVE (March 11, 2026)
   - URL: https://ai.rus-teston.com/projects/01-ai-chatbot/index.html
   - Cloud Architecture Advisor powered by Amazon Bedrock Nova Lite
   - Full-stack serverless application (Lambda + API Gateway + S3)

2. **Well-Architected RAG** - ✅ LIVE (June 8, 2026)
   - URL: https://ai.rus-teston.com/projects/02-waf-rag/index.html
   - RAG-powered Q&A grounded in the official AWS Well-Architected Framework PDF
   - Serverless architecture (API Gateway + Lambda + Bedrock Titan Embeddings V2 + Nova Lite + S3)
   - 1,823 chunks indexed, cosine similarity retrieval, SAM/IaC deployment

3. **Language Translator** - ✅ LIVE (March 12, 2026)
   - URL: https://ai.rus-teston.com/projects/03-language-translator/index.html
   - Multi-language translation using AWS Translate
   - Serverless architecture (Lambda Function URL + S3)

4. **Document Intelligence Pipeline** - ✅ LIVE
   - URL: https://ai.rus-teston.com/projects/04-document-intelligence/index.html
   - AI-powered document processing with Textract and Bedrock
   - Event-driven serverless architecture (S3 + Lambda + Textract + Bedrock)

5. **Text-to-Speech Reader** - ✅ LIVE
   - URL: https://ai.rus-teston.com/projects/05-text-to-speech/index.html
   - AI-powered voice narration using Amazon Polly
   - Serverless architecture (Lambda Function URL + S3)
   - Audio player streams via pre-signed URL; Download MP3 uses separate pre-signed URL with forced attachment

6. **Cost Optimization Advisor** - ✅ LIVE (March 21, 2026)
   - URL: https://ai.rus-teston.com/projects/06-cost-optimizer/index.html
   - AI-powered AWS cost analysis and recommendations using Bedrock Nova Lite
   - Scheduled serverless agent (EventBridge Scheduler + Lambda + Cost Explorer + SES)
   - Second project using SAM/IaC deployment

7. **Architecture Reviewer** - ✅ LIVE (March 21, 2026)
   - URL: https://ai.rus-teston.com/projects/07-architecture-reviewer/index.html
   - AI-powered CloudFormation/SAM template review against Well-Architected Framework
   - Async serverless pipeline (API Gateway + Lambda + SQS + S3 + DynamoDB + Bedrock Nova Lite)
   - First project using SAM/IaC deployment

8. **AI Log Analyzer** - ✅ LIVE
   - URL: https://ai.rus-teston.com/projects/08-log-analyzer/index.html
   - Intelligent log analysis & troubleshooting using Bedrock Nova Lite
   - Event-driven serverless architecture (S3 + Lambda + Bedrock)

9. **Failover Orchestrator** - ✅ LIVE (March 22, 2026)
   - URL: https://ai.rus-teston.com/projects/09-failover-orchestrator/index.html
   - Intelligent multi-region failover with AI-powered decision making using Bedrock Nova Lite
   - Step Functions orchestration with conditional branching (EventBridge + Lambda + Step Functions + DynamoDB + Bedrock Nova Lite + SAM IaC)

10. **Perfect Prompt Builder** - ✅ LIVE (April 2, 2026)
    - URL: https://ai.rus-teston.com/projects/10-prompt-builder/index.html
    - Structured prompt builder with AI-powered enhancement using Bedrock Nova Lite
    - Serverless architecture (Lambda Function URL + Bedrock Nova Lite + S3)

11. **Architecture Diagram Studio** - ✅ LIVE (June 8, 2026)
    - URL: https://ai.rus-teston.com/projects/11-architecture-studio/index.html
    - AI-powered AWS and on-premises architecture diagram generator with migration analysis
    - Serverless architecture (Lambda Function URL + Bedrock Nova Lite + S3)

12. **On-Prem to AWS Translator** - ✅ LIVE (June 8, 2026)
    - URL: https://ai.rus-teston.com/projects/12-aws-translator/index.html
    - Translates on-premises infrastructure descriptions into AWS equivalent architectures
    - Serverless architecture (Lambda Function URL + Bedrock Nova Lite + S3)

13. **AWS Architecture Catalog** - ✅ LIVE (June 8, 2026)
    - URL: https://ai.rus-teston.com/projects/13-architecture-catalog/index.html
    - Curated catalog of AWS reference architectures with diagrams and best-practice descriptions
    - Static frontend (S3 + CloudFront)

14. **AWS Service Reference** - ✅ LIVE (June 8, 2026)
    - URL: https://ai.rus-teston.com/projects/14-aws-service-reference/index.html
    - Searchable AWS service reference with tiered categorization and definitions
    - Static frontend (S3 + CloudFront)

15. **Course Spec Builder** - ✅ LIVE (August 9, 2026)
    - URL: https://ai.rus-teston.com/projects/15-course-spec-builder/index.html
    - 12-section course specification questionnaire with localStorage persistence, PDF + Markdown export
    - Client-side only (S3 + CloudFront, no backend)

---

## 🏗️ Infrastructure

**AWS Services:**
- **S3 Bucket**: `ai-2026-project-lonestar`
- **Region**: `us-east-1`
- **CloudFront Distribution**: `E6LY7PZWUOBBP` (`d309r1vnuulj1s.cloudfront.net`)
- **Custom Domain**: `https://ai.rus-teston.com`
- **ACM Certificate**: Covering `ai.rus-teston.com` (TLS 1.2+, SNI)
- **DNS**: Route 53 alias record in `rus-teston.com` hosted zone
- **Security Headers**: Enterprise-grade response headers policy (HSTS, CSP, X-Frame, XSS Protection)
- **Price Class**: PriceClass_100 (cost optimized)

**Projects:**
- **Project 1**: AI Chatbot (Lambda + API Gateway + Bedrock Nova Lite)
- **Project 3**: Language Translator (Lambda Function URL + AWS Translate)
- **Project 4**: Document Intelligence (Lambda + Textract + Bedrock Nova Lite)
- **Project 5**: Text-to-Speech Reader (Lambda Function URL + Amazon Polly)
- **Project 6**: Cost Optimization Advisor (EventBridge Scheduler + Lambda + Cost Explorer + SES + Bedrock Nova Lite + SAM IaC)
- **Project 7**: Architecture Reviewer (API Gateway + Lambda + SQS + S3 + DynamoDB + Bedrock Nova Lite + SAM IaC)
- **Project 8**: AI Log Analyzer (Lambda + S3 Events + Bedrock Nova Lite)
- **Project 9**: Failover Orchestrator (EventBridge + Lambda + Step Functions + DynamoDB + Bedrock Nova Lite + SAM IaC)
- **Project 2**: Well-Architected RAG (API Gateway + Lambda + Bedrock Titan Embeddings V2 + Nova Lite + S3)
- **Project 10**: Perfect Prompt Builder (Lambda Function URL + Bedrock Nova Lite)
- **Project 11**: Architecture Diagram Studio (Lambda Function URL + Bedrock Nova Lite)
- **Project 12**: On-Prem to AWS Translator (Lambda Function URL + Bedrock Nova Lite)
- **Project 13**: AWS Architecture Catalog (Static — S3 + CloudFront)
- **Project 14**: AWS Service Reference (Static — S3 + CloudFront)
- **Project 15**: Course Spec Builder (Static — S3 + CloudFront, client-side only)

**CI/CD Pipeline:**
- **GitHub Repos**: Public repos at github.com/RusTeston
- **GitHub Actions**: Auto-deploy on push to main branch
- **OIDC Federation**: Secure AWS authentication (no stored credentials)
- **IAM Role**: `GitHubActions-Deploy` with least-privilege permissions
- **CloudFront Invalidation**: Automatic cache invalidation after each deploy

**Website Features:**
- Single-page portfolio design
- Dark modern theme with Inter font
- Professional grid layout for projects
- Project summary modals on all project pages
- Responsive layout (desktop/tablet optimized)
- 15 AI projects live
- No external dependencies

---

## 📋 Technical Details

**Technology Stack:**
- Pure HTML/CSS (no frameworks)
- Self-contained single file
- AWS S3 static hosting
- Corporate-standard Arial/Helvetica fonts

**Design Elements:**
- Dark modern theme (navy gradient background, white/light blue text)
- Inter font (matching rus-teston.com)
- Professional grid layout for projects

---

## 🎊 Project Status

**LIVE AND OPERATIONAL** ✅  
**Website**: Fully functional and accessible  
**Infrastructure**: S3 bucket configured and optimized  
**Design**: Professional corporate aesthetic  

**Next Steps:**
- Add automated testing to CI/CD workflows
- Migrate remaining projects to SAM/CloudFormation (IaC) — ✅ Started with Project 7
- Tighten Lambda CORS from `*` to `https://ai.rus-teston.com` (deferred — requires SAM redeploys)
- Expand project portfolio as new AI projects are completed

**Recent Updates:**
- ✅ **Repo Cleanup** (August 9, 2026): Moved unused files to POSSIBLE_DELETE_ME, deleted originals (screenshots, generated-diagrams, 02-agentic-rag abandoned folder)
- ✅ **Project 15: Course Spec Builder** (August 9, 2026): 12-section questionnaire, localStorage auto-save, jsPDF PDF export, Markdown download, access code gate
- ✅ **Project 02: Well-Architected RAG** (June 8, 2026): RAG Q&A grounded in AWS WAF PDF — 1,823 chunks, Titan Embeddings V2, cosine similarity, Nova Lite via Converse API, SAM deployment. Includes step-by-step summary, My RAG diagram, and AWS Best Practice RAG diagram comparison.
- ✅ **Project 13/14 card dates** (June 8, 2026): Added Jun 8, 2026 date and yellow styling to New badge cards (02, 11-14)
- ✅ **Project 5: Audio Player Fix** (May 11, 2026): Fixed audio player not loading — added `media-src` to CloudFront CSP, switched to pre-signed URLs for streaming (audio player) and forced download (Download MP3 button)
- ✅ **Project 10: Perfect Prompt Builder** (April 2, 2026): Structured prompt builder with AI enhancement via Bedrock Nova Lite
- ✅ **CloudFront + HTTPS** (March 25, 2026): `ai.rus-teston.com` served via CloudFront CDN with TLS 1.2+, security headers, PriceClass_100
- ✅ **CI/CD CloudFront invalidation** (March 25, 2026): Auto-invalidation added to GitHub Actions workflow
- ✅ **URL migration** (March 25, 2026): All S3 URLs replaced with `https://ai.rus-teston.com` across all projects, README, and portfolio site
- ✅ **Project summary modals** (March 25, 2026): Clickable summary overlays added to all 8 project pages
- ✅ **P9 restore fix** (March 25, 2026): Restore Healthy clears AI verdict and timeline
- ✅ **Project 9: Failover Orchestrator** (March 22, 2026): AI-powered multi-region failover with Step Functions, Bedrock reasoning layer, SAM/IaC
- ✅ **Project 6: Cost Optimization Advisor** (March 21, 2026): Replaced Superhero Transformer, SAM/IaC, EventBridge + SES
- ✅ **Project 7: Architecture Reviewer** (March 21, 2026): First SAM/IaC project, async pipeline with Bedrock
- ✅ **Landing page redesign** (March 21, 2026): Dark modern theme, dropped Texas branding
- ✅ **CI/CD Pipeline** (March 20, 2026): GitHub Actions + OIDC federation for both repos
- ✅ **CI/CD Pipeline diagrams** added to Projects 1, 3, 4, 5, 8
- ✅ **Well-Architected designs** created for Projects 1, 3, 4, 5, 8
- ✅ **Error pages** deployed for both sites
- ✅ **Project 8: AI Log Analyzer** built and deployed

---

*This project demonstrates AWS cloud infrastructure expertise, static website hosting, and professional web design principles.*
