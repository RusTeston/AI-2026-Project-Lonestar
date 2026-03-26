# CloudFront Migration Checklist — Project Lonestar

**Goal**: Serve ai-2026-project-lonestar via CloudFront + HTTPS at `https://ai.rus-teston.com`  
**Created**: March 22, 2026  
**Status**: ✅ COMPLETE

---

## Phase 1: CloudFront + SSL Setup ✅ COMPLETE
- [x] Request ACM certificate for `ai.rus-teston.com` (us-east-1) — `arn:aws:acm:us-east-1:901779867920:certificate/44d125cf-bff3-4651-bd17-7b553a05be4c`
- [x] Validate certificate via Route 53 DNS
- [x] Create CloudFront distribution pointing to `ai-2026-project-lonestar` S3 bucket — `E6LY7PZWUOBBP` (`d309r1vnuulj1s.cloudfront.net`)
- [x] Attach ACM certificate to distribution — TLS 1.2+, SNI, PriceClass_100
- [x] Add Route 53 alias record: `ai.rus-teston.com` → CloudFront distribution
- [x] Verify `https://ai.rus-teston.com` loads correctly — HTTP 200, SSL valid

## Phase 2: CI/CD Updates ✅ COMPLETE
- [x] Check `GitHubActions-Deploy` IAM role has `cloudfront:CreateInvalidation` permission — added `E6LY7PZWUOBBP`
- [x] Add CloudFront invalidation step to GitHub Actions workflow
- [x] Test: push a change, confirm auto-deploy + invalidation works

## Phase 3: URL Updates ✅ COMPLETE
- [x] Update Lonestar landing page links from S3 URLs to `https://ai.rus-teston.com`
- [x] Update project page links (Projects 1, 3, 4, 5, 8 back links + diagram links)
- [x] Update error page home button link
- [x] Update portfolio site (rus-teston.com) AI Projects link
- [x] Update README.md with new live site URL

## Phase 4: Security Hardening
- [x] Add security response headers policy to CloudFront — `d409f843-33ea-453e-a8f7-2fb44e4804ef` (HSTS, CSP, X-Frame, XSS Protection, Content-Type-Options)
- [ ] Tighten Lambda CORS from `*` to `https://ai.rus-teston.com` — DEFERRED (requires SAM redeploy of Projects 6, 7, 9 + Lambda update for Project 1; low risk item, `*` is acceptable for public demo APIs)

## Notes
- S3 website URL remains functional as fallback throughout
- Each phase is independent — completing one doesn't break anything
- Portfolio site (rus-teston.com) is unaffected by all changes
