# Project 3: Language Translator - Well-Architected Production Design

**Document Created**: March 19, 2026
**Author**: Rus Teston
**Status**: Reference Architecture (Not Deployed)

---

## Overview

This document outlines how the Language Translator would be designed and deployed in a true production environment following the **AWS Well-Architected Framework**. The current implementation is a functional demo; this document describes the enterprise-grade version suitable for internal employee use.

---

## Current Architecture (Demo)

| Component | Current Implementation |
|-----------|----------------------|
| Frontend | S3 static website (HTTP) |
| API | Lambda Function URL - no auth |
| Compute | Single Lambda function |
| Translation | AWS Translate (75+ languages) |
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
| **Infrastructure as Code** | AWS SAM template defining Lambda, Function URL, IAM role, and monitoring in a single stack | Repeatable deployments, version-controlled, peer-reviewable, rollback capable |
| **CI/CD Pipeline** | CodePipeline triggered by GitHub commits → CodeBuild → SAM deploy | Eliminates manual deployment errors, enables automated testing before production |
| **Structured Logging** | Lambda Powertools for Python with correlation IDs, JSON-formatted logs including source/target language pairs and text length | Enables usage analytics and troubleshooting |
| **Monitoring Dashboard** | CloudWatch dashboard with widgets for: invocation count, error rate, latency, language pair usage, character volume | Single pane of glass for operational health and usage patterns |
| **Alerting** | CloudWatch Alarms → SNS notifications for: error rate > 5%, latency p99 > 5s, daily character volume threshold | Proactive issue detection and cost monitoring |

### 2. Security

**Principle**: Protect information, systems, and assets through risk assessments and mitigation strategies.

| Area | Production Design | Reasoning |
|------|------------------|-----------|
| **Authentication** | Amazon Cognito User Pool with employee email domain restriction | Only authorized employees can access the translator |
| **Authorization** | API Gateway with Cognito Authorizer replacing Function URL | Every request verified against valid session token |
| **CORS Policy** | Locked to specific domain (e.g., `https://translator.company.com`) | Prevents cross-origin abuse from unauthorized domains |
| **WAF** | AWS WAF with rate limiting (50 requests/min per IP), request body size limits, known bad IP blocking | Protects against abuse and excessive AWS Translate charges |
| **IAM Least Privilege** | Lambda role scoped to: translate:TranslateText only, CloudWatch Logs for its own log group | Minimizes blast radius if credentials are compromised |
| **Encryption in Transit** | CloudFront with TLS 1.2+ enforced, HTTPS-only | All data encrypted between client and server |
| **Encryption at Rest** | S3 bucket encryption (SSE-S3) | Protects stored frontend assets |
| **Input Validation** | Lambda validates text length (max 5000 chars), sanitizes input, validates language codes against allowed list | Prevents injection and excessive translation charges |
| **Data Privacy** | No translation content logged or stored; stateless processing only | Sensitive text never persisted |

### 3. Reliability

**Principle**: Ensure a workload performs its intended function correctly and consistently.

| Area | Production Design | Reasoning |
|------|------------------|-----------|
| **Throttling** | API Gateway usage plan: 50 requests/second burst, 20 requests/second steady state | Prevents any single user from overwhelming the system or running up costs |
| **Retry Logic** | AWS Translate calls wrapped with exponential backoff (3 retries, 1s/2s/4s) | Handles transient Translate service throttling gracefully |
| **Health Check** | API Gateway `/health` endpoint returning Lambda + Translate connectivity status | Enables monitoring systems to detect outages |
| **Graceful Degradation** | If Translate is unavailable, return clear "service temporarily unavailable" message | Users get a clear message instead of a cryptic error |
| **Multi-AZ** | Lambda runs across multiple AZs by default | Built-in redundancy |
| **Input Limits** | Enforce 5000 character limit on both frontend and backend | Prevents oversized requests from failing at the AWS Translate API |

### 4. Performance Efficiency

**Principle**: Use computing resources efficiently to meet system requirements and maintain efficiency as demand changes.

| Area | Production Design | Reasoning |
|------|------------------|-----------|
| **CloudFront CDN** | CloudFront distribution in front of S3 for frontend assets | Sub-100ms load times globally, HTTPS, caching |
| **Lambda Memory** | 128MB (current) - appropriate for I/O-bound Translate API calls | AWS Translate does the heavy lifting; Lambda just proxies the request |
| **Connection Reuse** | Translate client initialized outside handler (already done) | Reuses TCP connections across warm invocations |
| **Lambda Cold Start** | Minimal concern at 128MB with simple Python function | Cold start adds ~500ms; Translate response time (200-500ms) is the primary latency |

### 5. Cost Optimization

**Principle**: Avoid unnecessary costs and understand where money is being spent.

| Area | Production Design | Reasoning |
|------|------------------|-----------|
| **Usage Plans** | API Gateway usage plan with monthly quota (e.g., 500,000 characters/month) | Hard cap prevents runaway AWS Translate costs ($15/million characters) |
| **Cost Alarms** | CloudWatch Billing alarm at $15/month threshold → SNS email alert | Early warning before costs spiral |
| **Character Limits** | 5000 character max per request enforced at frontend and backend | Controls per-request cost |
| **Right-Sized Lambda** | 128MB memory, 30s timeout | Matches workload requirements without over-provisioning |
| **Estimated Monthly Cost** | ~$10-15/month for moderate usage (1000 translations/day) | Lambda ($0.20/million), Translate (~$7.50 for 500K chars), API Gateway ($3.50/million) |

### 6. Sustainability

**Principle**: Minimize environmental impact of running cloud workloads.

| Area | Production Design | Reasoning |
|------|------------------|-----------|
| **Serverless Architecture** | Lambda + S3 (no idle resources) | Zero compute when not in use; scales to zero automatically |
| **Right-Sized Lambda** | 128MB - minimum needed for this workload | Lower energy consumption per invocation |
| **CloudFront Caching** | Reduces origin requests for static assets | Fewer S3 reads, lower data transfer |
| **Stateless Design** | No database, no storage of translations | Minimal resource footprint |

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
| Error Handling | Generic catch | Retries + graceful degradation |
| Input Validation | Frontend only (5000 chars) | Frontend + backend validation |
| Cost Controls | None | Usage plans + billing alarms |
| CORS | Open (`*`) | Domain-restricted |
| Data Privacy | Not addressed | No content logging or storage |
| IaC | None | Full SAM template |

---

## Architecture Diagram

See the production architecture diagram: [Project 3 - Well-Architected Production Design](project-3-well-architected.png)

---

*This document demonstrates understanding of the AWS Well-Architected Framework applied to a real-world serverless translation application. The current demo proves functionality; this design proves production readiness.*
