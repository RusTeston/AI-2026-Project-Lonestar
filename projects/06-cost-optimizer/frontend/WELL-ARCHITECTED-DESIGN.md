# Project 06: AI-Powered Cost Optimization Advisor — Well-Architected Design

## Architecture Overview

Scheduled serverless agent that scans AWS account resources for cost waste, analyzes findings with Bedrock Nova Lite, and delivers a prioritized savings report via SES email. Also supports on-demand scans via API Gateway.

**Weekly Flow:** EventBridge Scheduler → Collect Lambda → S3 → Analyze Lambda (Bedrock) → S3 → Notify Lambda (SES)
**On-Demand Flow:** API Gateway → On-Demand Lambda (Collect + Analyze inline) → Frontend

## Pillar 1: Operational Excellence

| Principle | Implementation |
|-----------|---------------|
| IaC | SAM template defines all infrastructure (`template.yaml`) |
| Automation | EventBridge Scheduler triggers weekly scans automatically |
| Monitoring | CloudWatch Logs for all Lambda functions |
| Scheduled Operations | Cron-based scanning eliminates manual effort |

## Pillar 2: Security

| Principle | Implementation |
|-----------|---------------|
| Least Privilege | Read-only IAM for all AWS service scanning |
| Collect Function | Read-only: ce:GetCostAndUsage, ec2:Describe*, rds:Describe*, s3:List/Get, lambda:List/Get, cloudwatch:GetMetricStatistics |
| Analyze Function | S3 read/write + Bedrock invoke only |
| Notify Function | S3 read + SES send only |
| No Write Access | Scanning never modifies customer resources |
| No Secrets | IAM roles only, no hardcoded credentials |

## Pillar 3: Reliability

| Principle | Implementation |
|-----------|---------------|
| Chained Invocation | Collect → Analyze → Notify with async Lambda invoke |
| Error Handling | Each function handles errors independently |
| Scan Persistence | Raw findings and reports stored in S3 for audit |
| Graceful Degradation | Individual service scan failures don't block other scans |

## Pillar 4: Performance Efficiency

| Principle | Implementation |
|-----------|---------------|
| Right-Sizing | Collect/Analyze at 256MB, Notify at 128MB |
| On-Demand Path | Inline analysis for immediate frontend results |
| Scheduled Path | Async chain for weekly digest (no time pressure) |
| Model Choice | Nova Lite balances quality and speed |

## Pillar 5: Cost Optimization

| Principle | Implementation |
|-----------|---------------|
| Pay-per-Use | All serverless — zero cost at idle |
| S3 Lifecycle | Reports auto-deleted after 30 days |
| Weekly Schedule | Minimal API calls (once per week) |
| Cost Explorer | $0.01/request × 4/month = $0.04/month |
| SES Free Tier | 62,000 emails/month included |
| Lambda Free Tier | 1M invocations/month included |

## Pillar 6: Sustainability

| Principle | Implementation |
|-----------|---------------|
| Managed Services | S3, SES, EventBridge, Lambda — no servers |
| Auto-Cleanup | S3 lifecycle removes stale reports |
| Efficient Scanning | Targeted API calls, not full account enumeration |

## Infrastructure (SAM-Deployed)

- **EventBridge Scheduler**: Weekly cron (Mondays 8 AM UTC)
- **API Gateway**: REST API for on-demand scans
- **S3 Bucket**: Report storage with 30-day lifecycle
- **Lambda Functions**: 4 functions (Collect, Analyze, Notify, On-Demand)
- **SES**: Email delivery for weekly digest
- **Bedrock**: Nova Lite (`us.amazon.nova-lite-v1:0`)
- **IAM**: Read-only cross-service policies
