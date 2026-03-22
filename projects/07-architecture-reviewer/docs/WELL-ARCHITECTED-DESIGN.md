# Project 07: Intelligent AWS Architecture Reviewer — Well-Architected Design

## Architecture Overview

Async serverless pipeline that accepts CloudFormation/SAM templates, analyzes them against the AWS Well-Architected Framework using Amazon Bedrock (Nova Lite), and returns prioritized findings.

**Flow:** API Gateway → Ingest Lambda → S3 + SQS → Analyze Lambda (Bedrock) → DynamoDB → Results Lambda → API Gateway

## Pillar 1: Operational Excellence

| Principle | Implementation |
|-----------|---------------|
| IaC | SAM template defines all infrastructure (`template.yaml`) |
| Automation | SAM CLI for build/deploy, GitHub Actions CI/CD |
| Monitoring | CloudWatch Logs auto-enabled for all Lambda functions |
| Observability | SQS metrics for queue depth, DynamoDB metrics for read/write |

## Pillar 2: Security

| Principle | Implementation |
|-----------|---------------|
| Least Privilege | SAM policy templates scope each function to only required actions |
| Ingest Function | S3 write + SQS send only |
| Analyze Function | S3 read + DynamoDB write + Bedrock invoke only |
| Results Function | DynamoDB read only |
| Input Validation | Template size limit (50KB), JSON validation |
| No Secrets | No hardcoded credentials; IAM roles only |
| CORS | Configured at API Gateway level |

## Pillar 3: Reliability

| Principle | Implementation |
|-----------|---------------|
| Async Decoupling | SQS queue buffers between ingest and analysis |
| Retry | SQS automatic retry on Lambda failure |
| Error Handling | Failed analyses recorded in DynamoDB with error details |
| Timeout | Analyze function has 300s timeout for Bedrock calls |
| Polling | Frontend polls with 60-attempt max (3-minute timeout) |

## Pillar 4: Performance Efficiency

| Principle | Implementation |
|-----------|---------------|
| Right-Sizing | Ingest/Results at 128MB, Analyze at 256MB (Bedrock needs more) |
| Async Processing | User gets immediate jobId response, no blocking |
| Batch Size | SQS batch size of 1 for predictable processing |
| Model Choice | Nova Lite balances quality and speed |

## Pillar 5: Cost Optimization

| Principle | Implementation |
|-----------|---------------|
| Pay-per-Use | All serverless — zero cost at idle |
| S3 Lifecycle | Templates auto-deleted after 7 days |
| DynamoDB On-Demand | No provisioned capacity — pay per read/write |
| SQS Free Tier | 1M requests/month included |
| Lambda Free Tier | 1M invocations/month included |
| Right-Sized Memory | Minimal memory allocations per function |

## Pillar 6: Sustainability

| Principle | Implementation |
|-----------|---------------|
| Managed Services | S3, SQS, DynamoDB, Lambda — no servers to manage |
| Auto-Cleanup | S3 lifecycle removes stale data automatically |
| Efficient Processing | Single Bedrock call per analysis, structured prompt |

## Infrastructure (SAM-Deployed)

- **API Gateway**: REST API with CORS (implicit from SAM)
- **S3 Bucket**: Template storage with 7-day lifecycle
- **SQS Queue**: Analysis buffer with 300s visibility timeout
- **DynamoDB Table**: On-demand, keyed by jobId
- **Lambda Functions**: 3 functions (Ingest, Analyze, Results)
- **Bedrock**: Nova Lite (`us.amazon.nova-lite-v1:0`)
- **IAM**: SAM-managed roles with policy templates
