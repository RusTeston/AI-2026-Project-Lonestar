# Follow-Up: Architecture, Security & IaC Improvements

**Created**: March 17, 2026
**Status**: TODO - To be addressed in a future session

---

## Areas to Address

### 1. Infrastructure as Code (IaC) - ✅ STARTED (March 21, 2026)
- ~~Currently all projects deployed via bash scripts with raw AWS CLI commands~~
- Project 06 (Cost Optimization Advisor) and Project 07 (Architecture Reviewer) deployed via SAM
- Remaining projects still use manual deployment — migrate over time

### 2. Security Hardening
- Lambda Function URLs use `AUTH_TYPE NONE` with `*` principal (open to internet)
- No API throttling or rate limiting (risk of bill shock from spam uploads)
- No input validation on file content in processor Lambdas (only extension checks)
- Project 8 Bedrock IAM uses `Resource: "*"` (needs scoping down)
- No encryption at rest specified on S3 buckets
- No VPC configuration

### 3. Monitoring & Alerting
- No CloudWatch alarms for errors, throttling, or cost spikes
- No dashboards for operational visibility

### 4. CI/CD Pipeline - ✅ IMPLEMENTED (March 20, 2026)
- ~~Everything is manual deploy~~ → GitHub Actions CI/CD deployed for both repos
- ~~No automated testing or deployment pipeline~~ → Auto-deploy on push to main
- GitHub repos: `RusTeston/AI-2026-Project-Lonestar` and `RusTeston/rus-portfolio-prod`
- OIDC federation (no stored AWS credentials)
- IAM Role: `GitHubActions-Deploy` scoped to specific repos and resources
- **Still TODO**: Add automated testing steps to workflows

### 5. High Availability & Fault Tolerance
- No retry logic or exponential backoff on AWS service calls
- No Dead Letter Queues (DLQ) for failed Lambda invocations
- No fallback handling when Bedrock or other services are unavailable

### 6. Code Quality & Modularity
- Single-file Lambda functions with no shared libraries
- No reusable utility modules across projects (e.g., error handling, response formatting)
- No unit tests or integration tests

### 7. Secure Data Handling
- No input schema validation beyond file extension checks
- No request body size limits enforced at application level
- No data sanitization on user-uploaded content before processing

---

## Affected Projects
- Project 1: AI Chatbot
- Project 3: Language Translator
- Project 4: Document Intelligence
- Project 5: Text-to-Speech Reader
- Project 6: ~~Superhero Transformer~~ Cost Optimization Advisor (replaced March 21, 2026)
- Project 7: Architecture Reviewer (added March 21, 2026)
- Project 8: AI Log Analyzer

---

## Priority Recommendations
1. **SAM templates** - Proper IaC for all projects
2. **API throttling / WAF** - Protect against bill shock
3. **CloudWatch alarms** - Error rates and cost monitoring
4. **Automated tests in CI/CD** - Add lint/test steps to GitHub Actions workflows

---

## Follow-Up: Well-Architected Design & UI Rollout

**Added**: March 19, 2026

Apply the following to each project (one at a time):
- Create Well-Architected Design document (like Project 1)
- Create Well-Architected production architecture diagram
- Update header: move "Project X: Name" and "Powered by..." into header
- Update footer: bolder links (font-weight 600, 1rem, 2px blue top border), diagram/artifact links only
- Footer link order: CI/CD Pipeline | Demo Diagram | WAF Design | WAF Diagram
- Note: Project 6 still needs its base architecture diagram, WAF docs, and CI/CD link

**Projects to update:**
- Project 1: AI Chatbot - ✅ COMPLETE
- Project 3: Language Translator - ✅ COMPLETE
- Project 4: Document Intelligence - ✅ COMPLETE
- Project 5: Text-to-Speech Reader - ✅ COMPLETE
- Project 6: Cost Optimization Advisor - ✅ COMPLETE (SAM/IaC, new project)
- Project 7: Architecture Reviewer - ✅ COMPLETE (SAM/IaC, new project)
- Project 8: AI Log Analyzer - ✅ COMPLETE

---

## CI/CD Pipeline Implementation

**Added**: March 20, 2026

### What Was Set Up
- **GitHub Repos**: Both projects pushed to public GitHub repos
  - https://github.com/RusTeston/AI-2026-Project-Lonestar
  - https://github.com/RusTeston/rus-portfolio-prod
- **OIDC Federation**: GitHub Actions authenticates to AWS via OIDC (no stored credentials)
- **IAM Role**: `GitHubActions-Deploy` with least-privilege permissions
  - S3: PutObject/GetObject/DeleteObject/ListBucket on both buckets
  - Lambda: UpdateFunctionCode in us-east-1
  - CloudFront: CreateInvalidation on distribution E3IA5ZUL2HT0NT
- **GitHub Actions Workflows**: Auto-deploy on push to main
  - rus-portfolio-prod: Syncs `live-site-html/` to S3, invalidates CloudFront
  - Lonestar: Deploys `website/` and `projects/*/frontend/` to S3
- **CI/CD Pipeline diagram**: Added to Projects 1, 3, 4, 5, 8 footers (end-to-end-deployment-flow.png)
- **Tested**: Both pipelines verified end-to-end

### Diagrams Created
- `generated-diagrams/github-actions-cicd-pipeline.png` - GitHub Actions workflow detail
- `generated-diagrams/end-to-end-deployment-flow.png` - Full flow from developer to customer
