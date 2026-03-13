# AI Trust Sentinel — Core Pipeline Roadmap
### Hours 8–20 | React Frontend + API Integration + Live Trust UI

> **"The backend works. Now make it visible. The demo lives or dies on what judges see in the browser — not what runs in your terminal."**

---

## Table of Contents

1. [Overview & Goals](#1-overview--goals)
2. [Pre-Phase Checklist — Handoff from Foundation](#2-pre-phase-checklist--handoff-from-foundation)
3. [Phase 5 — Backend Hardening & Pipeline Optimization (08:00–10:00)](#3-phase-5--backend-hardening--pipeline-optimization-0800--1000)
4. [Phase 6 — Frontend Scaffold & API Service Layer (10:00–13:00)](#4-phase-6--frontend-scaffold--api-service-layer-1000--1300)
5. [Phase 7 — Trust Score Widget & Sentence Highlighting (13:00–17:00)](#5-phase-7--trust-score-widget--sentence-highlighting-1300--1700)
6. [Phase 8 — Source Chain, Chat UX & Live Integration (17:00–20:00)](#6-phase-8--source-chain-chat-ux--live-integration-1700--2000)
7. [Master Checkpoint Summary](#7-master-checkpoint-summary)
8. [Error Reference Handbook](#8-error-reference-handbook)
9. [Component API Contract](#9-component-api-contract)
10. [If You Fall Behind Schedule](#10-if-you-fall-behind-schedule)

---

## 1. Overview & Goals

### What Hours 8–20 Must Deliver

The foundation (Hours 0–8) gave you a working backend API. Hours 8–20 transform that API into a **visual, interactive, demo-ready product**. By Hour 20, a judge must be able to:

1. Type any question into the chat interface
2. Watch the Trust Score animate into place in real-time
3. See the AI response with green/yellow/red sentence highlights
4. Click a highlighted claim and see the real source URL open in a new tab
5. Ask the same question again and see an instant cached response

Nothing else matters until those five experiences work perfectly.

---

### Deliverables Table

| Deliverable | Owner | Done When |
|---|---|---|
| Backend hardening & streaming endpoint | Backend lead | `/api/stream` SSE endpoint works with `curl` |
| Sentence segmentation service | Backend lead | Backend splits answer into annotated sentence array |
| React app scaffold | Frontend lead | Vite dev server running, Tailwind configured, file structure set |
| API service layer (`api.js`) | Frontend lead | `verifyQuery()` resolves correctly with real backend data |
| `TrustScoreMeter` component | Frontend lead | Animated gauge renders correctly for any 0–100 value |
| `ChatMessage` component | Frontend lead | Renders AI text with per-sentence color highlighting |
| `SourceChain` component | Frontend lead | Claim badges with status colors + clickable links |
| `ChatInput` component | Frontend lead | Submit on Enter/button, loading state, disabled during request |
| Full end-to-end demo flow | All | User types query → score appears → highlights render → sources clickable |
| Streaming UX (stretch goal) | Frontend lead | Trust score updates progressively as pipeline stages complete |

---

### Architecture for This Phase

```
┌─────────────────────────────────────────────────────────────┐
│                     BROWSER (React App)                     │
│                                                             │
│  ┌──────────────┐  ┌──────────────────────────────────────┐ │
│  │  ChatInput   │  │         ChatMessage                  │ │
│  │              │  │                                      │ │
│  │  [query...]  │  │  ┌──────────────────────────────┐   │ │
│  │  [Submit]    │  │  │    TrustScoreMeter (0-100)   │   │ │
│  └──────┬───────┘  │  │    ████████░░░░  82           │   │ │
│         │          │  └──────────────────────────────┘   │ │
│         │ POST     │                                      │ │
│         │          │  "The Eiffel Tower was built in      │ │
│         ▼          │   [████ 1889] for the [░░░░ World's] │ │
│  ┌──────────────┐  │   Fair. It stands [████ 330m] tall." │ │
│  │  api.js      │  │                                      │ │
│  │  axios POST  │  │  ┌──────────────────────────────┐   │ │
│  └──────┬───────┘  │  │      SourceChain              │   │ │
│         │          │  │  ✓ Built in 1889 → wiki.org   │   │ │
│         │          │  │  ? World's Fair → (unverified)│   │ │
│         │          │  │  ✓ 330m tall → toureiffel.fr  │   │ │
│         │          │  └──────────────────────────────┘   │ │
│         │          └──────────────────────────────────────┘ │
└─────────┼───────────────────────────────────────────────────┘
          │ HTTP POST /api/verify
          ▼
┌─────────────────────────────────────────────────────────────┐
│              FastAPI Backend (from Hours 0-8)               │
│                                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌───────────┐  │
│  │  Redis   │  │ GPT-4o   │  │  Gemini  │  │  Tavily   │  │
│  │  Cache   │  │  mini    │  │  Flash   │  │ Fact-Check│  │
│  └──────────┘  └──────────┘  └──────────┘  └───────────┘  │
│                                                             │
│  NEW: Sentence segmentation added to pipeline output       │
└─────────────────────────────────────────────────────────────┘
```

---

### Team Split for Hours 8–20

| Hours | Backend Lead | Frontend Lead | Sync Points |
|---|---|---|---|
| 8:00–10:00 | Hardening, sentence segmentation, streaming | Environment setup, scaffold | 10:00 — API contract review |
| 10:00–13:00 | Supporting frontend questions, bug fixes | API service layer, component skeleton | 13:00 — First real API call from React |
| 13:00–17:00 | Optimize pipeline latency, add more test cases | TrustScoreMeter, ChatMessage, highlighting | 17:00 — Full component integration |
| 17:00–20:00 | Final API polish, error responses, logging | SourceChain, chat UX, end-to-end wiring | 20:00 — Demo flow must work completely |

---

## 2. Pre-Phase Checklist — Handoff from Foundation

Before starting Phase 5, verify the following with the complete team. This sync takes 10 minutes and saves hours of confusion.

### Backend (from Hours 0–8)

```bash
# Run the full acceptance test from Checkpoint 7
# Every item should be ✓

curl -s http://localhost:8000/health | python -m json.tool
# Expected: {"status": "ok", "version": "1.0.0"}

curl -s -X POST http://localhost:8000/api/verify \
  -H "Content-Type: application/json" \
  -d '{"query": "What year was the Eiffel Tower built?"}' \
  | python -m json.tool
# Expected: Full JSON with trust_score, answer, claims[], from_cache, latency_ms
```

### Shared API Contract Review

Both frontend and backend must agree on this schema before splitting work:

```json
{
  "trust_score": 82,
  "answer": "Full primary LLM answer...",
  "confidence": 88,
  "verifier_used": false,
  "claims": [
    {
      "text": "The Eiffel Tower was completed in 1889",
      "status": "VERIFIED",
      "source_url": "https://en.wikipedia.org/wiki/Eiffel_Tower",
      "source_title": "Eiffel Tower — Wikipedia"
    }
  ],
  "from_cache": false,
  "latency_ms": 1842,
  "error": null
}
```

> ⚠️ **Freeze this schema now.** Any field rename after the frontend has built against it will break components. Additions are OK. Renames are not.

### Team Sync Checklist

- [ ] Backend: `/api/verify` returns correct schema for 3 different test queries
- [ ] Backend: Redis cache is working (second call returns `from_cache: true`)
- [ ] Backend: At least one `CONTRADICTED` claim detectable on a false test query
- [ ] Frontend: Node.js 18+ and npm available (`node --version`)
- [ ] All: API base URL agreed (`http://localhost:8000/api` for development)
- [ ] All: Git repo committed and pushed before splitting work

---

## 3. Phase 5 — Backend Hardening & Pipeline Optimization (08:00–10:00)

**Goal:** Strengthen the backend before the frontend team starts building against it. Add sentence-level segmentation to the pipeline output, improve streaming support, and lock in the final response schema.

**Owner:** Backend lead  
**Frontend status:** Setting up React environment in parallel (Phase 6, Task 6.1)

---

### Task 5.1 — Sentence Segmentation Service (40 min)

The frontend needs to render the AI answer with per-sentence color coding. To do this, the backend must split the answer into individual sentences and annotate each one with a trust status based on which claims it contains.

```python
# backend/services/sentence_segmenter.py
import re
import logging
from models.schemas import ClaimResult, ClaimStatus

logger = logging.getLogger(__name__)


def split_into_sentences(text: str) -> list[str]:
    """
    Splits text into sentences using a regex that handles common edge cases:
    - Abbreviations (Dr., Mr., U.S.)
    - Decimal numbers (3.14)
    - Ellipsis (...)
    - Quoted speech ending with ." or !"
    """
    # Protect common abbreviations from being split
    abbreviations = ["Dr", "Mr", "Mrs", "Ms", "Prof", "Sr", "Jr",
                     "vs", "etc", "e.g", "i.e", "U.S", "U.K", "approx"]
    protected = text
    for abbr in abbreviations:
        protected = protected.replace(f"{abbr}.", f"{abbr}<<<DOT>>>")

    # Split on sentence-ending punctuation followed by space + capital
    sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z"\'(])', protected)

    # Restore protected dots and strip whitespace
    cleaned = []
    for s in sentences:
        s = s.replace("<<<DOT>>>", ".").strip()
        if len(s) > 8:     # Filter out very short fragments
            cleaned.append(s)

    return cleaned if cleaned else [text]


def annotate_sentences(
    sentences: list[str],
    claims:    list[ClaimResult]
) -> list[dict]:
    """
    Maps each sentence to a trust status based on which claim(s) it best matches.

    Returns a list of dicts:
    [
      {
        "text":       "The Eiffel Tower was built in 1889.",
        "status":     "VERIFIED",
        "claim_ref":  "The Eiffel Tower was completed in 1889",
        "source_url": "https://en.wikipedia.org/wiki/Eiffel_Tower"
      },
      ...
    ]
    """
    annotated = []

    for sentence in sentences:
        best_match_status = None
        best_match_score  = 0.0
        best_claim_ref    = None
        best_source_url   = None

        sentence_words = set(sentence.lower().split())

        for claim in claims:
            claim_words = set(claim.text.lower().split())
            overlap = len(sentence_words & claim_words) / max(len(claim_words), 1)

            if overlap > best_match_score:
                best_match_score  = overlap
                best_match_status = claim.status
                best_claim_ref    = claim.text
                best_source_url   = claim.source_url

        # Only annotate with a claim if there's meaningful overlap
        if best_match_score >= 0.20 and best_match_status:
            status = best_match_status.value
        else:
            status = "NEUTRAL"   # No matching claim — render without highlight

        annotated.append({
            "text":       sentence,
            "status":     status,
            "claim_ref":  best_claim_ref,
            "source_url": best_source_url
        })

        logger.debug(f"Sentence: '{sentence[:40]}...' → {status} (overlap={best_match_score:.2f})")

    return annotated
```

**Test the segmenter standalone:**

```python
# Quick test
from services.sentence_segmenter import split_into_sentences, annotate_sentences
from models.schemas import ClaimResult, ClaimStatus

text = (
    "The Eiffel Tower was built in 1889 for the World's Fair. "
    "It stands 330 meters tall and was designed by Gustave Eiffel. "
    "The tower was originally meant to be demolished after 20 years. "
    "Today it receives over 7 million visitors annually."
)

sentences = split_into_sentences(text)
print(f"Segmented into {len(sentences)} sentences:")
for i, s in enumerate(sentences):
    print(f"  [{i+1}] {s}")

# Mock claims for testing
mock_claims = [
    ClaimResult(text="Eiffel Tower built in 1889", status=ClaimStatus.VERIFIED,
                source_url="https://en.wikipedia.org/wiki/Eiffel_Tower"),
    ClaimResult(text="stands 330 meters tall", status=ClaimStatus.VERIFIED,
                source_url="https://www.toureiffel.paris"),
    ClaimResult(text="planned for demolition after 20 years", status=ClaimStatus.UNCERTAIN,
                source_url=None),
]

annotated = annotate_sentences(sentences, mock_claims)
for a in annotated:
    print(f"  [{a['status']}] {a['text'][:50]}")
```

---

### Task 5.2 — Update Pipeline to Include Annotated Sentences (20 min)

Update the Pydantic schema and pipeline orchestrator to include sentence annotations in the response.

```python
# backend/models/schemas.py — ADD these new models

class SentenceAnnotation(BaseModel):
    text:       str
    status:     str           # "VERIFIED" | "UNCERTAIN" | "CONTRADICTED" | "NEUTRAL"
    claim_ref:  Optional[str] = None
    source_url: Optional[str] = None


class VerifyResponse(BaseModel):
    trust_score:    int
    answer:         str
    confidence:     int
    verifier_used:  bool
    claims:         List[ClaimResult]
    sentences:      List[SentenceAnnotation]   # NEW — add this field
    from_cache:     bool
    latency_ms:     int
    error:          Optional[str] = None
    trust_label:    Optional[str] = None       # NEW — "HIGH CONFIDENCE" etc.
    trust_color:    Optional[str] = None       # NEW — hex color for frontend
```

```python
# backend/services/pipeline.py — UPDATE Stage 7

from services.sentence_segmenter import split_into_sentences, annotate_sentences
from services.trust_score import score_to_label, score_to_color

# Inside run_verification_pipeline(), replace the finalize block:

# ── Stage 7: Sentence segmentation + Trust score + finalize ──────────
trust_score = calculate_trust_score(
    primary_confidence=primary["confidence"],
    consistency_score=consistency,
    fact_results=fact_results,
    verifier_used=verifier_used
)

# Segment and annotate sentences
sentences_raw  = split_into_sentences(primary["answer"])
sentences_ann  = annotate_sentences(sentences_raw, fact_results)

elapsed_ms = int((time.time() - start_time) * 1000)

result = VerifyResponse(
    trust_score   = trust_score,
    answer        = primary["answer"],
    confidence    = primary["confidence"],
    verifier_used = verifier_used,
    claims        = fact_results,
    sentences     = sentences_ann,           # NEW
    from_cache    = False,
    latency_ms    = elapsed_ms,
    trust_label   = score_to_label(trust_score),   # NEW
    trust_color   = score_to_color(trust_score),   # NEW
)
```

---

### Task 5.3 — Add Streaming SSE Endpoint (30 min)

Streaming lets the frontend show progress while the pipeline runs — a critical UX improvement for a product that takes 1–3 seconds. Even if the frontend doesn't use it at first, having it ready is valuable.

```python
# backend/routers/verify.py — ADD streaming endpoint

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from models.schemas import VerifyRequest
import asyncio, json, time

router = APIRouter()


@router.post("/verify/stream")
async def verify_stream(payload: VerifyRequest):
    """
    Server-Sent Events streaming endpoint.
    Emits pipeline stage events as they complete, then the final result.

    Frontend subscribes with: new EventSource(url) or fetch() + ReadableStream
    """
    query = payload.query.strip()

    async def event_generator():
        start = time.time()

        # Emit stage progress events as pipeline runs
        async def emit(event: str, data: dict):
            payload_str = json.dumps(data)
            yield f"event: {event}\ndata: {payload_str}\n\n"

        yield f"event: start\ndata: {json.dumps({'stage': 'started', 'query': query})}\n\n"
        await asyncio.sleep(0)

        # Stage 1: Cache check
        from services.cache import get_cached
        cached = get_cached(query)
        if cached:
            yield f"event: cache_hit\ndata: {json.dumps({'from_cache': True})}\n\n"
            yield f"event: complete\ndata: {json.dumps(cached)}\n\n"
            return

        yield f"event: stage\ndata: {json.dumps({'stage': 'calling_primary_llm'})}\n\n"

        # Stage 2: Primary LLM
        from services.llm_primary import call_primary
        try:
            primary = await call_primary(query)
        except Exception as e:
            yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"
            return

        yield f"event: primary_done\ndata: {json.dumps({'confidence': primary['confidence']})}\n\n"

        # Stage 3-7: Run the rest of the pipeline
        from services.pipeline import run_verification_pipeline
        yield f"event: stage\ndata: {json.dumps({'stage': 'fact_checking'})}\n\n"

        result = await run_verification_pipeline(query)
        result_dict = result.model_dump()

        yield f"event: complete\ndata: {json.dumps(result_dict)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",   # Disable nginx buffering
        }
    )
```

---

### Task 5.4 — Pipeline Latency Optimization (30 min)

Profile the pipeline and apply targeted optimizations. A sub-2-second response for non-cached queries makes the demo feel instant.

```python
# backend/services/pipeline.py — Add timing instrumentation

import time
import logging

logger = logging.getLogger(__name__)

class PipelineTimer:
    """Simple timer for profiling each pipeline stage."""

    def __init__(self):
        self.start = time.time()
        self.stages = {}

    def mark(self, stage: str):
        self.stages[stage] = round((time.time() - self.start) * 1000)
        logger.info(f"[PIPELINE] {stage}: {self.stages[stage]}ms elapsed")

    def summary(self) -> dict:
        return self.stages


# In run_verification_pipeline(), instrument every stage:
async def run_verification_pipeline(query: str) -> VerifyResponse:
    timer = PipelineTimer()

    cached = get_cached(query)
    timer.mark("cache_check")
    if cached:
        return VerifyResponse(**cached)

    primary = await call_primary(query)
    timer.mark("primary_llm")

    escalate = should_escalate(primary["confidence"])
    timer.mark("gate_decision")

    # Run verifier + claim extraction in PARALLEL (key optimization)
    verifier_coro  = call_verifier(query) if escalate else asyncio.sleep(0, result=None)
    extractor_coro = extract_claims(primary["answer"])

    verifier_raw, raw_claims = await asyncio.gather(
        verifier_coro, extractor_coro, return_exceptions=True
    )
    timer.mark("parallel_llm_and_extraction")

    claims = validate_claims(raw_claims if isinstance(raw_claims, list) else [])

    # Fact-check all claims concurrently
    fact_results = await fact_check_all_claims(claims)
    timer.mark("fact_check")

    # Sentence segmentation + score (fast, no API calls)
    sentences_raw = split_into_sentences(primary["answer"])
    sentences_ann = annotate_sentences(sentences_raw, fact_results)
    trust_score   = calculate_trust_score(
        primary["confidence"],
        calculate_consistency_score(primary["answer"], verifier_raw["answer"])
            if isinstance(verifier_raw, dict) and verifier_raw.get("answer") else None,
        fact_results,
        isinstance(verifier_raw, dict)
    )
    timer.mark("score_and_segment")

    logger.info(f"[PIPELINE SUMMARY] {timer.summary()}")
    # ... build and return VerifyResponse
```

**Run and read the timing output. Anything > 1000ms is worth optimizing:**

```
[PIPELINE] cache_check: 12ms elapsed          ← always fast
[PIPELINE] primary_llm: 890ms elapsed         ← acceptable
[PIPELINE] gate_decision: 891ms elapsed       ← instant
[PIPELINE] parallel_llm_and_extraction: 1240ms ← good, running in parallel
[PIPELINE] fact_check: 1850ms elapsed         ← optimize if > 2000ms
[PIPELINE] score_and_segment: 1855ms elapsed  ← always fast
```

**If `fact_check` is slow:**
- Check `search_depth="basic"` is set on Tavily (not `"advanced"`)
- Reduce `MAX_TAVILY_RESULTS` from 3 to 2
- Set `max_results=2` in the Tavily call

---

### ✅ Checkpoint 5 — Backend Hardening Complete (@ 10:00)

```bash
# Test 1: Sentence segmentation in response
curl -s -X POST http://localhost:8000/api/verify \
  -H "Content-Type: application/json" \
  -d '{"query": "The Great Wall of China is visible from space."}' \
  | python -m json.tool | grep -A 20 '"sentences"'

# Expected: Array of sentence objects with text, status, source_url fields

# Test 2: trust_label and trust_color in response
curl -s -X POST http://localhost:8000/api/verify \
  -H "Content-Type: application/json" \
  -d '{"query": "Water boils at 100 degrees Celsius."}' \
  | python -m json.tool | grep -E '"trust_label"|"trust_color"|"trust_score"'

# Expected: trust_label: "HIGH CONFIDENCE", trust_color: "#00FF9D", trust_score: 85+

# Test 3: Streaming endpoint responds
curl -N -X POST http://localhost:8000/api/verify/stream \
  -H "Content-Type: application/json" \
  -d '{"query": "Who built the Pyramids?"}' 2>&1 | head -20

# Expected: stream of event: ... data: ... lines

# Test 4: Pipeline timing logged
# Check server logs for: [PIPELINE SUMMARY] {'cache_check': X, 'primary_llm': X, ...}
```

| Test | Expected | If Failing |
|---|---|---|
| `sentences` array in response | Non-empty list of sentence objects | Check `sentence_segmenter` imported in pipeline and `sentences` field added to schema |
| Each sentence has `status` | One of: `VERIFIED`, `UNCERTAIN`, `CONTRADICTED`, `NEUTRAL` | Check `annotate_sentences()` always returns a status string |
| `trust_label` present | `"HIGH CONFIDENCE"` or similar | Add `trust_label` and `trust_color` to `VerifyResponse` schema |
| Streaming endpoint returns SSE | Lines starting with `event:` and `data:` | Check `media_type="text/event-stream"` and no buffering |
| Total pipeline latency | < 3000ms for non-cached | Check fact-check parallel execution, reduce Tavily `max_results` |

---

## 4. Phase 6 — Frontend Scaffold & API Service Layer (10:00–13:00)

**Goal:** React app running with Tailwind, folder structure mirroring the backend's organization, and a fully working API service that the component team can call with a single function.

**Owner:** Frontend lead  
**Backend status:** Continuing optimization and answering questions

---

### Task 6.1 — React App Scaffold (30 min)

Run these commands in the `/frontend` directory.

```bash
# Create React app with Vite (fastest setup)
cd ai-trust-sentinel/frontend
npm create vite@latest . -- --template react
npm install

# Install all dependencies upfront
npm install axios tailwindcss postcss autoprefixer
npm install @headlessui/react lucide-react
npm install clsx

# Initialize Tailwind
npx tailwindcss init -p
```

**Configure Tailwind to scan all component files:**

```javascript
// frontend/tailwind.config.js
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // AI Trust Sentinel brand colors — match the pitch deck
        "ats-bg":       "#060A10",
        "ats-surface":  "#0F1A2E",
        "ats-border":   "#1D304E",
        "ats-cyan":     "#00E5FF",
        "ats-green":    "#00FF9D",
        "ats-yellow":   "#FFD166",
        "ats-red":      "#FF4F6A",
        "ats-purple":   "#9B72FF",
        "ats-text":     "#C8D8EE",
        "ats-muted":    "#4A6080",
      },
      fontFamily: {
        mono: ["'JetBrains Mono'", "monospace"],
        sans: ["Barlow", "sans-serif"],
      },
      animation: {
        "fade-up":   "fadeUp 0.4s ease both",
        "score-in":  "scoreIn 0.8s cubic-bezier(0.34, 1.56, 0.64, 1) both",
        "pulse-dot": "pulseDot 2s infinite",
        "shimmer":   "shimmer 1.5s infinite",
      },
      keyframes: {
        fadeUp: {
          "0%":   { opacity: "0", transform: "translateY(12px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        scoreIn: {
          "0%":   { transform: "scale(0.6)", opacity: "0" },
          "100%": { transform: "scale(1)",   opacity: "1" },
        },
        pulseDot: {
          "0%, 100%": { opacity: "1",   transform: "scale(1)" },
          "50%":      { opacity: "0.4", transform: "scale(0.85)" },
        },
        shimmer: {
          "0%":   { backgroundPosition: "-200% 0" },
          "100%": { backgroundPosition: "200% 0" },
        },
      },
    },
  },
  plugins: [],
}
```

**Add Google Fonts and global CSS:**

```html
<!-- frontend/index.html — add to <head> -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;700&family=Barlow:wght@300;500;600;700;800&display=swap" rel="stylesheet">
<title>AI Trust Sentinel</title>
```

```css
/* frontend/src/index.css — replace default content */
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  body {
    @apply bg-ats-bg text-ats-text font-sans;
    background-image:
      linear-gradient(rgba(0,229,255,0.025) 1px, transparent 1px),
      linear-gradient(90deg, rgba(0,229,255,0.025) 1px, transparent 1px);
    background-size: 48px 48px;
  }

  * {
    @apply box-border;
    scrollbar-width: thin;
    scrollbar-color: #1D304E transparent;
  }
}

@layer components {
  .card {
    @apply bg-ats-surface border border-ats-border rounded-xl;
  }

  .badge-verified {
    @apply bg-green-950 text-ats-green border border-green-800 text-xs font-mono px-2 py-0.5 rounded-full;
  }

  .badge-uncertain {
    @apply bg-yellow-950 text-ats-yellow border border-yellow-800 text-xs font-mono px-2 py-0.5 rounded-full;
  }

  .badge-contradicted {
    @apply bg-red-950 text-ats-red border border-red-900 text-xs font-mono px-2 py-0.5 rounded-full;
  }

  .badge-neutral {
    @apply bg-ats-surface text-ats-muted border border-ats-border text-xs font-mono px-2 py-0.5 rounded-full;
  }
}
```

---

### Task 6.2 — Folder Structure (15 min)

Create this exact structure before writing any component code.

```
frontend/src/
├── api/
│   └── client.js          # Axios instance + verifyQuery() function
├── components/
│   ├── ChatInput.jsx       # Query input + submit button
│   ├── ChatMessage.jsx     # Message bubble container
│   ├── TrustScoreMeter.jsx # Animated trust score gauge
│   ├── SentenceText.jsx    # Highlighted sentence renderer
│   ├── SourceChain.jsx     # Claim cards with source links
│   ├── LoadingState.jsx    # Skeleton/spinner while pipeline runs
│   └── ErrorState.jsx      # Error message display
├── hooks/
│   └── useVerify.js        # Custom hook wrapping API call + state
├── utils/
│   └── trustHelpers.js     # Color/label/icon helpers
├── App.jsx                 # Root layout
└── main.jsx                # Entry point
```

---

### Task 6.3 — API Service Layer (45 min)

This is the most critical frontend file. Every component depends on it. Build it carefully and test it before touching UI.

```javascript
// frontend/src/api/client.js
import axios from "axios";

const BASE_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000/api";

const apiClient = axios.create({
  baseURL: BASE_URL,
  timeout: 30000,           // 30 second timeout — pipeline can be slow
  headers: {
    "Content-Type": "application/json",
  },
});

// Request interceptor — log outgoing calls in development
apiClient.interceptors.request.use((config) => {
  if (import.meta.env.DEV) {
    console.log(`[API] ${config.method?.toUpperCase()} ${config.url}`, config.data);
  }
  return config;
});

// Response interceptor — log responses and handle errors centrally
apiClient.interceptors.response.use(
  (response) => {
    if (import.meta.env.DEV) {
      console.log(`[API] Response ${response.status}`, response.data);
    }
    return response;
  },
  (error) => {
    const status  = error.response?.status;
    const message = error.response?.data?.detail ?? error.message;
    console.error(`[API] Error ${status}:`, message);

    // Normalize all errors into a consistent shape
    const normalized = {
      status,
      message,
      isTimeout:   error.code === "ECONNABORTED",
      isNetwork:   !error.response,
      isServer:    status >= 500,
      isClient:    status >= 400 && status < 500,
    };
    return Promise.reject(normalized);
  }
);

export default apiClient;


/**
 * verifyQuery — main API call
 *
 * @param {string} query  - The user's question
 * @returns {Promise<VerifyResponse>}
 *
 * VerifyResponse shape:
 * {
 *   trust_score:   number (0-100)
 *   answer:        string
 *   confidence:    number (0-100)
 *   verifier_used: boolean
 *   claims:        ClaimResult[]
 *   sentences:     SentenceAnnotation[]
 *   from_cache:    boolean
 *   latency_ms:    number
 *   trust_label:   string
 *   trust_color:   string (hex)
 *   error:         string | null
 * }
 */
export async function verifyQuery(query) {
  if (!query?.trim()) {
    throw { status: 400, message: "Query cannot be empty", isClient: true };
  }

  const response = await apiClient.post("/verify", { query: query.trim() });
  return response.data;
}


/**
 * checkHealth — ping the backend
 * @returns {Promise<boolean>}
 */
export async function checkHealth() {
  try {
    await apiClient.get("/health", { timeout: 3000 });
    return true;
  } catch {
    return false;
  }
}
```

**Create the `.env` file for the frontend:**

```bash
# frontend/.env
VITE_API_URL=http://localhost:8000/api
```

---

### Task 6.4 — `useVerify` Custom Hook (40 min)

Centralizes all API state management. Every component stays clean because they consume this hook rather than managing their own fetch state.

```javascript
// frontend/src/hooks/useVerify.js
import { useState, useCallback, useRef } from "react";
import { verifyQuery } from "../api/client";

const INITIAL_STATE = {
  data:      null,     // VerifyResponse or null
  loading:   false,
  error:     null,     // Error message string or null
  fromCache: false,
};

export function useVerify() {
  const [state, setState] = useState(INITIAL_STATE);
  const abortRef = useRef(null);   // For potential future request cancellation

  const verify = useCallback(async (query) => {
    // Cancel any in-flight request
    if (abortRef.current) {
      abortRef.current.abort();
    }

    setState({ data: null, loading: true, error: null, fromCache: false });

    try {
      const result = await verifyQuery(query);

      setState({
        data:      result,
        loading:   false,
        error:     null,
        fromCache: result.from_cache ?? false,
      });

      return result;

    } catch (err) {
      let errorMessage = "Something went wrong. Please try again.";

      if (err.isTimeout) {
        errorMessage = "The request timed out. The pipeline may be busy — try again.";
      } else if (err.isNetwork) {
        errorMessage = "Cannot reach the server. Is the backend running on port 8000?";
      } else if (err.isClient) {
        errorMessage = err.message ?? "Invalid request.";
      } else if (err.isServer) {
        errorMessage = "Server error. Check the backend logs.";
      }

      setState({
        data:      null,
        loading:   false,
        error:     errorMessage,
        fromCache: false,
      });

      return null;
    }
  }, []);

  const reset = useCallback(() => {
    setState(INITIAL_STATE);
  }, []);

  return {
    ...state,
    verify,
    reset,
    hasResult: !!state.data && !state.loading,
    isLoading: state.loading,
    hasError:  !!state.error && !state.loading,
  };
}
```

---

### Task 6.5 — Utility Helpers (20 min)

Centralizing these prevents inconsistency across components.

```javascript
// frontend/src/utils/trustHelpers.js

/**
 * Returns Tailwind color classes and display properties for a given trust score.
 */
export function getTrustConfig(score) {
  if (score >= 85) return {
    label:          "HIGH CONFIDENCE",
    color:          "#00FF9D",
    bgClass:        "bg-green-950",
    borderClass:    "border-green-700",
    textClass:      "text-ats-green",
    ringClass:      "ring-ats-green",
    emoji:          "✓",
  };
  if (score >= 65) return {
    label:          "MODERATE CONFIDENCE",
    color:          "#FFD166",
    bgClass:        "bg-yellow-950",
    borderClass:    "border-yellow-700",
    textClass:      "text-ats-yellow",
    ringClass:      "ring-ats-yellow",
    emoji:          "~",
  };
  if (score >= 45) return {
    label:          "LOW CONFIDENCE",
    color:          "#FF9A3C",
    bgClass:        "bg-orange-950",
    borderClass:    "border-orange-800",
    textClass:      "text-orange-400",
    ringClass:      "ring-orange-400",
    emoji:          "!",
  };
  return {
    label:          "UNRELIABLE",
    color:          "#FF4F6A",
    bgClass:        "bg-red-950",
    borderClass:    "border-red-900",
    textClass:      "text-ats-red",
    ringClass:      "ring-ats-red",
    emoji:          "✗",
  };
}

/**
 * Returns Tailwind classes for a claim/sentence status string.
 */
export function getStatusConfig(status) {
  switch (status?.toUpperCase()) {
    case "VERIFIED":
      return {
        highlightBg:  "bg-green-950/60",
        highlightBdr: "border-b-2 border-ats-green",
        badgeClass:   "badge-verified",
        dotColor:     "bg-ats-green",
        label:        "Verified",
        icon:         "✓",
      };
    case "UNCERTAIN":
      return {
        highlightBg:  "bg-yellow-950/50",
        highlightBdr: "border-b-2 border-ats-yellow",
        badgeClass:   "badge-uncertain",
        dotColor:     "bg-ats-yellow",
        label:        "Uncertain",
        icon:         "?",
      };
    case "CONTRADICTED":
      return {
        highlightBg:  "bg-red-950/60",
        highlightBdr: "border-b-2 border-ats-red",
        badgeClass:   "badge-contradicted",
        dotColor:     "bg-ats-red",
        label:        "Contradicted",
        icon:         "✗",
      };
    default:
      return {
        highlightBg:  "",
        highlightBdr: "",
        badgeClass:   "badge-neutral",
        dotColor:     "bg-ats-muted",
        label:        "Unverified",
        icon:         "–",
      };
  }
}

/**
 * Formats latency in milliseconds into a human-readable string.
 */
export function formatLatency(ms) {
  if (!ms) return null;
  if (ms < 100)  return "instant (cached)";
  if (ms < 1000) return `${ms}ms`;
  return `${(ms / 1000).toFixed(1)}s`;
}
```

---

### ✅ Checkpoint 6 — Frontend Foundation Ready (@ 13:00)

```bash
# In the frontend directory:

# Test 1: Dev server starts
npm run dev
# Expected: "Local: http://localhost:5173/" with no errors

# Test 2: API call from browser console (open localhost:5173)
# Open DevTools > Console and paste:
fetch("http://localhost:8000/api/verify", {
  method: "POST",
  headers: {"Content-Type": "application/json"},
  body: JSON.stringify({query: "What is the capital of France?"})
})
.then(r => r.json())
.then(d => console.log("TRUST SCORE:", d.trust_score, "| SENTENCES:", d.sentences?.length))
# Expected: TRUST SCORE: [number] | SENTENCES: [number > 0]

# Test 3: CORS working
# If you see "Access-Control-Allow-Origin" error → backend CORS not configured
# Fix: Ensure CORSMiddleware in FastAPI allows localhost:5173

# Test 4: Environment variable
# In browser console:
console.log(import.meta.env.VITE_API_URL)
# Expected: "http://localhost:8000/api"
```

| Check | Expected | If Failing |
|---|---|---|
| `npm run dev` no errors | Server at localhost:5173 | Check Node version ≥ 18, delete node_modules and reinstall |
| API call from console works | Returns JSON with trust_score | Check backend is running, CORS allows localhost:5173 |
| CORS not blocked | No CORS error in console | Add `"http://localhost:5173"` to FastAPI `allow_origins` list |
| `VITE_API_URL` defined | Shows the API URL | Check `.env` file is in `/frontend/` root, not `/frontend/src/` |
| Tailwind classes apply | Background should be very dark (#060A10) | Check `tailwind.config.js` `content` array includes `./src/**/*.jsx` |

---

## 5. Phase 7 — Trust Score Widget & Sentence Highlighting (13:00–17:00)

**Goal:** Build the three core visual components that define the product's identity: the Trust Score Meter, the sentence-highlighted response, and the Source Chain.

---

### Task 7.1 — `TrustScoreMeter` Component (60 min)

The most memorable visual element. Must animate smoothly, react instantly to the score value, and communicate trust level at a glance.

```jsx
// frontend/src/components/TrustScoreMeter.jsx
import { useEffect, useState, useRef } from "react";
import { getTrustConfig } from "../utils/trustHelpers";

/**
 * Animated circular gauge showing the trust score 0-100.
 *
 * Props:
 *   score {number}  - Trust score 0-100
 *   size  {number}  - Diameter in pixels (default: 160)
 *   animated {bool} - Whether to animate from 0 (default: true)
 */
export default function TrustScoreMeter({ score, size = 160, animated = true }) {
  const [displayScore, setDisplayScore] = useState(animated ? 0 : score);
  const config = getTrustConfig(score);

  // Animate score counting up from 0 to target
  useEffect(() => {
    if (!animated) { setDisplayScore(score); return; }

    let current   = 0;
    const target  = score;
    const duration = 900;  // ms
    const steps    = 60;
    const increment = target / steps;
    const interval  = duration / steps;

    const timer = setInterval(() => {
      current += increment;
      if (current >= target) {
        setDisplayScore(target);
        clearInterval(timer);
      } else {
        setDisplayScore(Math.floor(current));
      }
    }, interval);

    return () => clearInterval(timer);
  }, [score, animated]);

  // SVG circle math
  const radius      = (size / 2) - 14;
  const circumference = 2 * Math.PI * radius;
  const strokeDash   = (displayScore / 100) * circumference;
  const center       = size / 2;

  return (
    <div className="flex flex-col items-center gap-3 animate-score-in">
      {/* SVG circular gauge */}
      <div className="relative" style={{ width: size, height: size }}>
        <svg
          width={size}
          height={size}
          viewBox={`0 0 ${size} ${size}`}
          className="-rotate-90"
        >
          {/* Background track */}
          <circle
            cx={center}
            cy={center}
            r={radius}
            fill="none"
            stroke="#1D304E"
            strokeWidth="8"
          />
          {/* Progress arc */}
          <circle
            cx={center}
            cy={center}
            r={radius}
            fill="none"
            stroke={config.color}
            strokeWidth="8"
            strokeLinecap="round"
            strokeDasharray={`${strokeDash} ${circumference}`}
            style={{
              transition: "stroke-dasharray 0.05s linear",
              filter: `drop-shadow(0 0 8px ${config.color}60)`,
            }}
          />
        </svg>

        {/* Center content */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span
            className="font-mono font-bold leading-none"
            style={{
              fontSize:  size * 0.28,
              color:     config.color,
              textShadow: `0 0 20px ${config.color}50`,
            }}
          >
            {displayScore}
          </span>
          <span className="text-ats-muted font-mono" style={{ fontSize: size * 0.075 }}>
            /100
          </span>
        </div>
      </div>

      {/* Label below gauge */}
      <div className="flex flex-col items-center gap-1">
        <span
          className={`font-mono text-xs font-bold tracking-widest ${config.textClass}`}
        >
          {config.label}
        </span>

        {/* Status bar */}
        <div className="w-32 h-1.5 bg-ats-border rounded-full overflow-hidden">
          <div
            className="h-full rounded-full transition-all duration-700"
            style={{
              width:      `${score}%`,
              background: config.color,
              boxShadow:  `0 0 6px ${config.color}`,
            }}
          />
        </div>
      </div>
    </div>
  );
}
```

**Render it for testing:**

```jsx
// Quick test in App.jsx
import TrustScoreMeter from "./components/TrustScoreMeter";

function App() {
  return (
    <div className="min-h-screen flex items-center justify-center gap-8">
      <TrustScoreMeter score={92} />
      <TrustScoreMeter score={68} />
      <TrustScoreMeter score={31} />
    </div>
  );
}
```

---

### Task 7.2 — `SentenceText` Component (50 min)

The most technically nuanced component. Renders the AI answer with per-sentence color highlighting and makes each highlighted sentence clickable to reveal its source.

```jsx
// frontend/src/components/SentenceText.jsx
import { useState } from "react";
import { getStatusConfig } from "../utils/trustHelpers";

/**
 * Renders an AI response with per-sentence trust highlighting.
 *
 * Props:
 *   sentences {Array} - Array of SentenceAnnotation objects from the API:
 *     { text, status, claim_ref, source_url }
 */
export default function SentenceText({ sentences }) {
  const [activeSentence, setActiveSentence] = useState(null);

  if (!sentences?.length) return null;

  return (
    <div className="space-y-1">
      {sentences.map((sentence, idx) => (
        <SentenceSegment
          key={idx}
          sentence={sentence}
          isActive={activeSentence === idx}
          onToggle={() => setActiveSentence(activeSentence === idx ? null : idx)}
        />
      ))}
    </div>
  );
}

function SentenceSegment({ sentence, isActive, onToggle }) {
  const config     = getStatusConfig(sentence.status);
  const isNeutral  = sentence.status === "NEUTRAL" || !sentence.status;
  const hasSource  = !!sentence.source_url;
  const isClickable = !isNeutral;

  return (
    <div className="group">
      {/* Sentence text with conditional highlighting */}
      <span
        className={[
          "inline leading-relaxed text-base transition-all duration-200",
          !isNeutral && config.highlightBg,
          !isNeutral && config.highlightBdr,
          !isNeutral && "px-1 py-0.5 rounded-sm mr-0.5",
          isClickable && "cursor-pointer hover:opacity-80",
          isNeutral && "text-ats-text",
        ].filter(Boolean).join(" ")}
        onClick={isClickable ? onToggle : undefined}
        title={isClickable ? `Click to see source — ${config.label}` : undefined}
      >
        {/* Status dot for non-neutral sentences */}
        {!isNeutral && (
          <span
            className={`inline-block w-1.5 h-1.5 rounded-full mr-1.5 mb-0.5 ${config.dotColor}`}
          />
        )}
        {sentence.text}
        {/* Trailing space to prevent sentences running together */}
        {" "}
      </span>

      {/* Expandable source panel */}
      {isActive && (
        <div className="mt-2 mb-3 ml-2 animate-fade-up">
          <div className="card p-3 border-l-2 max-w-lg"
               style={{ borderLeftColor: getStatusConfig(sentence.status).dotColor.replace("bg-", "") }}>

            {/* Status header */}
            <div className="flex items-center gap-2 mb-2">
              <span className={config.badgeClass}>
                {config.icon} {config.label}
              </span>
              {sentence.from_cache !== undefined && (
                <span className="text-xs font-mono text-ats-muted">
                  {sentence.from_cache ? "cached" : "live check"}
                </span>
              )}
            </div>

            {/* Claim reference */}
            {sentence.claim_ref && (
              <p className="text-xs text-ats-muted font-mono mb-2 leading-relaxed">
                Matched claim: "{sentence.claim_ref}"
              </p>
            )}

            {/* Source link */}
            {hasSource ? (
              <a
                href={sentence.source_url}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-2 text-xs text-ats-cyan hover:underline font-mono break-all"
              >
                <span>↗</span>
                <span>{sentence.source_url}</span>
              </a>
            ) : (
              <p className="text-xs text-ats-muted font-mono">
                No source URL available for this claim.
              </p>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
```

---

### Task 7.3 — `SourceChain` Component (40 min)

A separate panel below the response that shows all claims as cards with their verification status. The "Source Chain" is the product's unique differentiator from ModelProof.

```jsx
// frontend/src/components/SourceChain.jsx
import { useState } from "react";
import { getStatusConfig } from "../utils/trustHelpers";

/**
 * Displays all extracted claims as a visual chain with status indicators.
 *
 * Props:
 *   claims {Array} - Array of ClaimResult objects from the API:
 *     { text, status, source_url, source_title }
 */
export default function SourceChain({ claims }) {
  if (!claims?.length) return null;

  const verifiedCount     = claims.filter(c => c.status === "VERIFIED").length;
  const uncertainCount    = claims.filter(c => c.status === "UNCERTAIN").length;
  const contradictedCount = claims.filter(c => c.status === "CONTRADICTED").length;

  return (
    <div className="card p-4 mt-4 animate-fade-up">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <span className="text-ats-cyan font-mono text-xs font-bold tracking-widest">
            SOURCE CHAIN
          </span>
          <span className="text-ats-muted font-mono text-xs">
            {claims.length} claim{claims.length !== 1 ? "s" : ""} extracted
          </span>
        </div>

        {/* Summary pills */}
        <div className="flex items-center gap-2">
          {verifiedCount > 0 && (
            <span className="badge-verified">{verifiedCount} verified</span>
          )}
          {uncertainCount > 0 && (
            <span className="badge-uncertain">{uncertainCount} uncertain</span>
          )}
          {contradictedCount > 0 && (
            <span className="badge-contradicted">{contradictedCount} contradicted</span>
          )}
        </div>
      </div>

      {/* Claim cards */}
      <div className="space-y-2">
        {claims.map((claim, idx) => (
          <ClaimCard key={idx} claim={claim} index={idx} />
        ))}
      </div>
    </div>
  );
}

function ClaimCard({ claim, index }) {
  const [expanded, setExpanded] = useState(false);
  const config   = getStatusConfig(claim.status);
  const hasSource = !!claim.source_url;

  return (
    <div
      className={`rounded-lg border p-3 transition-all duration-200 cursor-pointer hover:border-opacity-80 ${config.highlightBg}`}
      style={{ borderColor: `${config.dotColor.replace("bg-", "")}40` }}
      onClick={() => setExpanded(!expanded)}
    >
      {/* Claim header row */}
      <div className="flex items-start gap-3">
        {/* Index number */}
        <span className="font-mono text-xs text-ats-muted mt-0.5 flex-shrink-0 w-5">
          {index + 1}.
        </span>

        {/* Status dot */}
        <span className={`w-2 h-2 rounded-full mt-1.5 flex-shrink-0 ${config.dotColor}`} />

        {/* Claim text */}
        <p className="text-sm text-ats-text flex-1 leading-relaxed">
          {claim.text}
        </p>

        {/* Status badge */}
        <span className={`${config.badgeClass} flex-shrink-0`}>
          {config.icon} {config.label}
        </span>
      </div>

      {/* Expanded source details */}
      {expanded && (
        <div className="mt-3 ml-8 pl-3 border-l border-ats-border animate-fade-up">
          {hasSource ? (
            <div className="space-y-1">
              {claim.source_title && (
                <p className="text-xs text-ats-muted font-mono">
                  {claim.source_title}
                </p>
              )}
              <a
                href={claim.source_url}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-1.5 text-xs text-ats-cyan hover:underline font-mono break-all"
                onClick={(e) => e.stopPropagation()}
              >
                <span>↗</span>
                <span>{claim.source_url}</span>
              </a>
            </div>
          ) : (
            <p className="text-xs text-ats-muted font-mono">
              No web source found for this claim.
            </p>
          )}
        </div>
      )}
    </div>
  );
}
```

---

### ✅ Checkpoint 7 — Core Components Rendered (@ 17:00)

```jsx
// Paste into App.jsx for visual testing — remove after checkpoint passes

import TrustScoreMeter from "./components/TrustScoreMeter";
import SentenceText    from "./components/SentenceText";
import SourceChain     from "./components/SourceChain";

const MOCK_DATA = {
  trust_score: 78,
  sentences: [
    { text: "The Eiffel Tower was built in 1889 for the World's Fair.", status: "VERIFIED", source_url: "https://en.wikipedia.org/wiki/Eiffel_Tower", claim_ref: "Eiffel Tower built in 1889" },
    { text: "It stands 330 meters tall and was designed by Gustave Eiffel.", status: "VERIFIED", source_url: "https://www.toureiffel.paris", claim_ref: "stands 330 meters tall" },
    { text: "The tower was originally intended to be dismantled after 20 years.", status: "UNCERTAIN", source_url: null, claim_ref: "planned for demolition after 20 years" },
    { text: "Today it is the most visited paid monument in the world.", status: "NEUTRAL", source_url: null, claim_ref: null },
  ],
  claims: [
    { text: "Eiffel Tower built in 1889", status: "VERIFIED", source_url: "https://en.wikipedia.org/wiki/Eiffel_Tower", source_title: "Eiffel Tower — Wikipedia" },
    { text: "stands 330 meters tall", status: "VERIFIED", source_url: "https://www.toureiffel.paris", source_title: "Official Eiffel Tower site" },
    { text: "planned for demolition after 20 years", status: "UNCERTAIN", source_url: null, source_title: null },
  ]
};

function App() {
  return (
    <div className="min-h-screen p-8 max-w-2xl mx-auto space-y-6">
      <TrustScoreMeter score={MOCK_DATA.trust_score} />
      <SentenceText sentences={MOCK_DATA.sentences} />
      <SourceChain claims={MOCK_DATA.claims} />
    </div>
  );
}

export default App;
```

| Visual Check | Expected | If Failing |
|---|---|---|
| `TrustScoreMeter` animates from 0 to 78 | Smooth count-up animation | Check `useEffect` interval logic, verify `animated={true}` is default |
| Green/yellow sentence highlighting visible | Colored underlines/backgrounds on sentences | Check Tailwind `content` paths include `.jsx` files, check class names match config |
| Neutral sentences have no highlight | Plain text color | Check `status === "NEUTRAL"` guard in `SentenceSegment` |
| Click on highlighted sentence expands source panel | Source panel appears below sentence | Check `onToggle` and `isActive` logic in `SentenceSegment` |
| SourceChain renders all 3 claim cards | Cards with status badges visible | Check `claims` prop is passed correctly |
| Clicking claim card expands source URL | URL appears below claim | Check `expanded` state toggle and conditional render |

---

## 6. Phase 8 — Source Chain, Chat UX & Live Integration (17:00–20:00)

**Goal:** Wire everything together. The `ChatInput` captures queries, the `useVerify` hook fetches real data, all three core components render real API output, and the full demo flow works end-to-end.

---

### Task 8.1 — `ChatInput` Component (30 min)

```jsx
// frontend/src/components/ChatInput.jsx
import { useState, useRef, useEffect } from "react";

/**
 * Query input with submit on Enter or button click.
 *
 * Props:
 *   onSubmit  {function(query: string)} - Called with trimmed query string
 *   loading   {boolean}                 - Disables input while pipeline runs
 *   disabled  {boolean}                 - Hard disable
 */
export default function ChatInput({ onSubmit, loading = false, disabled = false }) {
  const [query, setQuery]     = useState("");
  const textareaRef           = useRef(null);
  const isDisabled            = loading || disabled;

  // Auto-focus on mount
  useEffect(() => {
    textareaRef.current?.focus();
  }, []);

  // Auto-resize textarea as user types
  useEffect(() => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = Math.min(el.scrollHeight, 160) + "px";
  }, [query]);

  const handleSubmit = () => {
    const trimmed = query.trim();
    if (!trimmed || isDisabled) return;
    onSubmit(trimmed);
    setQuery("");
    // Reset textarea height
    if (textareaRef.current) textareaRef.current.style.height = "auto";
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="card p-4">
      {/* Textarea */}
      <textarea
        ref={textareaRef}
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Ask anything — AI Trust Sentinel will verify it..."
        disabled={isDisabled}
        rows={1}
        className={[
          "w-full bg-transparent text-ats-text font-sans text-sm",
          "placeholder-ats-muted resize-none outline-none",
          "leading-relaxed min-h-[40px]",
          isDisabled && "opacity-50 cursor-not-allowed",
        ].filter(Boolean).join(" ")}
      />

      {/* Bottom bar: hints + submit button */}
      <div className="flex items-center justify-between mt-3 pt-3 border-t border-ats-border">
        <div className="flex items-center gap-3">
          <span className="text-xs text-ats-muted font-mono">
            Enter to submit · Shift+Enter for newline
          </span>
          {loading && (
            <span className="text-xs text-ats-cyan font-mono animate-pulse">
              ● Analyzing...
            </span>
          )}
        </div>

        <button
          onClick={handleSubmit}
          disabled={!query.trim() || isDisabled}
          className={[
            "px-4 py-2 rounded-lg font-mono text-xs font-bold tracking-wide",
            "transition-all duration-200",
            query.trim() && !isDisabled
              ? "bg-ats-cyan text-ats-bg hover:bg-opacity-90 cursor-pointer"
              : "bg-ats-border text-ats-muted cursor-not-allowed opacity-50",
          ].filter(Boolean).join(" ")}
        >
          {loading ? "Analyzing..." : "Verify →"}
        </button>
      </div>
    </div>
  );
}
```

---

### Task 8.2 — `LoadingState` & `ErrorState` Components (20 min)

```jsx
// frontend/src/components/LoadingState.jsx

export default function LoadingState() {
  const stages = [
    { label: "Calling primary model...",    color: "text-ats-cyan",   delay: "0ms"   },
    { label: "Evaluating confidence...",    color: "text-ats-purple", delay: "400ms" },
    { label: "Extracting key claims...",    color: "text-ats-yellow", delay: "900ms" },
    { label: "Fact-checking sources...",    color: "text-ats-green",  delay: "1400ms"},
    { label: "Computing Trust Score...",    color: "text-ats-cyan",   delay: "2000ms"},
  ];

  return (
    <div className="card p-6 space-y-4 animate-fade-up">
      {/* Pulsing header */}
      <div className="flex items-center gap-3">
        <div className="w-3 h-3 rounded-full bg-ats-cyan animate-pulse-dot" />
        <span className="font-mono text-sm text-ats-cyan font-bold tracking-widest">
          PIPELINE RUNNING
        </span>
      </div>

      {/* Stage indicators */}
      <div className="space-y-2">
        {stages.map((stage, i) => (
          <div
            key={i}
            className="flex items-center gap-3 opacity-0 animate-fade-up"
            style={{ animationDelay: stage.delay, animationFillMode: "both" }}
          >
            <div className={`w-1.5 h-1.5 rounded-full ${stage.color.replace("text-", "bg-")} animate-pulse-dot`}
                 style={{ animationDelay: stage.delay }} />
            <span className={`font-mono text-xs ${stage.color}`}>{stage.label}</span>
          </div>
        ))}
      </div>

      {/* Shimmer skeleton for where the response will appear */}
      <div className="space-y-2 mt-4">
        {[80, 95, 70, 88, 60].map((w, i) => (
          <div
            key={i}
            className="h-4 rounded"
            style={{
              width: `${w}%`,
              background: "linear-gradient(90deg, #1D304E 25%, #243A5C 50%, #1D304E 75%)",
              backgroundSize: "200% 100%",
              animation: `shimmer 1.5s infinite`,
              animationDelay: `${i * 100}ms`,
            }}
          />
        ))}
      </div>
    </div>
  );
}
```

```jsx
// frontend/src/components/ErrorState.jsx

export default function ErrorState({ message, onRetry }) {
  return (
    <div className="card p-5 border-ats-red border animate-fade-up">
      <div className="flex items-start gap-3">
        <span className="text-ats-red text-lg flex-shrink-0">⚠</span>
        <div className="flex-1">
          <p className="font-mono text-xs text-ats-red font-bold tracking-widest mb-1">
            PIPELINE ERROR
          </p>
          <p className="text-sm text-ats-text">{message}</p>
          {onRetry && (
            <button
              onClick={onRetry}
              className="mt-3 text-xs font-mono text-ats-cyan hover:underline"
            >
              ↻ Try again
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
```

---

### Task 8.3 — `ChatMessage` Container (25 min)

```jsx
// frontend/src/components/ChatMessage.jsx
import TrustScoreMeter from "./TrustScoreMeter";
import SentenceText    from "./SentenceText";
import SourceChain     from "./SourceChain";
import { formatLatency } from "../utils/trustHelpers";

/**
 * Full response container — wraps all three core components.
 *
 * Props:
 *   query   {string}        - The original user question
 *   data    {VerifyResponse} - Full API response object
 */
export default function ChatMessage({ query, data }) {
  if (!data) return null;

  return (
    <div className="space-y-4 animate-fade-up">
      {/* User query bubble */}
      <div className="flex justify-end">
        <div className="card px-4 py-3 max-w-lg border-ats-cyan/30">
          <p className="text-sm text-ats-text">{query}</p>
        </div>
      </div>

      {/* Response card */}
      <div className="card p-5">
        {/* Header row: Trust Score + meta */}
        <div className="flex items-start justify-between gap-6 mb-5">
          <div className="flex-1">
            {/* Meta line */}
            <div className="flex flex-wrap items-center gap-3 mb-3">
              <span className="text-xs font-mono text-ats-muted">
                AI Trust Sentinel
              </span>
              {data.verifier_used && (
                <span className="badge-verified">dual-LLM verified</span>
              )}
              {data.from_cache && (
                <span className="badge-neutral">⚡ from cache</span>
              )}
              {data.latency_ms && (
                <span className="text-xs font-mono text-ats-muted">
                  {formatLatency(data.latency_ms)}
                </span>
              )}
            </div>

            {/* Response text with sentence highlighting */}
            <SentenceText sentences={data.sentences} />
          </div>

          {/* Trust score meter on the right */}
          <div className="flex-shrink-0">
            <TrustScoreMeter score={data.trust_score} size={140} />
          </div>
        </div>

        {/* Source chain below */}
        <SourceChain claims={data.claims} />
      </div>
    </div>
  );
}
```

---

### Task 8.4 — `App.jsx` — Full Wiring (45 min)

```jsx
// frontend/src/App.jsx
import { useState } from "react";
import { useVerify }    from "./hooks/useVerify";
import ChatInput        from "./components/ChatInput";
import ChatMessage      from "./components/ChatMessage";
import LoadingState     from "./components/LoadingState";
import ErrorState       from "./components/ErrorState";

const SUGGESTED_QUERIES = [
  "Was Einstein really bad at math in school?",
  "Is the Great Wall of China visible from space?",
  "Did Napoleon Bonaparte have a short stature?",
  "Was the Eiffel Tower supposed to be permanent?",
];

export default function App() {
  const { verify, data, loading, error, reset } = useVerify();
  const [currentQuery, setCurrentQuery] = useState("");
  const [history, setHistory]           = useState([]);   // [{query, data}]

  const handleSubmit = async (query) => {
    setCurrentQuery(query);
    const result = await verify(query);
    if (result) {
      setHistory(prev => [{ query, data: result }, ...prev]);
    }
  };

  return (
    <div className="min-h-screen">
      {/* Top nav */}
      <header className="border-b border-ats-border bg-ats-surface/80 backdrop-blur-sm sticky top-0 z-10">
        <div className="max-w-3xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-2 h-2 rounded-full bg-ats-cyan animate-pulse-dot" />
            <span className="font-mono text-sm font-bold text-ats-cyan tracking-widest">
              AI TRUST SENTINEL
            </span>
          </div>
          <span className="font-mono text-xs text-ats-muted">
            The trust layer AI never gave you.
          </span>
        </div>
      </header>

      <main className="max-w-3xl mx-auto px-6 py-8 space-y-6">
        {/* Hero text — visible only before first query */}
        {!data && !loading && !error && history.length === 0 && (
          <div className="text-center py-12 space-y-4 animate-fade-up">
            <h1 className="text-4xl font-bold text-white font-sans tracking-tight">
              Ask anything.
              <br />
              <span className="text-ats-cyan">Know what to trust.</span>
            </h1>
            <p className="text-ats-muted font-mono text-sm max-w-md mx-auto leading-relaxed">
              Dual-LLM cross-verification · Real-time fact-checking ·
              Sentence-level trust scoring
            </p>

            {/* Suggested queries */}
            <div className="flex flex-wrap justify-center gap-2 mt-6">
              {SUGGESTED_QUERIES.map((q, i) => (
                <button
                  key={i}
                  onClick={() => handleSubmit(q)}
                  className="text-xs font-mono px-3 py-1.5 rounded-full
                             border border-ats-border text-ats-muted
                             hover:border-ats-cyan hover:text-ats-cyan
                             transition-all duration-200"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Current in-flight state */}
        {loading  && <LoadingState />}
        {error    && !loading && <ErrorState message={error} onRetry={() => reset()} />}
        {data     && !loading && <ChatMessage query={currentQuery} data={data} />}

        {/* Query history */}
        {history.length > 1 && (
          <div className="space-y-4">
            <div className="flex items-center gap-3">
              <div className="flex-1 h-px bg-ats-border" />
              <span className="text-xs font-mono text-ats-muted">Previous queries</span>
              <div className="flex-1 h-px bg-ats-border" />
            </div>
            {history.slice(1).map((item, i) => (
              <ChatMessage key={i} query={item.query} data={item.data} />
            ))}
          </div>
        )}

        {/* Input — always at bottom */}
        <div className="sticky bottom-6">
          <ChatInput
            onSubmit={handleSubmit}
            loading={loading}
          />
        </div>
      </main>
    </div>
  );
}
```

---

### ✅ Checkpoint 8 — Full End-to-End Demo Working (@ 20:00)

This is the critical acceptance test for Hours 8–20. Every item must pass before sleeping.

```
MANUAL DEMO TEST — Run through this sequence exactly:

1. Open http://localhost:5173 in browser
   ✓ Dark background visible
   ✓ "AI TRUST SENTINEL" header visible
   ✓ Hero text and suggested queries visible
   ✓ No console errors

2. Click a suggested query ("Was Einstein bad at math?")
   ✓ Query appears in input field and submits immediately
   ✓ LoadingState appears with animated stage indicators
   ✓ After 1–4 seconds: ChatMessage appears with real data
   ✓ TrustScoreMeter animates from 0 to actual score
   ✓ Sentences render with color highlighting
   ✓ At least some sentences have green or yellow underline

3. Click a highlighted sentence
   ✓ Source panel expands below that sentence
   ✓ Either a clickable source URL appears, or "No source found" message
   ✓ Clicking the URL opens the source in a new tab

4. Scroll down to SourceChain
   ✓ Claims are listed with status badges
   ✓ Clicking a claim card expands to show source URL

5. Submit a second query ("Did Napoleon have a short stature?")
   ✓ Previous result stays in history below
   ✓ New LoadingState appears
   ✓ New ChatMessage appears above history divider

6. Submit the first query again (exact same text)
   ✓ Response appears in < 200ms (from cache)
   ✓ "⚡ from cache" badge visible in ChatMessage header

7. Empty query
   ✓ Submit button stays disabled
   ✓ Pressing Enter with empty input does nothing
```

---

## 7. Master Checkpoint Summary

| Checkpoint | Time | Owner | Tests | Blocker? |
|---|---|---|---|---|
| **CP5** — Backend Hardening | 10:00 | Backend | Sentence segmentation in response, streaming endpoint live, latency < 3s | Yes |
| **CP6** — Frontend Foundation | 13:00 | Frontend | Dev server running, API call works from console, CORS not blocked | Yes |
| **CP7** — Core Components Rendered | 17:00 | Frontend | TrustScoreMeter animates, sentences highlight, SourceChain clicks | Yes |
| **CP8** — Full Demo Working | 20:00 | All | Complete manual test sequence passes top to bottom | Yes |

> ⚠️ **Checkpoint 8 is the hardest gate.** If the end-to-end demo is not working by 20:00, the team must debug together immediately. This is the minimum viable product for the hackathon. If CP8 fails, Hours 20–36 will be spent on bug fixes instead of polish.

---

## 8. Error Reference Handbook

---

### 8.1 Sentence Segmentation Errors

| Error | Cause | Fix |
|---|---|---|
| Entire response returned as one sentence | Regex not splitting on periods | Test `split_into_sentences()` standalone; check regex pattern handles your test input |
| Too many fragments (splitting mid-sentence) | Abbreviations breaking the regex | Add more abbreviations to the `abbreviations` list in `split_into_sentences()` |
| All sentences show status `NEUTRAL` | Overlap threshold too high | Lower `best_match_score >= 0.20` to `0.10` in `annotate_sentences()` |
| `sentences` key missing from response | Schema not updated | Add `sentences: List[SentenceAnnotation]` to `VerifyResponse` Pydantic model |
| `sentences` is empty list | Pipeline not calling segmenter | Check `split_into_sentences()` and `annotate_sentences()` are called in `run_verification_pipeline()` |

---

### 8.2 Streaming / SSE Errors

| Error | Cause | Fix |
|---|---|---|
| Streaming endpoint returns 422 | Wrong request body format | SSE endpoint takes POST body, not query params. Check curl command sends JSON body |
| Stream chunks buffered (arrive all at once) | Nginx/proxy buffering | Add `X-Accel-Buffering: no` header and `Cache-Control: no-cache` to `StreamingResponse` |
| `GeneratorExit` exception in server logs | Client disconnected early | Normal behavior — wrap generator body in `try/except GeneratorExit` |
| Events not parsed correctly | Frontend EventSource handling | For POST-based SSE use `fetch()` + `ReadableStream`, not `EventSource` (which only supports GET) |

---

### 8.3 React / Tailwind Errors

| Error | Cause | Fix |
|---|---|---|
| Tailwind classes not applying | `content` in `tailwind.config.js` doesn't include `*.jsx` | Update to `"./src/**/*.{js,ts,jsx,tsx}"` |
| Dark background not visible | Tailwind purging custom `ats-*` colors | Make sure custom colors are in `theme.extend.colors`, not inline `style={}` attributes |
| `Cannot read properties of undefined (reading 'map')` | Component receives `undefined` instead of array | Add optional chaining: `data?.sentences?.map(...)` and null checks before rendering |
| `useVerify is not a function` | Named export vs default export mismatch | Check `export function useVerify()` (named) and `import { useVerify }` (destructured) |
| CORS blocked in browser | FastAPI CORS not allowing 5173 | Add `"http://localhost:5173"` to `allow_origins` list alongside `"*"` |
| `Network Error` on API call | Backend not running | Run `uvicorn main:app --reload --port 8000` in backend directory |
| Textarea doesn't resize | `scrollHeight` read before render | Add `el.style.height = "auto"` before reading `scrollHeight` in the `useEffect` |
| Suggested queries don't submit | `onSubmit` handler missing | Check `ChatInput` receives `onSubmit` prop and calls it in `handleSubmit` |

---

### 8.4 State Management Errors

| Error | Cause | Fix |
|---|---|---|
| Old result flashes before new one loads | `data` not cleared on new query | Set `data: null` at the start of `verify()` in `useVerify` |
| Loading spinner never disappears | `loading` stays `true` after error | Ensure `loading: false` is set in both success and catch paths |
| History shows duplicate entries | `verify()` called twice | Check `onSubmit` not bound to both `onClick` and `onKeyDown` simultaneously |
| Cache badge not showing | `from_cache` not in response schema | Confirm `from_cache` field in `VerifyResponse` Pydantic model, confirm `cache.get_cached()` returns it |
| `TrustScoreMeter` doesn't re-animate | React not re-mounting component on new query | Add `key={currentQuery}` to `<TrustScoreMeter>` to force re-mount on each new response |

---

### 8.5 Integration Errors

| Error | Cause | Fix |
|---|---|---|
| `trust_label` or `trust_color` undefined | Not added to pipeline output | Add `trust_label = score_to_label(trust_score)` in pipeline, add to `VerifyResponse` schema |
| Sentence `status` is `None` | Backend returning null instead of string | Ensure `annotate_sentences()` always returns a string status, default `"NEUTRAL"` not `None` |
| Source URLs not opening | Missing `target="_blank"` on anchor | Add `target="_blank" rel="noopener noreferrer"` to all source link `<a>` tags |
| `latency_ms` shows very large numbers | Server clock issue | Check `time.time()` is captured at the true start of the pipeline, before cache check |
| API timeout from frontend | Backend pipeline > 30s | Check `asyncio.timeout(20)` is wrapping the full pipeline; verify Tavily `search_depth="basic"` |

---

## 9. Component API Contract

The exact props each component expects. Use this to coordinate between the backend team (defining the API response) and the frontend team (consuming it in components).

---

### `TrustScoreMeter`
```
Props:
  score    {number}   required  — Trust score 0-100
  size     {number}   optional  — Diameter in px, default 160
  animated {boolean}  optional  — Animate from 0, default true

Usage:
  <TrustScoreMeter score={data.trust_score} />
  <TrustScoreMeter score={82} size={120} animated={false} />
```

### `SentenceText`
```
Props:
  sentences {Array} required — Array of SentenceAnnotation objects:
    [
      {
        text:       string   — Sentence text
        status:     string   — "VERIFIED" | "UNCERTAIN" | "CONTRADICTED" | "NEUTRAL"
        claim_ref:  string   — Matching claim text (or null)
        source_url: string   — Source URL (or null)
      }
    ]

Usage:
  <SentenceText sentences={data.sentences} />
```

### `SourceChain`
```
Props:
  claims {Array} required — Array of ClaimResult objects:
    [
      {
        text:         string — Claim text
        status:       string — "VERIFIED" | "UNCERTAIN" | "CONTRADICTED"
        source_url:   string — Web source URL (or null)
        source_title: string — Page title (or null)
      }
    ]

Usage:
  <SourceChain claims={data.claims} />
```

### `ChatInput`
```
Props:
  onSubmit {function}  required — Called with (query: string) on submit
  loading  {boolean}   optional — Disables input during API call, default false
  disabled {boolean}   optional — Hard disable regardless of state, default false

Usage:
  <ChatInput onSubmit={handleSubmit} loading={isLoading} />
```

### `ChatMessage`
```
Props:
  query {string}        required — The original user question
  data  {VerifyResponse} required — Full API response object

Usage:
  <ChatMessage query={currentQuery} data={data} />
```

---

## 10. If You Fall Behind Schedule

---

### Decision Tree

```
Are you at Checkpoint 5 (10:00) with sentence segmentation not working?
├── YES → Return raw answer text as a single sentence object with status "NEUTRAL".
│         Frontend can render plain text without highlighting for now.
│         Come back to segmentation during Hours 20-36 polish phase.
└── NO ↓

Are you at Checkpoint 6 (13:00) with the React app not scaffolded?
├── YES → Use the absolute minimum: plain HTML + vanilla JS fetch().
│         A working API call from a plain HTML page is better than a
│         broken React app. You can add React during Hours 20-36.
└── NO ↓

Are you at Checkpoint 7 (17:00) with TrustScoreMeter not animating?
├── YES → Replace with a plain number display:
│         <div style={{color: data.trust_color}}>{data.trust_score}/100</div>
│         The number is what matters for the demo. Animation is polish.
└── NO ↓

Are you at Checkpoint 8 (20:00) with SourceChain not clickable?
├── YES → Make source URLs plain visible text links. Non-clickable source
│         display is still better than no source display.
│         Fix interactivity during Hours 20-36.
└── NO → You are on track. Hours 20-36 are polishing a working product.
```

---

### Minimum Viable Demo at Hour 20

If everything goes wrong and you must make hard cuts, this is the absolute floor — the minimum that still tells the product story:

```
MINIMUM DEMO (all cuts applied):

1. ChatInput — accepts query, calls API             [NEVER CUT]
2. Trust Score — big number on screen               [NEVER CUT]
3. AI answer displayed — even as plain text         [NEVER CUT]
4. At least one source URL visible somewhere        [NEVER CUT]

CAN CUT:
- Sentence-level highlighting       → show plain text instead
- TrustScoreMeter animation         → show static colored number
- SourceChain expand/collapse       → show flat non-interactive list
- History of previous queries       → just show current result
- LoadingState animation            → simple "Loading..." text
- Suggested queries on hero page    → remove entirely
```

---

### Absolute Priorities — Never Cut These

| Feature | Why |
|---|---|
| **Trust Score (0–100 number)** | This is the product's headline claim. A judge cannot evaluate the demo without it. |
| **At least one source URL** | This is your differentiator from ModelProof. If no source is visible, judges cannot distinguish you. |
| **Working API call from frontend** | A frontend that cannot talk to the backend is not a demo — it is a mockup. |
| **Real data — never fake it** | If you present mock data and a judge asks to type their own question, the demo dies instantly. Always use real API calls. |

---

*End of Core Pipeline Roadmap — AI Trust Sentinel v1.0*
*Prepared for: Hackathon Hours 8–20 | Track: AI/ML*
*Preceding document: Foundation Roadmap (Hours 0–8)*
*Following document: Polish & Deploy Roadmap (Hours 20–48)*
