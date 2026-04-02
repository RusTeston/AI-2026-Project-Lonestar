# Project 10: Perfect Prompt Builder — Well-Architected Design

## Operational Excellence
- **Static frontend on S3** — no server management, no patching, no scaling configuration
- **CloudFront CDN** — global edge caching with automatic HTTPS and security headers
- **CI/CD via GitHub Actions** — auto-deploy on push to main, CloudFront invalidation included
- **Structured form design** — guides users through prompt engineering best practices step by step

## Security
- **IAM least-privilege** — PromptBuilderRole has only Lambda basic execution + Bedrock invoke
- **Lambda Function URL CORS** — configured at the Function URL level, no duplicate headers
- **CloudFront security headers** — HSTS, CSP, X-Frame-Options, XSS Protection, Content-Type-Options
- **TLS 1.2+** — enforced on CloudFront distribution
- **No data persistence** — prompts are processed in memory, nothing stored

## Reliability
- **Serverless compute** — Lambda handles scaling automatically, no capacity planning
- **Managed AI inference** — Bedrock Nova Lite is a fully managed service with built-in availability
- **Graceful degradation** — Generate Prompt works without AI; Enhance with AI is optional
- **Error handling** — Lambda returns structured error responses, frontend displays user-friendly messages

## Performance Efficiency
- **Lambda 256MB** — right-sized for Bedrock API calls
- **60-second timeout** — sufficient for Bedrock inference without over-provisioning
- **CloudFront edge caching** — static assets served from nearest edge location
- **Single-page frontend** — no external dependencies, fast initial load

## Cost Optimization
- **Lambda free tier** — 1M requests/month included
- **Bedrock Nova Lite** — lowest-cost Bedrock model, ~$0.01-0.05/month at demo scale
- **S3 static hosting** — pennies per month for storage
- **No idle costs** — serverless scales to zero when not in use
- **Estimated total: < $0.05/month**
