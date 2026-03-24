# AI Project: Lone Star — Project Summaries

**All Projects Built and Deployed: March 11–22, 2026**
**Document Created**: March 22, 2026

---

## Project 1: Cloud Architecture Advisor (AI Chatbot)

### What It Is
An AI chatbot that provides AWS architecture recommendations. Users describe their application needs and the chatbot responds with detailed architecture advice including recommended services, reasoning, and tradeoffs.

### Architecture
**Synchronous request-response:**
- User Browser → S3 (static frontend) → API Gateway (REST) → Lambda → Bedrock Nova Lite → response

### AWS Services Used
S3, API Gateway (REST), Lambda (Python 3.12), Bedrock Nova Lite, IAM, CloudWatch

### What We Built — File by File
| File | Purpose |
|------|---------|
| `backend/lambda_function.py` | Lambda handler — takes user message, sends to Bedrock with system prompt, returns architecture advice |
| `frontend/index.html` | Chat interface with project label and diagram links |
| `frontend/app.js` | Frontend logic — API calls, message rendering, markdown formatting, loading states |
| `frontend/styles.css` | Professional styling |
| `scripts/deploy-lambda.sh` | Lambda deployment script |
| `scripts/deploy-api-gateway.sh` | API Gateway setup script |
| `scripts/test-lambda.sh` | Lambda testing script |
| `docs/WELL-ARCHITECTED-DESIGN.md` | WAF analysis across all 6 pillars |
| `README.md` | Full project documentation |

### Key Design Decisions
- API Gateway REST API (not Function URL) — first project, established the pattern
- System prompt scopes Bedrock to act as an AWS Solutions Architect
- Markdown formatting in frontend for headings, bold, bullets
- Temperature 0.7 for creative but grounded responses

### Deployment
- Lambda: `CloudArchitectureAdvisor` with API Gateway `ri802yjmt0`
- Frontend: `s3://ai-2026-project-lonestar/projects/01-ai-chatbot/`
- Deployed manually via bash scripts (pre-SAM era)

### Estimated Cost
~$4.30/month

---

## Project 3: Language Translator

### What It Is
A multi-language translation service supporting 9 languages (English, Spanish, French, German, Japanese, Chinese, Portuguese, Italian, Korean) using AWS Translate — a purpose-built AI service rather than a general LLM.

### Architecture
**Synchronous request-response:**
- User Browser → S3 (static frontend) → Lambda Function URL → AWS Translate → response

### AWS Services Used
S3, Lambda Function URL (Python 3.12), AWS Translate, IAM, CloudWatch

### What We Built — File by File
| File | Purpose |
|------|---------|
| `backend/lambda_function.py` | Lambda handler — validates input, calls AWS Translate, returns translated text |
| `frontend/index.html` | Translation interface with language selectors |
| `frontend/app.js` | Frontend logic — language dropdowns, character counter, API calls |
| `frontend/styles.css` | Professional styling matching Project 1 |
| `scripts/deploy-lambda.sh` | Deployment script |
| `docs/WELL-ARCHITECTED-DESIGN.md` | WAF analysis across all 6 pillars |
| `README.md` | Full project documentation |

### Key Design Decisions
- Lambda Function URL instead of API Gateway — simpler, cheaper for basic use cases
- AWS Translate instead of Bedrock — purpose-built service is 50% cheaper and faster for pure translation
- Auto-detect source language option
- 5,000 character limit (frontend + backend validation)
- CORS handled by Function URL (not Lambda code) — lesson learned from duplicate header bug

### Deployment
- Lambda: `LanguageTranslator` with Function URL
- Frontend: `s3://ai-2026-project-lonestar/projects/03-language-translator/`
- Deployed manually via bash scripts

### Estimated Cost
~$7.60/month (at 1,000 translations)

---

## Project 4: Document Intelligence Pipeline

### What It Is
An AI-powered document processing pipeline that extracts text from uploaded documents (PDF, PNG, JPEG) using Textract, then analyzes the content with Bedrock Nova Lite to classify document type, generate a summary, and extract key fields.

### Architecture
**Event-driven async pipeline:**
- User Browser → Lambda Function URL (API) → S3 `uploads/`
- S3 event trigger → Lambda (Processor) → Textract → Bedrock Nova Lite → S3 `results/`
- Frontend polls `/result` endpoint until processing completes

### AWS Services Used
S3 (uploads + results), Lambda Function URL (Python 3.12) × 2, AWS Textract, Bedrock Nova Lite, IAM, CloudWatch

### What We Built — File by File
| File | Purpose |
|------|---------|
| `backend/api_lambda.py` | API handler — file upload to S3, result retrieval, double-slash fix for Function URLs |
| `backend/processor_lambda.py` | S3-triggered processor — Textract text extraction → Bedrock analysis → JSON results to S3 |
| `frontend/index.html` | Drag-and-drop upload interface with results display |
| `frontend/app.js` | Frontend logic — file upload, polling, results rendering (doc type, summary, key fields, extracted text) |
| `frontend/styles.css` | Professional styling |
| `scripts/deploy.sh` | Deployment script |
| `docs/WELL-ARCHITECTED-DESIGN.md` | WAF analysis across all 6 pillars |

### Key Design Decisions
- Two Lambda functions: API (upload/results) and Processor (Textract + Bedrock) — separation of concerns
- S3 event trigger for async processing — user doesn't wait for Textract + Bedrock pipeline
- Base64 decode for binary uploads from Lambda Function URLs
- Double-slash rawPath fix (Lambda Function URL quirk)
- Textract `detect_document_text` (cheapest API) for text extraction
- First 4,000 chars sent to Bedrock for analysis (balances quality vs cost)
- User-friendly error for UnsupportedDocumentException (encrypted/signed PDFs)

### Deployment
- Lambda API: Function URL, Lambda Processor: S3-triggered
- Frontend: `s3://ai-2026-project-lonestar/projects/04-document-intelligence/`
- Deployed manually via bash scripts

### Estimated Cost
~$5-10/month (at 100 documents/day)

---

## Project 5: Text-to-Speech Reader

### What It Is
An AI-powered voice narration tool that converts uploaded text files (TXT, PDF) to MP3 audio using Amazon Polly. Supports both Neural (higher quality) and Standard voice engines with 4 voice options each.

### Architecture
**Event-driven async pipeline:**
- User Browser → Lambda Function URL (API) → S3 `uploads/` (filename encodes voice settings)
- S3 event trigger → Lambda (Processor) → Polly (+ Textract for PDFs) → S3 `results/` (MP3 + metadata JSON)
- Frontend polls `/result` endpoint, then plays audio via HTML5 audio player

### AWS Services Used
S3 (uploads + results), Lambda Function URL (Python 3.12) × 2, Amazon Polly, AWS Textract (for PDFs), IAM, CloudWatch

### What We Built — File by File
| File | Purpose |
|------|---------|
| `backend/api_lambda.py` | API handler — file upload with voice settings in filename, result retrieval, voice list endpoint |
| `backend/processor_lambda.py` | S3-triggered processor — reads file, extracts text (Textract for PDF), Polly synthesis, saves MP3 + metadata |
| `frontend/index.html` | Upload interface with voice quality/voice selection dropdowns, audio player |
| `frontend/app.js` | Frontend logic — voice options, file upload, polling, audio playback, download link |
| `frontend/styles.css` | Professional styling |
| `scripts/deploy.sh` | Deployment script |
| `docs/WELL-ARCHITECTED-DESIGN.md` | WAF analysis across all 6 pillars |

### Key Design Decisions
- Voice settings encoded in filename (`timestamp_engine_voiceId_originalname`) — no database needed
- Polly 3,000 character limit enforced with truncation warning shown to user
- Neural vs Standard engine choice exposed to user
- Audio served via direct S3 URL with HTML5 audio player + download button
- Same two-Lambda async pattern as Project 4

### Deployment
- Lambda API: Function URL, Lambda Processor: S3-triggered
- Frontend: `s3://ai-2026-project-lonestar/projects/05-text-to-speech/`
- Deployed manually via bash scripts

### Estimated Cost
~$8-12/month (at 200 conversions/day)

---

## Project 6: Cost Optimization Advisor

### What It Is
An AI-powered AWS cost analysis agent that scans your account for wasteful resources — unattached EBS volumes, idle EC2/RDS instances, S3 buckets without lifecycle rules, oversized Lambda functions — then uses Bedrock to generate plain-English recommendations ranked by potential savings. Runs weekly on a schedule and sends email digests via SES.

### Architecture
**Scheduled serverless agent + on-demand API:**
- Weekly: EventBridge Scheduler (cron) → Collect Lambda → S3 → Analyze Lambda (Bedrock) → S3 → Notify Lambda (SES email)
- On-demand: API Gateway → On-Demand Lambda (collect + analyze inline) → Frontend

### AWS Services Used
EventBridge Scheduler, Lambda (Python 3.12) × 4, S3, Bedrock Nova Lite, SES, API Gateway, Cost Explorer, EC2/RDS/S3/Lambda/CloudWatch APIs, IAM

### What We Built — File by File
| File | Purpose |
|------|---------|
| `template.yaml` | SAM/IaC template — all infrastructure (2nd SAM project) |
| `samconfig.toml` | SAM deploy config (stack: `project-06-cost-optimizer`) |
| `functions/collect/collect.py` | Collects findings from Cost Explorer, EC2, RDS, S3, Lambda, CloudWatch; also has on-demand handler with inline Bedrock analysis |
| `functions/analyze/analyze.py` | Reads raw findings from S3, sends to Bedrock for analysis, saves report, chains to notify |
| `functions/notify/notify.py` | Reads report from S3, builds styled HTML email, sends via SES |
| `frontend/index.html` | Dark modern theme dashboard — "Run Cost Scan Now" button, results with savings banner, severity-coded findings |
| `frontend/WELL-ARCHITECTED-DESIGN.md` | WAF analysis across all 6 pillars |

### Key Design Decisions
- Two execution paths: weekly scheduled (async chain) and on-demand (sync inline) — same collection logic, different orchestration
- Read-only IAM for all AWS service scanning — never modifies customer resources
- S3 lifecycle: 30-day auto-delete for reports
- SES email with styled HTML (severity colors, savings per finding, remediation steps)
- Replaced the original "Superhero Transformer" project (Project 6 was rebuilt)

### Deployment
- Deployed via `sam build && sam deploy` (SAM/IaC)
- Stack name: `project-06-cost-optimizer`
- Frontend: `s3://ai-2026-project-lonestar/projects/06-cost-optimizer/`

### Estimated Cost
~$1-2/month (weekly scans + occasional on-demand)

---

## Project 7: Intelligent AWS Architecture Reviewer

### What It Is
An AI-powered CloudFormation/SAM template reviewer that analyzes infrastructure templates against the AWS Well-Architected Framework. Users paste a template, and the system returns prioritized findings across all 6 WAF pillars with severity ratings and specific recommendations.

### Architecture
**Async serverless pipeline:**
- API Gateway → Ingest Lambda → S3 (template storage) + SQS (analysis queue)
- SQS → Analyze Lambda (Bedrock Nova Lite) → DynamoDB (results)
- Frontend polls → API Gateway → Results Lambda → DynamoDB

### AWS Services Used
API Gateway, Lambda (Python 3.12) × 3, S3, SQS, DynamoDB (SimpleTable), Bedrock Nova Lite, IAM

### What We Built — File by File
| File | Purpose |
|------|---------|
| `template.yaml` | SAM/IaC template — all infrastructure (1st SAM project) |
| `samconfig.toml` | SAM deploy config (stack: `project-07-architecture-reviewer`) |
| `functions/ingest/ingest.py` | Validates template (50KB limit), stores in S3, sends job to SQS, returns jobId |
| `functions/analyze/analyze.py` | SQS-triggered — reads template from S3, sends to Bedrock with WAF system prompt, stores results in DynamoDB |
| `functions/results/results.py` | API handler — reads job status/results from DynamoDB |
| `frontend/index.html` | Dark modern theme — template textarea, "Analyze Template" button, "Try a Demo Template" button, severity-coded findings by WAF pillar |
| `frontend/WELL-ARCHITECTED-DESIGN.md` | WAF analysis across all 6 pillars |

### Key Design Decisions
- SQS decoupling between ingest and analysis — handles Bedrock latency without blocking the API
- DynamoDB for job status tracking (QUEUED → ANALYZING → COMPLETE/FAILED)
- Demo template button auto-populates a deliberately flawed template (public S3, IAM `*`, oversized Lambda, provisioned DynamoDB)
- S3 lifecycle: 7-day auto-delete for uploaded templates
- First project deployed with SAM/IaC — established the pattern for Projects 6 and 9

### Deployment
- Deployed via `sam build && sam deploy` (SAM/IaC)
- Stack name: `project-07-architecture-reviewer`
- Frontend: `s3://ai-2026-project-lonestar/projects/07-architecture-reviewer/`

### Estimated Cost
~$1-2/month

---

## Project 8: AI Log Analyzer

### What It Is
An intelligent log analysis and troubleshooting tool. Users upload log files (LOG, TXT, CSV, JSON) and Bedrock Nova Lite provides a comprehensive analysis report: severity assessment, error root causes with fixes, warnings, recurring patterns, timeline narrative, prioritized remediation actions, and prevention tips.

### Architecture
**Event-driven async pipeline:**
- User Browser → Lambda Function URL (API) → S3 `uploads/`
- S3 event trigger → Lambda (Processor) → Bedrock Nova Lite → S3 `results/`
- Frontend polls `/result` endpoint until analysis completes

### AWS Services Used
S3 (uploads + results), Lambda Function URL (Python 3.12) × 2, Bedrock Nova Lite, IAM, CloudWatch

### What We Built — File by File
| File | Purpose |
|------|---------|
| `backend/api_lambda.py` | API handler — file upload with extension validation (.log/.txt/.csv/.json), result retrieval |
| `backend/processor_lambda.py` | S3-triggered processor — reads log file, sends first 15,000 chars to Bedrock with detailed analysis prompt, saves structured JSON results |
| `frontend/index.html` | Upload interface with comprehensive results display (severity badge, summary, timeline, errors, warnings, patterns, actions, prevention tips) |
| `frontend/app.js` | Frontend logic — file upload, polling, section-by-section results rendering with severity color coding |
| `frontend/styles.css` | Professional styling with severity-specific colors |
| `backend/deploy.sh` | Deployment script |
| `docs/WELL-ARCHITECTED-DESIGN.md` | WAF analysis across all 6 pillars |

### Key Design Decisions
- Most detailed Bedrock prompt of all projects — structured JSON output with errors, warnings, patterns, timeline, actions, prevention tips
- 15,000 character log sample (largest of any project) for thorough analysis
- Temperature 0.3 for consistent, factual analysis
- maxTokens 4,000 for detailed output
- Same two-Lambda async pattern as Projects 4 and 5
- File extension validation (not MIME type) for log files

### Deployment
- Lambda API: Function URL, Lambda Processor: S3-triggered
- Frontend: `s3://ai-2026-project-lonestar/projects/08-log-analyzer/`
- Deployed manually via bash scripts

### Estimated Cost
~$8-12/month (at 100 analyses/day)

---

## Project 9: Intelligent Multi-Region Failover Orchestrator

### What It Is
An AI-powered failover orchestration system that monitors a simulated primary region endpoint, detects failures, uses Bedrock Nova Lite to reason about whether failover is warranted, and then orchestrates a simulated multi-region failover — all through a Step Functions state machine.

### Architecture
**Event-driven serverless pipeline:**
- **EventBridge Scheduler** → triggers health checks every 2 minutes
- **Lambda (HealthCheck)** → hits a simulated endpoint via Function URL, stores results in DynamoDB
- **Step Functions State Machine** → triggered on failure detection, orchestrates the decision pipeline:
  1. **Decide** (Lambda + Bedrock Nova Lite) — gathers last 5 health checks, builds evidence, asks Bedrock to reason about whether failover is warranted
  2. **EvaluateVerdict** (Choice state) — only proceeds if `failover_warranted: true` AND `confidence: high`
  3. **ExecuteFailover** (Lambda) — simulates Route 53 DNS update, standby resource warming, health verification, and posts to Slack
- **DynamoDB** — single-table design (pk/sk) for health checks, config, and incident history with TTL auto-cleanup
- **API Gateway** — 3 endpoints: `/status`, `/history`, `/simulate`
- **Simulated Endpoint** (Lambda Function URL) — toggleable healthy/unhealthy via DynamoDB flag

### AWS Services Used
EventBridge Scheduler, Step Functions, Lambda (Python 3.12) × 5, Bedrock Nova Lite, DynamoDB, API Gateway, Lambda Function URLs, (optional) Slack webhook

### What We Built — File by File
| File | Purpose |
|------|---------|
| `template.yaml` | SAM/IaC template — all infrastructure defined as code (3rd SAM project) |
| `samconfig.toml` | SAM deploy config (stack: `project-09-failover-orchestrator`) |
| `statemachine/failover.asl.json` | Step Functions ASL definition — Decide → EvaluateVerdict → ExecuteFailover/NoAction |
| `functions/healthcheck/healthcheck.py` | Scheduled health check + `/status` and `/history` API handlers |
| `functions/decide/decide.py` | Bedrock reasoning — builds evidence from 5 checks, prompts Nova Lite for JSON verdict |
| `functions/failover/failover.py` | Simulated failover execution — Route 53, resource warming, incident logging, Slack notification |
| `functions/simulated-endpoint/endpoint.py` | Toggleable endpoint + `/simulate` API handler |
| `frontend/index.html` | Dark modern theme dashboard — health status, simulation controls, recent checks, AI verdict, incident timeline |
| `frontend/WELL-ARCHITECTED-DESIGN.md` | Well-Architected Framework analysis across all 5 pillars |
| `frontend/project-9-architecture.png` | Architecture diagram |
| `frontend/project-9-well-architected.png` | WAF diagram |

### Key Design Decisions
- **Simulation mode** — failover actions (Route 53, resource warming) are simulated to prevent accidental infrastructure changes, but health checks and AI reasoning are real
- **AI decision gate** — Bedrock must return `failover_warranted: true` with `confidence: high` before failover executes, preventing false positives
- **Single-table DynamoDB** — pk/sk pattern for health checks (`HEALTHCHECK`), config (`CONFIG`), and incidents (`INCIDENT`)
- **24h TTL on health checks, 7d TTL on incidents** — prevents unbounded storage growth
- **Slack integration** — optional webhook for incident notifications with formatted Block Kit messages

### Deployment
- Deployed via `sam build && sam deploy` (SAM/IaC)
- Stack name: `project-09-failover-orchestrator`
- Frontend: `s3://ai-2026-project-lonestar/projects/09-failover-orchestrator/`
- Landing page updated with Project 9 card (active/live status)
- Git committed as: `Project 09: Failover Orchestrator - full build with SAM deploy, frontend, diagrams, WAF doc`

### Estimated Cost
~$1-2/month

---

## Cross-Project Evolution

### Deployment Pattern Evolution
| Projects | Deployment Method |
|----------|------------------|
| 1, 3, 4, 5, 8 | Manual bash scripts, Lambda Function URLs |
| 7 | First SAM/IaC project (established the pattern) |
| 6 | Second SAM/IaC project |
| 9 | Third SAM/IaC project (most complex — Step Functions + EventBridge) |

### Architecture Pattern Evolution
| Pattern | Projects |
|---------|----------|
| Sync request-response (API Gateway → Lambda → AI) | 1 |
| Sync request-response (Function URL → Lambda → AWS service) | 3 |
| Async event-driven (Function URL → S3 → Lambda → AI → S3, frontend polls) | 4, 5, 8 |
| Async queue-based (API Gateway → SQS → Lambda → AI → DynamoDB, frontend polls) | 7 |
| Scheduled agent (EventBridge → Lambda chain → SES email) | 6 |
| Orchestrated pipeline (EventBridge → Lambda → Step Functions → AI → DynamoDB) | 9 |

### AI Services Used
| Service | Projects |
|---------|----------|
| Bedrock Nova Lite | 1, 4, 6, 7, 8, 9 |
| AWS Translate | 3 |
| Amazon Polly | 5 |
| AWS Textract | 4, 5 |

### All Projects Live At
http://ai-2026-project-lonestar.s3-website-us-east-1.amazonaws.com

---

*This document provides a complete reference for all projects built in AI Project: Lone Star.*
