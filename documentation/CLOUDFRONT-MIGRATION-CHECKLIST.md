# CloudFront Migration Checklist — Project Lonestar

**Goal**: Serve ai-2026-project-lonestar via CloudFront + HTTPS at `https://ai.rus-teston.com`  
**Created**: March 22, 2026  
**Status**: IN PROGRESS

---

## Phase 1: CloudFront + SSL Setup ✅ COMPLETE
- [x] Request ACM certificate for `ai.rus-teston.com` (us-east-1) — `arn:aws:acm:us-east-1:901779867920:certificate/44d125cf-bff3-4651-bd17-7b553a05be4c`
- [x] Validate certificate via Route 53 DNS
- [x] Create CloudFront distribution pointing to `ai-2026-project-lonestar` S3 bucket — `E6LY7PZWUOBBP` (`d309r1vnuulj1s.cloudfront.net`)
- [x] Attach ACM certificate to distribution — TLS 1.2+, SNI, PriceClass_100
- [x] Add Route 53 alias record: `ai.rus-teston.com` → CloudFront distribution
- [x] Verify `https://ai.rus-teston.com` loads correctly — HTTP 200, SSL valid

## Phase 2: CI/CD Updates
- [ ] Check `GitHubActions-Deploy` IAM role has `cloudfront:CreateInvalidation` permission
- [ ] Add CloudFront invalidation step to GitHub Actions workflow
- [ ] Test: push a change, confirm auto-deploy + invalidation works

## Phase 3: URL Updates
- [ ] Update Lonestar landing page links from S3 URLs to `https://ai.rus-teston.com`
- [ ] Update project page links (back to projects, etc.) if needed
- [ ] Update README.md with new live site URL

## Phase 4: Security Hardening (Optional, Best Practice)
- [ ] Tighten Lambda CORS from `*` to `https://ai.rus-teston.com`
- [ ] Add security response headers policy to CloudFront (matching portfolio site)

## Notes
- S3 website URL remains functional as fallback throughout
- Each phase is independent — completing one doesn't break anything
- Portfolio site (rus-teston.com) is unaffected by all changes
