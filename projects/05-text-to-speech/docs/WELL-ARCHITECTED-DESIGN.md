# Project 5: Text-to-Speech Reader - Well-Architected Production Design

**Document Created**: March 19, 2026
**Author**: Rus Teston
**Status**: Reference Architecture (Not Deployed)

---

## Overview

This document outlines how the Text-to-Speech Reader would be designed and deployed in a true production environment following the **AWS Well-Architected Framework**. The current implementation is a functional demo; this document describes the enterprise-grade version suitable for internal employee use.

---

## Current Architecture (Demo)

| Component | Current Implementation |
|-----------|----------------------|
| Frontend | S3 static website (HTTP) |
| API | Lambda Function URL - no auth |
| Compute | 2 Lambda functions (API + Processor) |
| Speech Synthesis | Amazon Polly (Standard + Neural voices) |
| PDF Text Extraction | AWS Textract |
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
| **Structured Logging** | Lambda Powertools for Python with correlation IDs, voice engine/voice ID logged per request | Enables usage analytics (most popular voices, average text length) |
| **Monitoring Dashboard** | CloudWatch dashboard with widgets for: conversion count, success/failure rate, Polly latency, voice usage breakdown, character volume | Operational visibility and usage insights |
| **Alerting** | CloudWatch Alarms → SNS notifications for: processor error rate > 10%, daily character volume threshold, Polly throttling events | Proactive issue detection and cost monitoring |

### 2. Security

**Principle**: Protect information, systems, and assets through risk assessments and mitigation strategies.

| Area | Production Design | Reasoning |
|------|------------------|-----------|
| **Authentication** | Amazon Cognito User Pool with employee email domain restriction | Only authorized employees can convert documents |
| **Authorization** | API Gateway with Cognito Authorizer replacing Function URL | Every request verified against valid session token |
| **CORS Policy** | Locked to specific domain | Prevents cross-origin abuse |
| **WAF** | AWS WAF with rate limiting (30 conversions/min per IP), request body size limits | Protects against abuse and excessive Polly charges |
| **IAM Least Privilege** | Separate IAM roles per Lambda: API role (S3 read/write), Processor role (S3 read/write, Polly, Textract) | Each function has only the permissions it needs |
| **Encryption in Transit** | CloudFront with TLS 1.2+ enforced | All data encrypted between client and server |
| **Encryption at Rest** | S3 bucket encryption (SSE-S3) | Protects stored files and generated audio |
| **Input Validation** | API Lambda validates file type (TXT/PDF only), file size, filename sanitization | Prevents malicious file uploads |
| **Audio File Access** | Presigned URLs with 1-hour expiration for audio downloads instead of public S3 URLs | Audio files not permanently publicly accessible |
| **Content Cleanup** | S3 lifecycle policy deletes uploads and results after 24 hours | Uploaded documents and generated audio not retained long-term |

### 3. Reliability

**Principle**: Ensure a workload performs its intended function correctly and consistently.

| Area | Production Design | Reasoning |
|------|------------------|-----------|
| **Dead Letter Queue** | SQS DLQ attached to Processor Lambda for failed S3 event invocations | Failed conversions captured for retry or investigation |
| **Retry Logic** | Polly and Textract calls wrapped with exponential backoff (3 retries) | Handles transient service throttling gracefully |
| **Error Handling** | User-friendly error messages for: unsupported PDF, empty text, Polly character limit exceeded | Users understand what went wrong |
| **Timeout Configuration** | Processor Lambda: 60s (sufficient for Textract + Polly); API Lambda: 30s | Prevents hung invocations |
| **Character Limit Handling** | Clear warning when text is truncated to 3000 characters (already implemented) | Users know their content was shortened |

### 4. Performance Efficiency

**Principle**: Use computing resources efficiently to meet system requirements and maintain efficiency as demand changes.

| Area | Production Design | Reasoning |
|------|------------------|-----------|
| **CloudFront CDN** | CloudFront distribution in front of S3 for frontend assets | Sub-100ms load times globally, HTTPS, caching |
| **Lambda Memory** | API Lambda: 128MB (I/O proxy), Processor Lambda: 256MB (Textract + Polly processing) | Right-sized per function workload |
| **Async Processing** | Upload returns immediately; processing happens asynchronously via S3 trigger | Users don't wait for the full pipeline |
| **Neural vs Standard** | Both voice engines available; Neural for quality, Standard for speed | Users choose the trade-off that fits their needs |
| **Connection Reuse** | All AWS clients initialized outside handler | Reuses TCP connections across warm invocations |

### 5. Cost Optimization

**Principle**: Avoid unnecessary costs and understand where money is being spent.

| Area | Production Design | Reasoning |
|------|------------------|-----------|
| **Usage Plans** | API Gateway usage plan with monthly quota (e.g., 1,000,000 characters/month) | Hard cap prevents runaway Polly costs |
| **Cost Alarms** | CloudWatch Billing alarm at $15/month threshold → SNS email alert | Early warning before costs spiral |
| **Character Limits** | 3000 character max per request (Polly limit, already enforced) | Controls per-request cost |
| **S3 Lifecycle** | Auto-delete uploads and audio files after 24 hours | Eliminates storage cost accumulation |
| **Polly Pricing Awareness** | Standard: $4/million chars, Neural: $16/million chars; default to Standard for cost-sensitive deployments | Users informed of cost difference between engines |
| **Estimated Monthly Cost** | ~$8-12/month for moderate usage (200 conversions/day) | Polly (~$5-8), Lambda/S3 (~$1), Textract (~$1 for PDFs) |

### 6. Sustainability

**Principle**: Minimize environmental impact of running cloud workloads.

| Area | Production Design | Reasoning |
|------|------------------|-----------|
| **Serverless Architecture** | Lambda + S3 (no idle resources) | Zero compute when not in use |
| **Event-Driven Processing** | S3 trigger invokes processor only when needed | No polling or idle compute |
| **Auto-Cleanup** | S3 lifecycle deletes temporary files and audio | No unnecessary storage accumulation |
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
| Audio Access | Public S3 URL | Presigned URLs (1hr expiration) |
| File Retention | Indefinite | 24-hour auto-delete lifecycle |
| Cost Controls | None | Usage plans + billing alarms |
| CORS | Open (`*`) | Domain-restricted |
| IaC | None | Full SAM template |

---

## Architecture Diagram

See the production architecture diagram: [Project 5 - Well-Architected Production Design](project-5-well-architected.png)

---

*This document demonstrates understanding of the AWS Well-Architected Framework applied to a real-world serverless text-to-speech application. The current demo proves functionality; this design proves production readiness.*
