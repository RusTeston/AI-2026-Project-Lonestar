# Project 8: AI Log Analyzer - Well-Architected Production Design

**Document Created**: March 19, 2026
**Author**: Rus Teston
**Status**: Reference Architecture (Not Deployed)

---

## Overview

This document outlines how the AI Log Analyzer would be designed and deployed in a true production environment following the **AWS Well-Architected Framework**. The current implementation is a functional demo; this document describes the enterprise-grade version suitable for internal employee use.

---

## Current Architecture (Demo)

| Component | Current Implementation |
|-----------|----------------------|
| Frontend | S3 static website (HTTP) |
| API | Lambda Function URL - no auth |
| Compute | 2 Lambda functions (API + Processor) |
| AI Analysis | Bedrock Nova Lite (log analysis, root cause, recommendations) |
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
| **Structured Logging** | Lambda Powertools for Python with correlation IDs, log file metadata (size, type, severity) logged per request | Enables usage analytics and troubleshooting |
| **Monitoring Dashboard** | CloudWatch dashboard with widgets for: analysis count, success/failure rate, Bedrock latency, severity distribution, average log file size | Operational visibility and usage insights |
| **Alerting** | CloudWatch Alarms → SNS notifications for: processor error rate > 10%, Bedrock throttling, daily analysis volume threshold | Proactive issue detection and cost monitoring |

### 2. Security

**Principle**: Protect information, systems, and assets through risk assessments and mitigation strategies.

| Area | Production Design | Reasoning |
|------|------------------|-----------|
| **Authentication** | Amazon Cognito User Pool with employee email domain restriction | Only authorized employees can upload log files |
| **Authorization** | API Gateway with Cognito Authorizer replacing Function URL | Every request verified against valid session token |
| **CORS Policy** | Locked to specific domain | Prevents cross-origin abuse |
| **WAF** | AWS WAF with rate limiting (20 uploads/min per IP), request body size limits (5MB), known bad IP blocking | Protects against abuse and excessive Bedrock charges |
| **IAM Least Privilege** | Separate IAM roles per Lambda: API role (S3 read/write), Processor role (S3 read/write, Bedrock scoped to Nova Lite model) | Each function has only the permissions it needs; Bedrock resource no longer wildcard |
| **Encryption in Transit** | CloudFront with TLS 1.2+ enforced | All data encrypted between client and server |
| **Encryption at Rest** | S3 bucket encryption (SSE-S3) | Protects stored log files |
| **Input Validation** | API Lambda validates file type (LOG/TXT/CSV/JSON only), file size (max 5MB), filename sanitization | Prevents malicious file uploads |
| **Log File Privacy** | S3 lifecycle policy deletes uploads and results after 24 hours; no long-term log retention | Sensitive log data (may contain IPs, credentials, internal paths) not stored permanently |
| **Content Sanitization** | Processor truncates log content to 15,000 chars before sending to Bedrock | Limits data exposure to AI model |

### 3. Reliability

**Principle**: Ensure a workload performs its intended function correctly and consistently.

| Area | Production Design | Reasoning |
|------|------------------|-----------|
| **Dead Letter Queue** | SQS DLQ attached to Processor Lambda for failed S3 event invocations | Failed analyses captured for retry or investigation |
| **Retry Logic** | Bedrock calls wrapped with exponential backoff (3 retries, 1s/2s/4s) | Handles transient Bedrock throttling gracefully |
| **Error Handling** | User-friendly error messages for: unsupported file type, empty file, Bedrock timeout, malformed log content | Users understand what went wrong |
| **Timeout Configuration** | Processor Lambda: 60s (sufficient for Bedrock analysis); API Lambda: 30s | Prevents hung invocations while allowing adequate analysis time |
| **JSON Parse Fallback** | If Bedrock returns malformed JSON, return structured "unable to analyze" response instead of crashing | Graceful degradation when AI output is unexpected |

### 4. Performance Efficiency

**Principle**: Use computing resources efficiently to meet system requirements and maintain efficiency as demand changes.

| Area | Production Design | Reasoning |
|------|------------------|-----------|
| **CloudFront CDN** | CloudFront distribution in front of S3 for frontend assets | Sub-100ms load times globally, HTTPS, caching |
| **Lambda Memory** | API Lambda: 128MB (I/O proxy), Processor Lambda: 256MB (Bedrock processing) | Right-sized per function workload |
| **Async Processing** | Upload returns immediately; processing happens asynchronously via S3 trigger | Users don't wait for the full Bedrock analysis |
| **Log Truncation** | First 15,000 characters sent to Bedrock | Balances analysis thoroughness with token cost and latency |
| **Bedrock Config** | temperature: 0.3, maxTokens: 4000 | Low temperature for consistent analysis; sufficient tokens for detailed output |
| **Connection Reuse** | All AWS clients initialized outside handler | Reuses TCP connections across warm invocations |

### 5. Cost Optimization

**Principle**: Avoid unnecessary costs and understand where money is being spent.

| Area | Production Design | Reasoning |
|------|------------------|-----------|
| **Usage Plans** | API Gateway usage plan with monthly quota (e.g., 5,000 analyses/month) | Hard cap prevents runaway Bedrock costs |
| **Cost Alarms** | CloudWatch Billing alarm at $15/month threshold → SNS email alert | Early warning before costs spiral |
| **Token Limits** | maxTokens: 4000 output, input capped at 15,000 chars | Controls per-request Bedrock cost |
| **S3 Lifecycle** | Auto-delete uploads and results after 24 hours | Eliminates storage cost accumulation |
| **Right-Sized Lambda** | API: 128MB/30s, Processor: 256MB/60s | Matches workload requirements without over-provisioning |
| **Estimated Monthly Cost** | ~$8-12/month for moderate usage (100 analyses/day) | Bedrock (~$6-8), Lambda/S3 (~$1-2) |

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
| Error Handling | Basic catch | DLQ + retries + user-friendly messages |
| Bedrock IAM | Resource: `*` | Scoped to specific model ARN |
| Log Retention | Indefinite | 24-hour auto-delete lifecycle |
| Cost Controls | None | Usage plans + billing alarms |
| CORS | Open (`*`) | Domain-restricted |
| IaC | None | Full SAM template |

---

## Architecture Diagram

See the production architecture diagram: [Project 8 - Well-Architected Production Design](project-8-well-architected.png)

---

*This document demonstrates understanding of the AWS Well-Architected Framework applied to a real-world serverless log analysis application. The current demo proves functionality; this design proves production readiness.*
