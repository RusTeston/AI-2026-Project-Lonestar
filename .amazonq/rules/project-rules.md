# AI-2026-Project-Lonestar Rules

## Project Standards
- Always follow the Deployment Discipline Agreement - require explicit "APPROVED TO PROCEED" before each phase
- Use dark modern theme (navy gradient, Inter font, white/light blue text) for all Lonestar projects
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

## Deployment Discipline
<!-- See rus-portfolio-prod/documentation/migration-reports/DEPLOYMENT-DISCIPLINE-AGREEMENT.md -->
- Minor changes (comments, text edits, doc updates, small fixes): proceed efficiently with approval
- Major changes (new pages, rewrites, new infrastructure, new projects): follow full Deployment Discipline Agreement
  - Propose → Review → Test Plan → Rollback Plan → "APPROVED TO PROCEED" → Execute → Validate → Document
  - Create mockup/preview before deploying to production
- After confirming changes are working, always commit and push to GitHub before moving to the next task

## Safety
- Preview HTML changes locally (open in browser) before deploying to S3
- Never deploy without explicit approval
- Always have a rollback plan
- Clean up test data from S3 after testing
- Back up current files before making UI changes
- Before any CI/CD workflow that syncs or deletes from S3, compare S3 contents against local files and download any S3-only files first
- Never use `--delete` flag on S3 sync without first verifying all S3 assets exist locally

## Architecture Catalog — Project 13 Quality Standards

### MANDATORY process for EVERY architecture (all 24 diagrams):

**STEP 1 — RESEARCH FIRST**
- Use the `search_documentation` tool to search AWS documentation for the specific architecture pattern
- Cross-reference AWS Well-Architected Framework guidance where applicable
- Identify the current recommended services, patterns, and approaches per AWS documentation
- Do NOT skip this step under any circumstances

**STEP 2 — VERIFY & UPDATE HTML**
- Compare the existing description, service list, and flow steps against what AWS documentation says
- Update anything that is outdated, missing, imprecise, or not reflective of current AWS best practice
- Present ALL changes to Rus for review and explicit approval before proceeding
- Do NOT proceed to diagram until Rus says "Approved"

**STEP 3 — DIAGRAM ONLY AFTER APPROVAL**
- Generate the PNG only after Rus has explicitly approved the updated description
- Diagram must exactly match the approved description — every service in the description must appear as a node
- Use proper clusters, left-to-right flow, and complete end-to-end path
- High fidelity standard: no sparse diagrams, no missing services, no generic labels

**STEP 4 — DEPLOY AFTER EACH**
- Copy PNG to `website/projects/13-architecture-catalog/images/{slug}.png`
- S3 sync → CloudFront invalidation → git commit and push
- One architecture fully complete before moving to the next

### Quality reminder phrase
If Rus says **"High fidelity standard"** — stop, re-research, re-verify, re-draw to full quality.

### Interview context
Rus is demoing Project 13 to an AWS SA Manager. Every description and diagram must reflect the latest AWS recommended architecture and best practices. There is no room for outdated, generic, or incomplete content.
