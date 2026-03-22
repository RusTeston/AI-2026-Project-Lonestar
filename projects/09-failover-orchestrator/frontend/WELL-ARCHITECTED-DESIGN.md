# Project 09: Failover Orchestrator — Well-Architected Design

## Operational Excellence
- **Step Functions orchestration** provides visible, auditable workflow execution with built-in state tracking
- **EventBridge scheduled health checks** (every 2 min) ensure continuous monitoring without manual intervention
- **DynamoDB incident history** with TTL provides automatic cleanup of stale records
- **Structured incident timeline** captures every failover step with timestamps for post-incident review

## Security
- **IAM least-privilege roles** — each Lambda has only the permissions it needs (DynamoDB read vs CRUD, Bedrock invoke)
- **API Gateway CORS** restricts cross-origin access
- **No stored credentials** — Slack webhook URL passed as environment variable via SAM parameter
- **Simulated failover actions** prevent accidental infrastructure changes during demos

## Reliability
- **AI-powered decision gate** — Bedrock Nova Lite reasons over 5-check evidence window to prevent false-positive failovers
- **Step Functions conditional branching** — only executes failover when AI confidence is "high"
- **Health check pattern** — 2-minute intervals with latency tracking detect both outages and degradation
- **DynamoDB on-demand** — no capacity planning needed, scales automatically

## Performance Efficiency
- **Serverless compute** — all Lambda functions, no idle resources
- **Step Functions Standard** — appropriate for low-frequency, long-running orchestration workflows
- **DynamoDB single-table design** — pk/sk pattern minimizes table count and query complexity
- **Bedrock inference** — low-latency AI reasoning without managing ML infrastructure

## Cost Optimization
- **Lambda free tier** — health checks and API handlers well within 1M requests/month
- **Step Functions free tier** — 4,000 state transitions/month covers demo usage
- **EventBridge Scheduler** — free
- **DynamoDB on-demand** — pay only for actual reads/writes (pennies at demo scale)
- **Bedrock Nova Lite** — minimal cost per inference (~$0.01-0.05/month)
- **24h/7d TTL** on records prevents unbounded storage growth
- **Estimated total: $1-2/month**
