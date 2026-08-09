# AI Project: Lone Star — Project Summaries

**All Projects Built and Deployed: March 11–August 9, 2026**
**Document Last Updated**: August 9, 2026

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

## Project 2: Well-Architected Framework RAG

### What It Is
A RAG-powered Q&A tool that answers questions about the AWS Well-Architected Framework. The official AWS WAF PDF (1,002 pages) was pre-processed into 1,823 text chunks, embedded with Bedrock Titan Embeddings V2, and stored in S3. At query time, the user's question is embedded and compared against all chunks using cosine similarity. The top 5 most relevant chunks are injected as context into Bedrock Nova Lite, which generates a grounded answer with page citations.

### Architecture
**Ingestion (one-time):**
- WAF PDF (S3) → Ingestion Script (PyMuPDF) → Bedrock Titan Embeddings V2 → embeddings.json (S3, 41.9MB)

**Query (runtime):**
- User Browser → CloudFront → API Gateway → Lambda → Titan Embeddings V2 (embed question) → S3 embeddings.json (cosine similarity) → Bedrock Nova Lite (Converse API) → answer + source pages

### AWS Services Used
S3, API Gateway (REST), Lambda (Python 3.12), Bedrock Titan Embeddings V2, Bedrock Nova Lite, IAM, CloudWatch

### What We Built — File by File
| File | Purpose |
|------|---------|
| `ingestion.py` | One-time script — extracts text from WAF PDF, chunks, embeds via Titan V2, writes embeddings.json to S3 |
| `lambda/query_handler.py` | Query Lambda — loads embeddings from S3, cosine similarity search, calls Nova Lite via Converse API |
| `template.yaml` | SAM/IaC template — API Gateway + Lambda + IAM |
| `index.html` | Frontend — question input, example questions, answer panel with source pages, step-by-step summary toggle, My RAG diagram toggle, AWS Best Practice RAG diagram toggle |

### Key Design Decisions
- No managed vector DB (avoids $700+/month OpenSearch Serverless cost) — flat JSON + in-Lambda cosine similarity
- Embeddings cached in Lambda memory across warm invocations — 41.9MB loaded once per cold start
- Top-k = 5 chunks per query (~2,000 tokens of context)
- 1,823 chunks with 150-char overlap to preserve cross-boundary context
- Open API (no Cognito) consistent with Project 1 — throttled at 10 req/sec via API Gateway
- Includes side-by-side comparison of My RAG approach vs AWS Best Practice (Bedrock Knowledge Base + OpenSearch)

### Deployment
- SAM stack: `waf-rag`
- API: `https://cnprlsg9sb.execute-api.us-east-1.amazonaws.com/prod/query`
- Frontend: `s3://ai-2026-project-lonestar/projects/02-waf-rag/`

### Estimated Cost
~$1.70/month at light use (1,500 questions/month)

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
- Audio player uses pre-signed S3 URL (`audio_url`) for in-browser streaming
- Download button uses a separate pre-signed S3 URL (`download_url`) with `Content-Disposition: attachment` to force file save
- CloudFront CSP includes `media-src https://ai-text-to-speech-p5.s3.amazonaws.com` to allow audio player to load cross-origin S3 URLs
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

## Project 10: Perfect Prompt Builder

### What It Is
A structured prompt engineering tool that guides users through building high-quality prompts for any foundation model. Users fill in Role, Task, Context, Constraints, Output Format, Verification, and Examples fields. The tool assembles a formatted prompt, then optionally sends it to Bedrock Nova Lite for AI-powered scoring, improvement suggestions, and an enhanced version of the prompt.

### Architecture
**Synchronous request-response:**
- User Browser → S3 (static frontend) → Lambda Function URL → Bedrock Nova Lite → score + improvements + enhanced prompt

### AWS Services Used
S3, Lambda Function URL (Python 3.12), Bedrock Nova Lite, IAM, CloudWatch

### What We Built — File by File
| File | Purpose |
|------|---------|
| `frontend/index.html` | Single-file app — 7 structured input fields (Role, Task, Context, Constraints, Output Format, Verification, Examples), Generate Prompt button, Enhance with AI button, score circle, improvement cards, enhanced prompt output |

### Key Design Decisions
- Client-side prompt assembly — no backend needed for generation, only for AI enhancement
- Score circle (0–100) with color tiers: green (≥75), yellow (≥50), red (<50)
- Improvement suggestions rendered as individual cards with 💡 prefix
- Enhanced prompt shown alongside original for easy comparison
- Demo button pre-fills a realistic AWS migration scenario
- Role dropdown with 6 presets + custom option
- Lambda Function URL: `https://n7taftgspogdij7l4g2ercpnsi0srofk.lambda-url.us-east-1.on.aws/`

### Deployment
- Lambda: Function URL
- Frontend: `s3://ai-2026-project-lonestar/projects/10-prompt-builder/`
- Deployed manually via bash scripts

### Estimated Cost
~$1-2/month (light Bedrock usage for enhancement only)

---

## Project 11: Architecture Diagram Studio

### What It Is
A dual-panel architecture diagram generator that produces SVG diagrams from plain-language descriptions. Users can describe an on-premises infrastructure (left panel) and an AWS architecture (right panel) independently, then trigger a migration analysis comparing the two. Diagrams can be downloaded as SVG or PNG and expanded to fullscreen.

### Architecture
**Synchronous request-response:**
- User Browser → S3 (static frontend) → Lambda Function URL → Bedrock Nova Lite → SVG diagram or migration analysis HTML

### AWS Services Used
S3, Lambda Function URL (Python 3.12), Bedrock Nova Lite, IAM, CloudWatch

### What We Built — File by File
| File | Purpose |
|------|---------|
| `website/projects/11-architecture-studio/index.html` | Dual-panel UI — On-Prem panel (blue) and AWS panel (orange), fullscreen modal, SVG/PNG download, migration analysis output |

### Key Design Decisions
- Single Lambda Function URL handles three request types: `onprem`, `aws`, and `migration`
- Lambda returns raw SVG for diagrams; returns HTML fragment for migration analysis
- Migration trigger button only appears when both panels have generated diagrams
- Client-side PNG conversion using Canvas API (2x scale for high resolution)
- Fullscreen modal with per-panel download buttons
- Ctrl+Enter keyboard shortcut to generate
- Lambda Function URL: `https://6mcb5tctfchpldojluzolhh6gu0ajpqj.lambda-url.us-east-1.on.aws/`
- Same Lambda URL shared with Project 12 (On-Prem to AWS Translator)

### Deployment
- Lambda: Function URL
- Frontend: `s3://ai-2026-project-lonestar/projects/11-architecture-studio/`
- Deployed via CI/CD (GitHub Actions)

### Estimated Cost
~$2-4/month

---

## Project 12: On-Prem to AWS Translator

### What It Is
A single-input translation tool that takes a plain-language description of on-premises infrastructure and returns a structured AWS architecture recommendation plus a full migration analysis. Output includes an AWS architecture description (copyable for use in diagramming tools), a component mapping table (on-prem → AWS service), migration benefits, and a phased migration roadmap. Includes a direct link to open the Architecture Diagram Studio with the description pre-loaded.

### Architecture
**Synchronous request-response:**
- User Browser → S3 (static frontend) → Lambda Function URL → Bedrock Nova Lite → AWS description + migration analysis HTML

### AWS Services Used
S3, Lambda Function URL (Python 3.12), Bedrock Nova Lite, IAM, CloudWatch

### What We Built — File by File
| File | Purpose |
|------|---------|
| `website/projects/12-aws-translator/index.html` | Single-page app — textarea input, character counter (4,000 limit), AWS description output with copy button, migration analysis HTML rendered inline, "Build a Diagram in Architecture Studio" CTA button |

### Key Design Decisions
- Request type `translate` sent to shared Lambda URL (same as Project 11)
- Lambda returns `aws_description` (plain text) + `html` (styled migration analysis fragment)
- Copy button auto-copies description to clipboard when user clicks "Build a Diagram in Architecture Studio"
- Opens Architecture Studio in new tab with description ready to paste into AWS panel
- Dark navy theme with yellow-green accent (`#E0FF4F`) matching Lonestar design language
- Lambda Function URL: `https://6mcb5tctfchpldojluzolhh6gu0ajpqj.lambda-url.us-east-1.on.aws/`

### Deployment
- Lambda: Function URL (shared with Project 11)
- Frontend: `s3://ai-2026-project-lonestar/projects/12-aws-translator/`
- Deployed via CI/CD (GitHub Actions)

### Estimated Cost
~$1-2/month (shared Lambda with Project 11)

---

## Project 13: AWS Architecture Catalog

### What It Is
A curated static catalog of AWS reference architectures with diagrams and best-practice descriptions. Users browse a searchable, filterable catalog of common AWS architecture patterns. Each entry includes a description, the AWS services involved, and a reference architecture diagram.

### Architecture
**Static frontend only:**
- User Browser → CloudFront → S3 (static HTML + images)

### AWS Services Used
S3, CloudFront, IAM

### What We Built — File by File
| File | Purpose |
|------|---------|
| `website/projects/13-architecture-catalog/index.html` | Static catalog page — searchable/filterable architecture entries, sidebar navigation, detail panel with diagram and description |
| `website/projects/13-architecture-catalog/images/` | Architecture diagram PNGs (one per catalog entry) |

### Key Design Decisions
- No backend — fully static, zero runtime cost
- All architecture data embedded in the HTML as a JavaScript array
- Diagrams generated using the Python `diagrams` package and stored as PNGs
- Each diagram follows the high-fidelity standard: left-to-right flow, proper clusters, every service as a node
- Content researched against AWS documentation before each diagram was drawn

### Deployment
- Frontend: `s3://ai-2026-project-lonestar/projects/13-architecture-catalog/`
- Deployed via CI/CD (GitHub Actions)

### Estimated Cost
~$0/month (static only, CloudFront free tier)

---

## Project 14: AWS Service Reference

### What It Is
A searchable AWS service reference guide with tiered categorization. Services are organized into 9 tiers by how frequently they appear in real-world architectures (e.g., "Appears in virtually every architecture", "Core compute and data", "AI and ML (rapidly rising)"). Each entry includes a plain-English definition.

### Architecture
**Static frontend only:**
- User Browser → CloudFront → S3 (static HTML)

### AWS Services Used
S3, CloudFront, IAM

### What We Built — File by File
| File | Purpose |
|------|---------|
| `website/projects/14-aws-service-reference/index.html` | Static reference page — search bar, tier-grouped service cards, definitions, tier badges |

### Key Design Decisions
- No backend — fully static, zero runtime cost
- All service data embedded as a JavaScript array (~75 services)
- 9 tiers: Appears in virtually every architecture, Core compute and data, Networking, Storage and database (specialized), Messaging and integration, Security and governance, DevOps, Analytics and data, AI and ML (rapidly rising)
- Live search filters across service names and definitions
- Designed as a quick-reference companion to Project 13 (Architecture Catalog)

### Deployment
- Frontend: `s3://ai-2026-project-lonestar/projects/14-aws-service-reference/`
- Deployed via CI/CD (GitHub Actions)

### Estimated Cost
~$0/month (static only, CloudFront free tier)

---

## Project 15: Course Specification Builder

### What It Is
A client-side course design questionnaire for instructional designers and training requestors. Users answer up to ~150 questions across 12 sections covering business need, target audience, performance expectations, learning objectives, scope, source materials, delivery format, instructional approach, assessment, measurement, stakeholders, and schedule. Answers auto-save to localStorage. On completion, users can download a full Q&A PDF or a structured Markdown course specification document.

### Architecture
**Client-side only:**
- User Browser → CloudFront → S3 (static HTML, no backend)

### AWS Services Used
S3, CloudFront, IAM

### What We Built — File by File
| File | Purpose |
|------|---------|
| `website/projects/15-course-spec-builder/index.html` | Single-file app — access code gate, requestor info screen, 12-section questionnaire with sidebar nav, progress bar, review screen, PDF download (jsPDF), Markdown download (Blob) |
| `website/projects/15-course-spec-builder/spec.md` | Technical specification document for the project |

### Key Design Decisions
- Access code gate (`8675309`) — prevents public access without distribution
- localStorage auto-save with 500ms debounce — no data loss on refresh or accidental close
- Schema versioning (`csb:v1:session`) — detects stale saved data and prompts user
- jsPDF for PDF generation — runs entirely in-browser, no server needed
- Markdown export uses Blob API — structured spec document for course developers
- Two output formats: full Q&A PDF (for requestor records) and condensed Markdown spec (for course developers)
- Section status dots: not started (grey), in-progress (yellow), complete (green), missing required (red)
- Required fields validated on section exit, not on every keystroke
- "Not applicable" toggle on optional questions
- Filename sanitization: PDF named `firstname-lastname-course-request.pdf`, Markdown named `course-title-spec.md`
- No external dependencies except jsPDF CDN

### Deployment
- Frontend: `s3://ai-2026-project-lonestar/projects/15-course-spec-builder/`
- Deployed via CI/CD (GitHub Actions)

### Estimated Cost
~$0/month (static only, CloudFront free tier)

---

## Cross-Project Evolution

### Deployment Pattern Evolution
| Projects | Deployment Method |
|----------|------------------|
| 1, 3, 4, 5, 8, 10, 11, 12 | Manual bash scripts, Lambda Function URLs |
| 7 | First SAM/IaC project (established the pattern) |
| 6 | Second SAM/IaC project |
| 9 | Third SAM/IaC project (most complex — Step Functions + EventBridge) |
| 2 | SAM/IaC (waf-rag stack) |
| 13, 14, 15 | CI/CD (GitHub Actions, static frontend only) |

### Architecture Pattern Evolution
| Pattern | Projects |
|---------|----------|
| Sync request-response (API Gateway → Lambda → AI) | 1 |
| RAG (API Gateway → Lambda → Embeddings → S3 cosine similarity → Nova Lite) | 2 |
| Sync request-response (Function URL → Lambda → AWS service) | 3 |
| Async event-driven (Function URL → S3 → Lambda → AI → S3, frontend polls) | 4, 5, 8 |
| Async queue-based (API Gateway → SQS → Lambda → AI → DynamoDB, frontend polls) | 7 |
| Scheduled agent (EventBridge → Lambda chain → SES email) | 6 |
| Orchestrated pipeline (EventBridge → Lambda → Step Functions → AI → DynamoDB) | 9 |
| Sync request-response (Function URL → Lambda → Bedrock) | 10, 11, 12 |
| Static client-side (S3 + CloudFront, no backend) | 13, 14, 15 |

### AI Services Used
| Service | Projects |
|---------|----------|
| Bedrock Nova Lite | 1, 2, 4, 6, 7, 8, 9, 10, 11, 12 |
| Bedrock Titan Embeddings V2 | 2 |
| AWS Translate | 3 |
| Amazon Polly | 5 |
| AWS Textract | 4, 5 |

### All Projects Live At
https://ai.rus-teston.com (CloudFront CDN + HTTPS)

### Frontend Features (March 25, 2026 onward)
- All project pages have clickable project summary modals
- Light theme modal (Projects 1, 3, 4, 5, 8) — white background, blue headings
- Dark theme modal (Projects 6, 7, 9–15) — dark background, theme-matching accents
- Projects 11–15 use yellow "New" tile styling on landing page
- Project 9: Restore Healthy button clears AI verdict and incident timeline

---

*This document provides a complete reference for all projects built in AI Project: Lone Star.*
