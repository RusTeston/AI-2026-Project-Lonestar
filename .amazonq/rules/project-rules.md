# AI-2026-Project-Lonestar Rules

## Project Standards
- Always follow the Deployment Discipline Agreement - require explicit "APPROVED TO PROCEED" before each phase
- Use Texas-themed UI (Blue #002868, White, Red #BF0A30) for all Lonestar projects
- AWS region: us-east-1, Account ID: 901779867920
- Lambda runtime: Python 3.12
- All projects use serverless architecture (Lambda + S3, no EC2)

## Deployment Patterns
- Frontend deploys to `s3://ai-2026-project-lonestar/projects/XX-name/`
- Always handle double-slash in rawPath from Lambda Function URLs
- Always base64 decode body from Lambda Function URL uploads

## Code Practices
- Bedrock model: us.amazon.nova-lite-v1:0 (Nova Lite)
- Keep responses minimal - don't be verbose
- Read existing project code for patterns before creating new projects
- Reference the follow-up doc at `documentation/FOLLOW-UP-ARCHITECTURE-SECURITY-IAC.md` for tracked improvements

## Safety
- Never deploy without explicit approval
- Always have a rollback plan
- Clean up test data from S3 after testing
- Back up current files before making UI changes
