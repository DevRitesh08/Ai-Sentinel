# AI Trust Sentinel Roadmap

This document is the execution plan for turning AI Trust Sentinel into a serious open-source project with a path to 5,000 GitHub stars, meaningful adoption, and a strong application for Anthropic's Claude for Open Source program.

## North Star

Build the most compelling open-source trust layer for AI answers on GitHub:

- Easy to understand in under 60 seconds
- Easy to run in under 10 minutes
- Easy to share because the output is visual, opinionated, and useful
- Serious enough for developers, product teams, and hackathon judges

## Reality Check

### What is already strong

- The core concept is interesting and timely.
- There is already a working full-stack product, not just a notebook.
- The frontend has personality and a good interaction model.
- The backend exposes a real API with a layered verification pipeline.

### What was holding the repo back

- The repo was nested one directory too deep.
- Debug files and local-only artifacts were mixed into the project story.
- The README did not explain the product as well as the product deserved.
- There was no contributor-facing roadmap or CI story.
- A public demo link was missing.
- The repo looked more like a local build directory than a launch-ready OSS project.

## What 5k-Star Repos Usually Get Right

- A sharp one-line value proposition
- A visual README with a clear architecture diagram
- A public demo people can try immediately
- Installation that feels safe and predictable
- A strong first impression on social feeds
- Visible traction loops: issues, PRs, screenshots, benchmarks, releases

Stars are downstream of product clarity, proof, and distribution. They are almost never the result of code quality alone.

## Phase 0: Cleanup And Positioning

Status: in progress

Goals:

- Make the GitHub root clean and understandable
- Remove misleading or local-only tracked files
- Rewrite the README around the actual product
- Add a contributor path and basic CI

Done in this pass:

- Flattened the repo to the GitHub root
- Removed tracked debug and documentation clutter
- Replaced the dead production frontend env file with an example file
- Added smoke tests and CI
- Rewrote the README
- Added this roadmap

## Phase 1: Demo-Ready Product

Target: next 7 days

Goals:

- Put a public demo online
- Make the product safe to try with minimal setup
- Capture visual proof for the README and launch content

Tasks:

1. Deploy the backend on Railway.
2. Deploy the frontend on Vercel.
3. Add a real public demo URL to the README.
4. Add 3-5 screenshots plus one short GIF.
5. Add a seeded demo mode so first impressions are consistently fast.
6. Add sample prompts that highlight controversial myths and clear evidence.

Success metrics:

- Public demo live
- Median response under 4 seconds on showcase prompts
- README contains screenshots, GIF, and working demo link

## Phase 2: Trustworthy Developer Experience

Target: next 2 weeks

Goals:

- Make developers comfortable starring, forking, and trying the repo
- Reduce friction for contributors and early users

Tasks:

1. Package the backend cleanly for `pip install`.
2. Add a proper namespaced Python package instead of generic module names.
3. Add Docker support for backend and frontend local runs.
4. Add example curl scripts and a simple SDK usage snippet.
5. Add GitHub issue templates, PR template, and release notes template.
6. Add benchmark fixtures for a small hallucination and myth dataset.
7. Publish a reproducible latency and cost breakdown.

Success metrics:

- One-command or near-one-command local setup
- First external contributor merged
- Zero "it does not run" issues in the first wave of traffic

## Phase 3: Product Quality And Research Credibility

Target: weeks 3-6

Goals:

- Make the project feel defensible, not just flashy
- Show where the system works and where it fails

Tasks:

1. Replace heuristic claim classification with a stronger verifier step.
2. Add eval scripts for claim extraction, fact-check quality, and trust-score calibration.
3. Publish a small benchmark table in the README.
4. Add a failure-case gallery.
5. Add observability around latency, cache-hit rate, and verification coverage.
6. Add streaming progress in the frontend so the system feels alive.

Success metrics:

- README benchmark section
- Clear performance and accuracy claims backed by repo artifacts
- Stronger comments and shares from technical audiences

## Phase 4: Distribution Engine

Target: weeks 2-8, overlapping with product work

Goals:

- Turn the repo into a project people discover repeatedly
- Build social proof outside GitHub

### Launch sequence

1. Ship demo and screenshots first.
2. Publish a Dev.to or Hashnode article.
3. Post on X with a short product demo clip.
4. Submit to Hacker News as "Show HN: AI Trust Sentinel".
5. Share in Reddit communities that fit the project.

### Good launch angles

- "I built a trust layer for AI answers that scores responses from 0-100"
- "This app highlights which sentences in an AI answer you should distrust"
- "A FastAPI plus React verifier pipeline for hallucination detection"
- "What happens when you force LLM answers through claim extraction plus live web checks?"

### Communities to target

- r/MachineLearning
- r/LocalLLaMA
- r/Python
- Hacker News
- Dev.to
- Hashnode
- X and LinkedIn

### Content assets to prepare

- 30-45 second demo video
- 3 screenshot carousel
- one architecture image
- one cost and latency chart
- one benchmark table

Success metrics:

- 500 stars in the first serious push
- At least 3 external writeups, reposts, or newsletters
- At least 20 quality GitHub issues or discussions from real users

## Phase 5: Community And Reuse

Target: weeks 6-12

Goals:

- Convert attention into ecosystem adoption
- Make the project useful beyond the main demo

Tasks:

1. Add a lightweight SDK or client helpers.
2. Add examples for RAG guardrails, agent validation, and chatbot moderation.
3. Open GitHub Discussions.
4. Curate "good first issue" and "help wanted" labels.
5. Publish release notes on a regular cadence.
6. Invite benchmark and data contributions.

Success metrics:

- 10 or more external contributors
- Repeat traffic from issues, forks, and release watchers
- Use cases beyond the demo app

## Hackathon Strategy

The project is a strong fit for:

- Devpost AI tracks
- MLH events
- lablab.ai AI agent or trust/safety tracks
- Cloud or platform hackathons with observability, safety, or agent themes

How to position it:

- Not as another chatbot
- As infrastructure for trustworthy AI UX
- As a practical guardrail layer for AI products

What to prepare:

- One-pager
- architecture slide
- 90-second live demo
- reproducible deploy
- benchmark summary

## Claude For Open Source Target

As of March 28, 2026, Anthropic's Claude for Open Source page says primary maintainers generally qualify with a public repo that has 5,000 or more GitHub stars or 1M or more monthly npm downloads, and it also explicitly invites ecosystem projects that do not fully fit the criteria to apply anyway.

Official source:

- [Claude for Open Source](https://claude.com/contact-sales/claude-for-oss)

### What that means for this repo

- The cleanest path is still to aim for 5,000 stars.
- A smaller but influential repo can still have a case if it becomes important infrastructure.
- The strongest application will include a live product, visible usage, recent activity, and a clear story about ecosystem value.

### Application checklist

- Public repo with polished README
- Live demo
- Consistent commits and releases in the last 3 months
- Visible community activity
- Clear explanation of why the project matters to the ecosystem
- Screenshots, benchmarks, and external references

## Metrics Dashboard To Track Weekly

- GitHub stars
- GitHub forks
- Unique repo visitors
- Frontend demo visits
- API requests
- Cache-hit rate
- Median and p95 latency
- Benchmark accuracy trend
- Number of contributors
- Number of discussions and issues

## Immediate 14-Day Sprint

### Week 1

1. Deploy backend and frontend.
2. Add screenshots and a GIF.
3. Add issue templates and PR template.
4. Add a benchmark seed dataset.
5. Add one strong launch article draft.

### Week 2

1. Ship a public launch on Hacker News and X.
2. Post on Reddit with visuals and honest metrics.
3. Submit to one hackathon.
4. Open GitHub Discussions.
5. Start collecting user feedback and failure cases.

## Non-Negotiables

- Do not fake accuracy claims.
- Do not hardcode broken demo URLs.
- Do not let the README drift away from the product.
- Do not optimize for stars at the expense of trust.

If this project becomes the open-source reference implementation for "show me why I should trust this AI answer," the stars will follow.
