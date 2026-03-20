# Project 1: AI Chatbot - Well-Architected Production Design

**Document Created**: March 19, 2026
**Author**: Rus Teston
**Status**: Reference Architecture (Not Deployed)

---

## Overview

This document outlines how the AI Chatbot (Cloud Architecture Advisor) would be designed and deployed in a true production environment following the **AWS Well-Architected Framework**. The current implementation is a functional demo; this document describes the enterprise-grade version suitable for internal employee use.

---

## Current Architecture (Demo)

| Component | Current Implementation |
|-----------|----------------------|
| Frontend | S3 static website (HTTP) |
| API | API Gateway (REST) - no auth |
| Compute | Single Lambda function |
| AI Model | Bedrock Nova Lite |
| Auth | None - open to public |
| IaC | Bash scripts |
| Monitoring | CloudWatch Logs only |
| CDN/HTTPS | None |

---

## Production Architecture by Well-Architected Pillar

### 1. Operational Excellence

**Principle**: Run and monitor systems to deliver business value and continually improve processes.

| Area | Production Design | Reasoning |
|------|------------------|-----------|
| **Infrastructure as Code** | AWS SAM (Serverless Application Model) template defining all resources in a single stack | Repeatable deployments, version-controlled, peer-reviewable, rollback capable |
| **CI/CD Pipeline** | CodePipeline triggered by GitHub commits → CodeBuild → SAM deploy | Eliminates manual deployment errors, enables automated testing before production |
| **Structured Logging** | Lambda Powertools for Python with correlation IDs, JSON-formatted logs | Enables log aggregation, filtering, and tracing across requests |
| **Monitoring Dashboard** | CloudWatch dashboard with widgets for: invocation count, error rate, latency (p50/p90/p99), Bedrock token usage | Single pane of glass for operational health |
| **Alerting** | CloudWatch Alarms → SNS notifications for: error rate > 5%, latency p99 > 10s, 5xx responses, monthly cost threshold | Proactive issue detection before users report problems |
| **Runbooks** | Documented procedures for common operational tasks: deployment, rollback, log investigation, scaling | Reduces mean time to recovery (MTTR) |

### 2. Security

**Principle**: Protect information, systems, and assets through risk assessments and mitigation strategies.

| Area | Production Design | Reasoning |
|------|------------------|-----------|
| **Authentication** | Amazon Cognito User Pool with employee email domain restriction | Only authorized employees can access the chatbot; supports MFA |
| **Authorization** | Cognito Authorizer on API Gateway; JWT token validation | Every API request verified against valid session token |
| **CORS Policy** | Locked to specific domain (e.g., `https://chatbot.company.com`) | Prevents cross-origin abuse from unauthorized domains |
| **WAF** | AWS WAF on API Gateway with rate limiting rules (100 requests/min per IP), SQL injection protection, known bad IP blocking | Protects against DDoS, abuse, and injection attacks |
| **IAM Least Privilege** | Lambda role scoped to: specific Bedrock model ARN, CloudWatch Logs for its own log group only | Minimizes blast radius if credentials are compromised |
| **Encryption in Transit** | CloudFront with TLS 1.2+ enforced, HTTPS-only | All data encrypted between client and server |
| **Encryption at Rest** | S3 bucket encryption (SSE-S3), CloudWatch Logs encryption | Protects stored data |
| **Input Validation** | Lambda validates message length (max 2000 chars), sanitizes input before sending to Bedrock | Prevents prompt injection and excessive token consumption |
| **Secrets Management** | No hardcoded values; all configuration via environment variables and SSM Parameter Store | Credentials never in source code |

### 3. Reliability

**Principle**: Ensure a workload performs its intended function correctly and consistently.

| Area | Production Design | Reasoning |
|------|------------------|-----------|
| **Throttling** | API Gateway usage plan: 100 requests/second burst, 50 requests/second steady state | Prevents any single user or bot from overwhelming the system |
| **Dead Letter Queue** | SQS DLQ attached to Lambda for failed async invocations | Failed requests captured for investigation rather than silently lost |
| **Retry Logic** | Bedrock calls wrapped with exponential backoff (3 retries, 1s/2s/4s) | Handles transient Bedrock throttling or timeouts gracefully |
| **Health Check** | API Gateway `/health` endpoint returning Lambda + Bedrock connectivity status | Enables monitoring systems to detect outages |
| **Graceful Degradation** | If Bedrock is unavailable, return cached "service temporarily unavailable" message | Users get a clear message instead of a cryptic error |
| **Multi-AZ** | Lambda runs across multiple AZs by default | Built-in redundancy |

### 4. Performance Efficiency

**Principle**: Use computing resources efficiently to meet system requirements and maintain efficiency as demand changes.

| Area | Production Design | Reasoning |
|------|------------------|-----------|
| **CloudFront CDN** | CloudFront distribution in front of S3 for frontend assets | Sub-100ms load times globally, HTTPS, caching |
| **Lambda Memory** | 256MB (current) with performance testing to right-size | Bedrock API calls are I/O-bound, not CPU-bound; 256MB is likely optimal |
| **API Gateway Caching** | Optional: 5-minute cache on identical requests | Reduces Bedrock costs for repeated questions (trade-off: slightly stale responses) |
| **Lambda Provisioned Concurrency** | Not recommended unless cold start latency is unacceptable | Cold starts add ~1-2s on first request; Bedrock response time (3-8s) dominates total latency |
| **Connection Reuse** | Bedrock client initialized outside handler (already done) | Reuses TCP connections across warm invocations |

### 5. Cost Optimization

**Principle**: Avoid unnecessary costs and understand where money is being spent.

| Area | Production Design | Reasoning |
|------|------------------|-----------|
| **Usage Plans** | API Gateway usage plan with monthly quota (e.g., 10,000 requests/month) | Hard cap prevents runaway Bedrock costs |
| **Cost Alarms** | CloudWatch Billing alarm at $25/month threshold → SNS email alert | Early warning before costs spiral |
| **Bedrock Token Limits** | maxTokens set to 1000 in inference config; input capped at 2000 chars | Controls per-request cost |
| **S3 Lifecycle** | No lifecycle needed (static assets only, minimal storage) | Already cost-optimized |
| **Right-Sized Lambda** | 256MB memory, 30s timeout | Matches workload requirements without over-provisioning |
| **Estimated Monthly Cost** | ~$8-15/month for moderate usage (500 requests/day) | Cognito free tier (50K MAU), API Gateway ($3.50/million), Lambda ($0.20/million), Bedrock (~$5-10 for Nova Lite) |

### 6. Sustainability

**Principle**: Minimize environmental impact of running cloud workloads.

| Area | Production Design | Reasoning |
|------|------------------|-----------|
| **Serverless Architecture** | Lambda + API Gateway + S3 (no idle resources) | Zero compute when not in use; scales to zero automatically |
| **Right-Sized Responses** | System prompt limits response to 300-500 words | Reduces unnecessary token generation and compute |
| **CloudFront Caching** | Reduces origin requests for static assets | Fewer S3 reads, lower data transfer |
| **Region Selection** | us-east-1 (one of AWS's most energy-efficient regions) | Lower carbon footprint |

---

## Production Architecture Components

```
User (Browser)
  → CloudFront (HTTPS, CDN, caching)
    → S3 (static frontend assets, encrypted)

User (Browser)
  → CloudFront
    → WAF (rate limiting, IP filtering, injection protection)
      → API Gateway (REST API)
        → Cognito Authorizer (JWT validation)
          → Lambda (input validation, structured logging)
            → Bedrock Nova Lite (AI inference)

Lambda failures → SQS Dead Letter Queue
CloudWatch Logs → CloudWatch Dashboard → CloudWatch Alarms → SNS → Email
AWS SAM Template → CodePipeline → CodeBuild → Automated Deployment
```

---

## Key Differences: Demo vs Production

| Aspect | Demo (Current) | Production (Proposed) |
|--------|---------------|----------------------|
| Authentication | None | Cognito + JWT |
| HTTPS | No (HTTP S3) | Yes (CloudFront + ACM) |
| Firewall | None | WAF with rate limiting |
| Deployment | Bash scripts | SAM + CI/CD pipeline |
| Monitoring | Basic logs | Dashboard + alarms + SNS |
| Error Handling | Generic catch | DLQ + retries + graceful degradation |
| Input Validation | None | Length + sanitization |
| Cost Controls | None | Usage plans + billing alarms |
| CORS | Open (`*`) | Domain-restricted |
| IaC | None | Full SAM template |

---

## Architecture Diagram

See the production architecture diagram: [Project 1 - Well-Architected Production Design](project-1-well-architected.png)

---

*This document demonstrates understanding of the AWS Well-Architected Framework applied to a real-world serverless AI application. The current demo proves functionality; this design proves production readiness.*
