# Follow-Up: Architecture, Security & IaC Improvements

**Created**: March 17, 2026
**Status**: TODO - To be addressed in a future session

---

## Areas to Address

### 1. Infrastructure as Code (IaC)
- Currently all projects deployed via bash scripts with raw AWS CLI commands
- Need to migrate to SAM, CloudFormation, or Terraform for reproducible, version-controlled infrastructure
- Would enable consistent tear-down and rebuild across all projects

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

### 4. CI/CD Pipeline
- Everything is manual deploy
- No automated testing or deployment pipeline

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
- Project 6: Superhero Transformer
- Project 8: AI Log Analyzer

---

## Priority Recommendations
1. **SAM templates** - Proper IaC for all projects
2. **API throttling / WAF** - Protect against bill shock
3. **CloudWatch alarms** - Error rates and cost monitoring

---

## Follow-Up: Well-Architected Design & UI Rollout

**Added**: March 19, 2026

Apply the following to each project (one at a time):
- Create Well-Architected Design document (like Project 1)
- Create Well-Architected production architecture diagram
- Update header: move "Project X: Name" and "Powered by..." into header
- Update footer: bolder links (font-weight 600, 1rem, 2px blue top border), diagram/artifact links only
- Add Demo Diagram, WAF Design, and WAF Diagram links to footer
- Note: Project 6 still needs its base architecture diagram created

**Projects to update:**
- Project 1: AI Chatbot - ✅ COMPLETE
- Project 3: Language Translator - ✅ COMPLETE
- Project 4: Document Intelligence - ✅ COMPLETE
- Project 5: Text-to-Speech Reader - ✅ COMPLETE
- Project 6: Superhero Transformer - TODO
- Project 8: AI Log Analyzer - ✅ COMPLETE
