# Hackathon Pitch Pack

## Elevator Pitch

AI Trust Sentinel is infrastructure for trustworthy AI UX. Instead of showing users a raw model answer, it verifies the answer through claim extraction, live source checks, model consistency, and a 0-100 trust score with sentence-level evidence.

## Why Judges Should Care

- It solves a real and growing problem: AI answers are useful but often overtrusted.
- It is product-shaped, not just model-shaped.
- It has a clear user-facing output, which makes it easy to demo.
- It can be integrated into chatbots, agents, copilots, search, and RAG systems.

## Demo Flow

### 90-second script

1. Ask a myth-style question with a clear factual answer.
2. Show the primary answer and trust score.
3. Open the source drawer to show claim verification.
4. Click into sentence-level inspection.
5. Ask a harder or more ambiguous query to show score degradation.
6. Close by explaining how this could sit in front of any AI app.

## Technical Talking Points

- Multi-stage verification pipeline
- Confidence-gated second-opinion model
- Claim extraction with GPT-4o-mini
- Live fact-checking with Tavily
- Bias and intent-alignment scans
- Redis caching for repeat queries and demos

## Best Demo Queries

- Was Einstein really bad at math in school?
- Is the Great Wall of China visible from space?
- Was the Eiffel Tower meant to be temporary?
- Do humans only use 10 percent of their brain?

## What To Prepare Before Submitting

- Public repo
- Public demo
- 3 screenshots
- 90-second walkthrough video
- One architecture diagram
- One slide on limitations and future work
