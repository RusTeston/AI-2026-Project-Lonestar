# Project 4: Document Intelligence - Well-Architected Production Design

**Document Created**: March 19, 2026
**Author**: Rus Teston
**Status**: Reference Architecture (Not Deployed)

---

## Overview

This document outlines how the Document Intelligence Pipeline would be designed and deployed in a true production environment following the **AWS Well-Architected Framework**. The current implementation is a functional demo; this document describes the enterprise-grade version suitable for internal employee use.

---

## Current Architecture (Demo)

| Component | Current Implementation |
|-----------|----------------------|
| Frontend | S3 static website (HTTP) |
| API | Lambda Function URL - no auth |
| Compute | 2 Lambda functions (API + Processor) |
| OCR | AWS Textract (text extraction) |
| AI Analysis | Bedrock Nova Lite (document classification & summarization) |
| Storage | S3 bucket (uploads/ and results/) |
| Auth | None - open to public |
| IaC | Bash deploy script |
| Monitoring | CloudWatch Logs only |
| CDN/HTTPS | None |

---

## Production Architecture by Well-Architected Pillar

### 1. Operational Excellence

**Principle**: Run and monitor systems to deliver business value and continually improve processes.

| Area | Production Design | Reasoning |
|------|------------------|-----------|
| **Infrastructure as Code** | AWS SAM template defining both Lambdas, S3 bucket, IAM roles, event notifications, and monitoring in a single stack | Repeatable deployments, version-controlled, rollback capable |
| **CI/CD Pipeline** | CodePipeline triggered by GitHub commits → CodeBuild → SAM deploy | Eliminates manual deployment errors, enables automated testing |
| **Structured Logging** | Lambda Powertools for Python with correlation IDs linking API request to processor execution | Enables end-to-end request tracing across both Lambda functions |
| **Monitoring Dashboard** | CloudWatch dashboard with widgets for: upload count, processing success/failure rate, Textract/Bedrock latency, document types processed | Operational visibility into the full pipeline |
| **Alerting** | CloudWatch Alarms → SNS notifications for: processor error rate > 10%, processing time > 45s, daily upload volume threshold | Proactive issue detection |

### 2. Security

**Principle**: Protect information, systems, and assets through risk assessments and mitigation strategies.

| Area | Production Design | Reasoning |
|------|------------------|-----------|
| **Authentication** | Amazon Cognito User Pool with employee email domain restriction | Only authorized employees can upload documents |
| **Authorization** | API Gateway with Cognito Authorizer replacing Function URL | Every upload request verified against valid session token |
| **CORS Policy** | Locked to specific domain | Prevents cross-origin abuse |
| **WAF** | AWS WAF with rate limiting (20 uploads/min per IP), file size limits, known bad IP blocking | Protects against abuse and excessive Textract/Bedrock charges |
| **IAM Least Privilege** | Separate IAM roles per Lambda: API role (S3 read/write only), Processor role (S3 read/write, Textract, Bedrock) | Each function has only the permissions it needs |
| **Encryption in Transit** | CloudFront with TLS 1.2+ enforced | All data encrypted between client and server |
| **Encryption at Rest** | S3 bucket encryption (SSE-S3), S3 lifecycle policy to auto-delete uploads after 24 hours | Protects stored documents; sensitive documents not retained |
| **Input Validation** | API Lambda validates file type (PDF/PNG/JPEG only), file size (max 10MB), filename sanitization | Prevents malicious file uploads |
| **Document Privacy** | S3 lifecycle policy deletes uploads and results after 24 hours; no long-term document retention | Sensitive business documents not stored permanently |

### 3. Reliability

**Principle**: Ensure a workload performs its intended function correctly and consistently.

| Area | Production Design | Reasoning |
|------|------------------|-----------|
| **Dead Letter Queue** | SQS DLQ attached to Processor Lambda for failed S3 event invocations | Failed document processing captured for retry or investigation |
| **Retry Logic** | Textract and Bedrock calls wrapped with exponential backoff (3 retries) | Handles transient service throttling gracefully |
| **Error Handling** | User-friendly error messages for known failures (UnsupportedDocumentException, file too large, encrypted PDF) | Users understand what went wrong and how to fix it |
| **Timeout Configuration** | Processor Lambda: 60s timeout (sufficient for Textract + Bedrock); API Lambda: 30s | Prevents hung invocations while allowing adequate processing time |
| **S3 Event Reliability** | S3 event notifications with DLQ ensure no uploads are missed | Documents always get processed even during transient failures |

### 4. Performance Efficiency

**Principle**: Use computing resources efficiently to meet system requirements and maintain efficiency as demand changes.

| Area | Production Design | Reasoning |
|------|------------------|-----------|
| **CloudFront CDN** | CloudFront distribution in front of S3 for frontend assets | Sub-100ms load times globally, HTTPS, caching |
| **Lambda Memory** | API Lambda: 128MB (I/O proxy), Processor Lambda: 256MB (Textract + Bedrock processing) | Right-sized per function workload |
| **Async Processing** | Upload returns immediately; processing happens asynchronously via S3 trigger | Users don't wait for the full Textract + Bedrock pipeline |
| **Text Truncation** | First 4000 characters sent to Bedrock for analysis | Balances analysis quality with token cost and latency |
| **Connection Reuse** | All AWS clients initialized outside handler | Reuses TCP connections across warm invocations |

### 5. Cost Optimization

**Principle**: Avoid unnecessary costs and understand where money is being spent.

| Area | Production Design | Reasoning |
|------|------------------|-----------|
| **Usage Plans** | API Gateway usage plan with monthly quota (e.g., 5,000 documents/month) | Hard cap prevents runaway Textract and Bedrock costs |
| **Cost Alarms** | CloudWatch Billing alarm at $20/month threshold → SNS email alert | Early warning before costs spiral |
| **S3 Lifecycle** | Auto-delete uploads and results after 24 hours | Eliminates storage cost accumulation |
| **Bedrock Token Limits** | maxTokens: 1000, input capped at 4000 chars | Controls per-request Bedrock cost |
| **Textract Pricing** | ~$1.50 per 1000 pages for detect_document_text | Most cost-effective Textract API for text extraction |
| **Estimated Monthly Cost** | ~$5-10/month for moderate usage (100 documents/day) | Textract (~$4.50), Bedrock (~$3), Lambda/S3 (~$1) |

### 6. Sustainability

**Principle**: Minimize environmental impact of running cloud workloads.

| Area | Production Design | Reasoning |
|------|------------------|-----------|
| **Serverless Architecture** | Lambda + S3 (no idle resources) | Zero compute when not in use |
| **Event-Driven Processing** | S3 trigger invokes processor only when needed | No polling or idle compute |
| **Auto-Cleanup** | S3 lifecycle deletes temporary files | No unnecessary storage accumulation |
| **Right-Sized Functions** | Each Lambda sized to its specific workload | Lower energy consumption per invocation |

---

## Key Differences: Demo vs Production

| Aspect | Demo (Current) | Production (Proposed) |
|--------|---------------|----------------------|
| Authentication | None | Cognito + JWT |
| HTTPS | No (HTTP S3) | Yes (CloudFront + ACM) |
| API | Lambda Function URL | API Gateway + Cognito Authorizer |
| Firewall | None | WAF with rate limiting |
| Deployment | Bash script | SAM + CI/CD pipeline |
| Monitoring | Basic logs | Dashboard + alarms + SNS |
| Error Handling | Basic UnsupportedDoc check | DLQ + retries + comprehensive error messages |
| Document Retention | Indefinite | 24-hour auto-delete lifecycle |
| Cost Controls | None | Usage plans + billing alarms |
| CORS | Open (`*`) | Domain-restricted |
| IaC | None | Full SAM template |

---

## Architecture Diagram

See the production architecture diagram: [Project 4 - Well-Architected Production Design](project-4-well-architected.png)

---

*This document demonstrates understanding of the AWS Well-Architected Framework applied to a real-world serverless document processing pipeline. The current demo proves functionality; this design proves production readiness.*
