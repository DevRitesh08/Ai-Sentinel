# AI Trust Sentinel — Deep Foundation Roadmap
### Hours 0–8 | Detailed Build Guide with Checkpoints & Error Detection

> **"The foundation you lay in the first 8 hours determines whether the next 40 hours are smooth execution or frantic debugging."**

---

## Table of Contents

1. [Overview & Goals](#1-overview--goals)
2. [Pre-Build Checklist](#2-pre-build-checklist)
3. [Phase 1 — Project Bootstrap (00:00–01:30)](#3-phase-1--project-bootstrap-0000--0130)
4. [Phase 2 — LLM Integration (01:30–03:30)](#4-phase-2--llm-integration-0130--0330)
5. [Phase 3 — Claim Extraction & Fact-Check (03:30–05:30)](#5-phase-3--claim-extraction--fact-check-0330--0530)
6. [Phase 4 — Redis Cache & Full Integration (05:30–08:00)](#6-phase-4--redis-cache--full-integration-0530--0800)
7. [Master Checkpoint Summary](#7-master-checkpoint-summary)
8. [Error Reference Handbook](#8-error-reference-handbook)
9. [Final API Contract](#9-final-api-contract)
10. [If You Fall Behind Schedule](#10-if-you-fall-behind-schedule)

---

## 1. Overview & Goals

### What Must Be Delivered by Hour 8

By the end of this foundation block, the backend must be a **fully operational, tested API** that the frontend team can consume without any further backend changes.

| Deliverable | Description | Done When |
|---|---|---|
| FastAPI server | Running, CORS-enabled, health check live | `GET /health` returns `{"status": "ok"}` |
| GPT-4o-mini integration | Returns answer + confidence score as JSON | JSON response with `answer` and `confidence` fields |
| Confidence Gate | Smart LLM escalation at threshold 75 | Logs show `gate=SKIP` or `gate=ESCALATE` correctly |
| Gemini Flash integration | Independent verifier, free tier | Returns non-empty response string |
| Claim extractor | Pulls 3–5 key assertions from LLM answer | Returns `{"claims": [...]}` array reliably |
| Tavily fact-check | Classifies each claim with source URL | Returns `VERIFIED`, `UNCERTAIN`, or `CONTRADICTED` |
| Trust Score engine | Aggregates all signals into 0–100 number | Validated against known-true and known-false queries |
| Redis cache | Hash-based query caching with TTL | Second identical query returns in < 50ms |
| End-to-end `/verify` | All stages wired into one clean endpoint | Returns complete schema with all fields |

### Architecture Diagram

```
User Query
    │
    ▼
┌─────────────────┐
│   Redis Cache   │ ──── HIT ────► Return cached result instantly ($0)
└────────┬────────┘
         │ MISS
         ▼
┌─────────────────────────────────────┐
│         GPT-4o-mini (Primary)       │
│   Returns: answer + confidence      │
└────────────────┬────────────────────┘
                 │
          ┌──────▼──────┐
          │  Confidence  │
          │    Gate      │
          │  threshold   │
          │     = 75     │
          └──┬───────┬───┘
        ≥ 75 │       │ < 75
             │       ▼
             │  ┌──────────────────┐
             │  │  Gemini Flash    │
             │  │  (Verifier)      │
             │  │  Free tier       │
             │  └────────┬─────────┘
             │           │
             └─────┬─────┘
                   │
                   ▼
        ┌──────────────────────┐
        │   Claim Extractor    │
        │   (GPT-4o-mini)      │
        │   Pulls 3–5 claims   │
        └──────────┬───────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │   Tavily Fact-Check  │
        │   Per extracted claim│
        │   Returns source URL │
        └──────────┬───────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │   Trust Score Engine │
        │   Aggregates signals │
        │   Outputs 0–100      │
        └──────────┬───────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │    Cache + Return    │
        │    Full JSON schema  │
        └──────────────────────┘
```

### Cost Budget for This Phase

| Service | Estimated cost during build | Notes |
|---|---|---|
| GPT-4o-mini | ~$0.01–0.05 total | Testing ~50–100 queries while building |
| Gemini Flash | $0.00 | Free tier |
| Tavily | $0.00 | Free tier (1,000 calls/month) |
| Upstash Redis | $0.00 | Free tier |
| Total for Hours 0–8 | **< $0.05** | You will not run out |

---

## 2. Pre-Build Checklist

Complete **every item** before writing a single line of application code. Skipping this causes cascading debugging pain.

### Accounts & API Keys

- [ ] OpenAI account — generate API key at platform.openai.com
- [ ] Google AI Studio account — generate Gemini API key at aistudio.google.com
- [ ] Tavily account — get free API key at tavily.com
- [ ] Upstash account — create free Redis database at upstash.com, copy `REDIS_URL` (starts with `rediss://`)
- [ ] Verify OpenAI key has credits loaded (check billing dashboard)

### Local Environment

- [ ] Python 3.11+ installed (`python --version`)
- [ ] Node.js 18+ installed (`node --version`)
- [ ] Git initialized in project folder
- [ ] `.env` file created (never committed)
- [ ] `.gitignore` includes `.env`, `venv/`, `node_modules/`, `__pycache__/`

### Ping Test All Keys Before Building

Run these quick tests **before writing any real code**. A dead key discovered at hour 5 is catastrophic.

```python
# test_keys.py — run this first, fix anything that fails
import os
from dotenv import load_dotenv
load_dotenv()

# Test 1: OpenAI
from openai import OpenAI
client = OpenAI()
res = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Say: KEY_OK"}],
    max_tokens=10
)
print("OpenAI:", res.choices[0].message.content)

# Test 2: Gemini
import google.generativeai as genai
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")
res = model.generate_content("Say: KEY_OK")
print("Gemini:", res.text)

# Test 3: Tavily
from tavily import TavilyClient
tc = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
res = tc.search("OpenAI GPT-4", max_results=1)
print("Tavily:", res["results"][0]["title"])

# Test 4: Redis
import redis
r = redis.from_url(os.getenv("REDIS_URL"))
r.set("test", "KEY_OK", ex=10)
print("Redis:", r.get("test").decode())
```

**Expected output:**
```
OpenAI: KEY_OK
Gemini: KEY_OK
Tavily: <any article title>
Redis:  KEY_OK
```

If any line fails — fix it before proceeding. Do not skip this step.

---

## 3. Phase 1 — Project Bootstrap (00:00–01:30)

**Goal:** A running server with proper folder structure, all dependencies installed, and CORS enabled.

---

### Task 1.1 — Folder Structure (15 min)

Create this exact structure. Consistency here saves hours of import confusion later.

```
ai-trust-sentinel/
├── backend/
│   ├── main.py                  # FastAPI app entry point
│   ├── requirements.txt         # All Python deps
│   ├── .env                     # API keys (never commit)
│   ├── routers/
│   │   └── verify.py            # /verify endpoint
│   ├── services/
│   │   ├── llm_primary.py       # GPT-4o-mini service
│   │   ├── llm_verifier.py      # Gemini Flash service
│   │   ├── claim_extractor.py   # Claim extraction logic
│   │   ├── fact_checker.py      # Tavily integration
│   │   ├── trust_score.py       # Score aggregation
│   │   └── cache.py             # Redis cache layer
│   └── models/
│       └── schemas.py           # Pydantic request/response models
└── frontend/
    ├── src/
    │   ├── components/
    │   │   ├── ChatInput.jsx
    │   │   ├── TrustScore.jsx
    │   │   ├── ResponseHighlight.jsx
    │   │   └── SourceChain.jsx
    │   └── services/
    │       └── api.js           # Axios calls to backend
    └── package.json
```

---

### Task 1.2 — Python Dependencies (15 min)

```
# backend/requirements.txt
fastapi==0.111.0
uvicorn[standard]==0.30.1
openai==1.35.0
google-generativeai==0.7.2
tavily-python==0.3.3
redis==5.0.7
python-dotenv==1.0.1
pydantic==2.7.4
httpx==0.27.0
```

```bash
cd backend
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**Verify:**
```bash
python -c "import fastapi, openai, google.generativeai, tavily, redis; print('All imports OK')"
```

---

### Task 1.3 — Environment File (10 min)

```bash
# backend/.env
OPENAI_API_KEY=sk-proj-...
GEMINI_API_KEY=AIzaSy...
TAVILY_API_KEY=tvly-...
REDIS_URL=rediss://default:...@...upstash.io:6379

# Tunable parameters (change these to optimize behavior)
CONFIDENCE_THRESHOLD=75
CACHE_TTL_SECONDS=3600
MAX_CLAIMS=5
MAX_TAVILY_RESULTS=3
```

> ⚠️ **Critical:** Upstash Redis URL must begin with `rediss://` (with double `s`). Using `redis://` will fail silently on the free tier.

---

### Task 1.4 — Pydantic Schemas (15 min)

Define the full request/response contract before writing any logic. This forces clarity on data shapes upfront and prevents schema drift.

```python
# backend/models/schemas.py
from pydantic import BaseModel
from typing import Optional, List
from enum import Enum

class ClaimStatus(str, Enum):
    VERIFIED      = "VERIFIED"
    UNCERTAIN     = "UNCERTAIN"
    CONTRADICTED  = "CONTRADICTED"

class VerifyRequest(BaseModel):
    query: str

class ClaimResult(BaseModel):
    text:         str
    status:       ClaimStatus
    source_url:   Optional[str] = None
    source_title: Optional[str] = None

class VerifyResponse(BaseModel):
    trust_score:    int                   # 0–100
    answer:         str                   # Primary LLM answer
    confidence:     int                   # Primary self-confidence 0–100
    verifier_used:  bool                  # Whether Gemini was called
    claims:         List[ClaimResult]     # Extracted + verified claims
    from_cache:     bool                  # Whether this was a cache hit
    latency_ms:     int                   # Total processing time
    error:          Optional[str] = None  # Populated only on failure
```

---

### Task 1.5 — FastAPI Server (35 min)

```python
# backend/main.py
import os
import time
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("main")

app = FastAPI(title="AI Trust Sentinel", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],           # Tighten to frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add request timing middleware
@app.middleware("http")
async def add_timing(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    elapsed = int((time.time() - start) * 1000)
    response.headers["X-Process-Time-Ms"] = str(elapsed)
    logger.info(f"{request.method} {request.url.path} → {response.status_code} ({elapsed}ms)")
    return response

@app.get("/health")
async def health():
    return {"status": "ok", "version": "1.0.0"}

# Import and register router (stub for now, fills in Phase 2)
from routers.verify import router
app.include_router(router, prefix="/api")
```

```python
# backend/routers/verify.py  (stub — will be filled in Phase 2)
from fastapi import APIRouter
from models.schemas import VerifyRequest, VerifyResponse

router = APIRouter()

@router.post("/verify", response_model=VerifyResponse)
async def verify_query(payload: VerifyRequest):
    # Stub: returns dummy response until Phase 4
    return VerifyResponse(
        trust_score=50,
        answer="Pipeline not yet implemented",
        confidence=50,
        verifier_used=False,
        claims=[],
        from_cache=False,
        latency_ms=0
    )
```

**Start the server:**
```bash
uvicorn main:app --reload --port 8000
```

---

### ✅ Checkpoint 1 — Environment Ready (@ 01:30)

Run each test. Do not proceed until all pass.

```bash
# Test 1: Server is running
curl http://localhost:8000/health
# Expected: {"status":"ok","version":"1.0.0"}

# Test 2: Stub /verify responds
curl -X POST http://localhost:8000/api/verify \
  -H "Content-Type: application/json" \
  -d '{"query": "test"}'
# Expected: JSON response with trust_score, answer, etc.

# Test 3: Env variables loaded
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
keys = ['OPENAI_API_KEY','GEMINI_API_KEY','TAVILY_API_KEY','REDIS_URL']
for k in keys:
    v = os.getenv(k)
    status = '✓' if v else '✗ MISSING'
    print(f'{status}  {k}')
"
```

| Test | Expected | If Failing |
|---|---|---|
| `/health` returns 200 | `{"status":"ok"}` | Check uvicorn is installed, port 8000 is free |
| `/api/verify` returns 200 | Stub JSON response | Check router import in main.py |
| All 4 env vars present | 4 × `✓` lines | Check `.env` is in `/backend/`, `load_dotenv()` called before `os.getenv()` |
| No import errors on start | Server starts cleanly | `source venv/bin/activate`, reinstall requirements |

---

## 4. Phase 2 — LLM Integration (01:30–03:30)

**Goal:** GPT-4o-mini returning structured answers with confidence scores; Gemini Flash running independently; smart Confidence Gate routing between them.

---

### Task 2.1 — Primary LLM Service — GPT-4o-mini (45 min)

The most important design decision here: **force JSON mode**. Without it, the model wraps output in markdown fences that crash JSON parsing.

```python
# backend/services/llm_primary.py
import os
import json
import logging
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
You are a precise factual assistant. Your job is to answer questions
accurately AND provide an honest self-assessment of your confidence.

Respond ONLY as valid JSON with this exact structure:
{
  "answer": "Your complete, well-reasoned answer here",
  "confidence": 82,
  "reasoning": "Brief explanation of your confidence level"
}

Confidence scoring rules:
- 90–100: Mathematical facts, universal scientific laws, verified historical events
- 75–89:  Well-documented facts with broad consensus
- 50–74:  Partial knowledge, some uncertainty, topic may have conflicting info
- 25–49:  Limited knowledge, significant uncertainty
- 0–24:   Largely unknown to you — say so clearly in the answer

CRITICAL: Be genuinely honest about uncertainty. Overconfident wrong answers
are worse than honest uncertainty. Never score above 75 for niche topics,
recent events, or anything you are not fully certain about.
"""

async def call_primary(query: str) -> dict:
    """
    Returns: {"answer": str, "confidence": int, "reasoning": str}
    Raises:  RuntimeError on API failure
    """
    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},  # CRITICAL — enforces JSON
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": query}
            ],
            max_tokens=800,
            temperature=0.3,   # Lower temp = more consistent confidence scoring
        )
        raw = response.choices[0].message.content
        result = json.loads(raw)

        # Validate required fields
        assert "answer"     in result, "Missing 'answer' field"
        assert "confidence" in result, "Missing 'confidence' field"
        assert 0 <= result["confidence"] <= 100, "Confidence out of range"

        logger.info(f"Primary LLM | confidence={result['confidence']} | query_len={len(query)}")
        return result

    except json.JSONDecodeError as e:
        logger.error(f"Primary LLM JSON parse error: {e}")
        raise RuntimeError("Primary LLM returned malformed JSON")
    except Exception as e:
        logger.error(f"Primary LLM API error: {e}")
        raise RuntimeError(f"Primary LLM failed: {str(e)}")
```

**Test it standalone:**
```python
import asyncio
from services.llm_primary import call_primary

async def test():
    # Should return confidence >= 90
    r1 = await call_primary("What is the capital of France?")
    print(f"High confidence test: {r1['confidence']} (expect ≥ 90)")

    # Should return confidence <= 70
    r2 = await call_primary("What was the exact population of Alexandria in 300 BC?")
    print(f"Low confidence test: {r2['confidence']} (expect ≤ 70)")

asyncio.run(test())
```

---

### Task 2.2 — Confidence Scoring Prompt Engineering (30 min)

The confidence prompt is critical IP. Spend time here testing and tuning.

**Test suite — run these and record scores:**

```python
# backend/services/prompt_calibration.py
# Run this to calibrate your confidence threshold

TEST_QUERIES = [
    # Expected HIGH confidence (≥ 85)
    ("What is 2 + 2?",                                   "MATH"),
    ("What element has atomic number 8?",                 "SCIENCE"),
    ("Who wrote Romeo and Juliet?",                       "LITERATURE"),

    # Expected MEDIUM confidence (50–84)
    ("What are the main causes of World War I?",          "HISTORY"),
    ("How does photosynthesis work?",                     "SCIENCE"),

    # Expected LOW confidence (< 50)
    ("What was the exact GDP of the Roman Empire?",       "OBSCURE"),
    ("What will the stock market do next week?",          "FUTURE"),
    ("What is the population of every city in India?",    "IMPOSSIBLE"),
]

# Run all tests and display table
import asyncio, json
from services.llm_primary import call_primary

async def calibrate():
    print(f"\n{'Query':<55} {'Type':<12} {'Score':<8} {'Status'}")
    print("-" * 90)
    for query, qtype in TEST_QUERIES:
        result = await call_primary(query)
        score = result["confidence"]
        status = "✓" if (
            (qtype in ["MATH", "SCIENCE", "LITERATURE"] and score >= 85) or
            (qtype == "HISTORY" and 50 <= score <= 85) or
            (qtype in ["OBSCURE", "FUTURE", "IMPOSSIBLE"] and score < 60)
        ) else "✗ RECALIBRATE"
        print(f"{query[:53]:<55} {qtype:<12} {score:<8} {status}")

asyncio.run(calibrate())
```

**If scores are miscalibrated:**

| Problem | Fix |
|---|---|
| All scores cluster at 95–100 | Strengthen prompt: add "Most topics should score 60–80. Reserve 90+ for absolute certainties only." |
| All scores cluster at 50–60 | Model is being too conservative. Add examples of high-confidence topics in the system prompt. |
| Scores jump randomly | Lower temperature to 0.1. Consistency matters more than accuracy here. |
| Score correlates with answer length, not certainty | Add to prompt: "Confidence reflects your certainty about factual accuracy, NOT your completeness or answer length." |

---

### Task 2.3 — Verifier LLM Service — Gemini Flash (35 min)

```python
# backend/services/llm_verifier.py
import os
import logging
import google.generativeai as genai

logger = logging.getLogger(__name__)
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

VERIFIER_SYSTEM = """
You are an independent factual verifier. Answer the question directly and
accurately. Be concise. Do not add caveats or disclaimers unless genuinely
important. Your answer will be compared against another AI's answer to
detect inconsistencies.
"""

async def call_verifier(query: str) -> dict:
    """
    Returns: {"answer": str}
    Falls back to Ollama if Gemini fails.
    """
    try:
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=VERIFIER_SYSTEM
        )
        response = model.generate_content(
            query,
            generation_config=genai.GenerationConfig(
                temperature=0.3,
                max_output_tokens=600,
            )
        )
        answer = response.text.strip()
        logger.info(f"Verifier LLM | answer_len={len(answer)}")
        return {"answer": answer}

    except Exception as e:
        logger.warning(f"Gemini failed ({e}), attempting Ollama fallback")
        return await _call_ollama_fallback(query)


async def _call_ollama_fallback(query: str) -> dict:
    """
    Local Llama 3 via Ollama — zero API cost, works offline.
    Requires: ollama pull llama3 (run once before hackathon)
    """
    import httpx
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "llama3",
                    "prompt": query,
                    "stream": False,
                    "options": {"temperature": 0.3}
                }
            )
            data = response.json()
            return {"answer": data["response"].strip()}
    except Exception as e:
        logger.error(f"Ollama fallback also failed: {e}")
        return {"answer": None}  # Graceful degradation — pipeline continues without verifier
```

> 📌 **Pre-hackathon:** Run `ollama pull llama3` once on the team's main laptop. The model is ~4.7GB — do NOT try to download it on hackathon WiFi.

---

### Task 2.4 — Confidence Gate Logic (30 min)

```python
# backend/services/gate.py
import os
import logging
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)
THRESHOLD = int(os.getenv("CONFIDENCE_THRESHOLD", "75"))


def should_escalate(confidence: int) -> bool:
    """Returns True if the primary model's confidence warrants a second opinion."""
    decision = confidence < THRESHOLD
    logger.info(f"Gate decision: confidence={confidence}, threshold={THRESHOLD}, escalate={decision}")
    return decision


def calculate_consistency_score(answer_a: str, answer_b: str) -> float:
    """
    Returns a 0.0–1.0 similarity score between two answers.
    High score = models agree = lower hallucination risk.
    Low score  = models disagree = higher hallucination risk.
    """
    # Normalize both answers
    a = answer_a.lower().strip()
    b = answer_b.lower().strip()

    # Use sequence matching as a simple baseline
    # For production: replace with cosine similarity on embeddings
    ratio = SequenceMatcher(None, a, b).ratio()

    logger.info(f"Consistency score: {ratio:.3f}")
    return ratio


def interpret_consistency(score: float) -> str:
    """Human-readable interpretation of consistency score."""
    if score >= 0.8:  return "HIGH_AGREEMENT"
    if score >= 0.5:  return "PARTIAL_AGREEMENT"
    return "SIGNIFICANT_DIVERGENCE"
```

---

### ✅ Checkpoint 2 — LLM Services Verified (@ 02:30)

```bash
# Quick integration test
python -c "
import asyncio
from services.llm_primary import call_primary
from services.llm_verifier import call_verifier
from services.gate import should_escalate, calculate_consistency_score

async def test():
    q = 'What is the boiling point of water at sea level?'

    primary = await call_primary(q)
    print(f'Primary confidence: {primary[\"confidence\"]}')
    print(f'Gate decision: {should_escalate(primary[\"confidence\"])}')

    verifier = await call_verifier(q)
    print(f'Verifier answer length: {len(verifier[\"answer\"])}')

    score = calculate_consistency_score(primary['answer'], verifier['answer'])
    print(f'Consistency score: {score:.2f}')
    print('ALL CHECKS PASSED' if primary['confidence'] > 0 and verifier['answer'] else 'FAIL')

asyncio.run(test())
"
```

| Check | Expected | Critical? |
|---|---|---|
| Primary confidence for boiling point | ≥ 85 | Yes |
| Gate returns `False` (skip) for above | Gate says no escalation needed | Yes |
| Gemini returns non-empty answer | Any text > 20 chars | Yes |
| Consistency score for same factual question | ≥ 0.5 | No (some variance expected) |
| No exceptions raised | Clean run | Yes |

---

### ✅ Checkpoint 3 — Gate Logic Verified (@ 03:30)

```bash
python -c "
import asyncio
from services.llm_primary import call_primary
from services.gate import should_escalate

async def test_gate():
    # HIGH confidence → should NOT escalate
    high = await call_primary('What is the chemical formula for water?')
    assert high['confidence'] >= 75, f'Expected high confidence, got {high[\"confidence\"]}'
    assert not should_escalate(high['confidence']), 'Gate should skip for high confidence'
    print(f'✓ High confidence ({high[\"confidence\"]}) → gate SKIPS Gemini correctly')

    # LOW confidence → SHOULD escalate
    low = await call_primary('What exact words did Julius Caesar say on March 15, 44 BC?')
    if low['confidence'] < 75:
        assert should_escalate(low['confidence']), 'Gate should escalate for low confidence'
        print(f'✓ Low confidence ({low[\"confidence\"]}) → gate ESCALATES to Gemini correctly')
    else:
        print(f'⚠ Model surprisingly confident ({low[\"confidence\"]}) — retune prompt if this persists')

asyncio.run(test_gate())
"
```

---

## 5. Phase 3 — Claim Extraction & Fact-Check (03:30–05:30)

**Goal:** Extract the key factual assertions from any AI answer, fact-check each one against live web sources, and aggregate results into a trust score.

---

### Task 3.1 — Claim Extractor (35 min)

```python
# backend/services/claim_extractor.py
import os
import json
import logging
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MAX_CLAIMS = int(os.getenv("MAX_CLAIMS", "5"))

EXTRACTION_PROMPT = f"""
You are a claim extraction specialist. Given a piece of text, extract the
{MAX_CLAIMS} most specific, independently verifiable factual claims.

Rules for extraction:
1. Only extract claims with concrete, checkable facts (names, dates, numbers, events)
2. Exclude opinions, predictions, and general statements
3. Exclude meta-commentary ("This is an interesting topic...")
4. Each claim must be self-contained — understandable without the original text
5. If fewer than 3 good claims exist, return only what is genuinely factual

Respond ONLY as valid JSON:
{{"claims": ["specific claim 1", "specific claim 2", "specific claim 3"]}}
"""

async def extract_claims(text: str) -> list[str]:
    """
    Returns a list of 1–5 factual claim strings extracted from text.
    Always returns a list, never raises — falls back to [full_text] on error.
    """
    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": EXTRACTION_PROMPT},
                {"role": "user",   "content": f"Extract claims from:\n\n{text}"}
            ],
            max_tokens=400,
            temperature=0.1,   # Low temp for consistent extraction
        )
        raw = json.loads(response.choices[0].message.content)
        claims = raw.get("claims", [])

        if not claims:
            logger.warning("Claim extractor returned empty list — using full text as fallback")
            return [text[:300]]  # Fallback: treat entire answer as one claim

        logger.info(f"Extracted {len(claims)} claims")
        return claims[:MAX_CLAIMS]

    except Exception as e:
        logger.error(f"Claim extraction failed: {e} — using fallback")
        return [text[:300]]  # Never fail silently — always return something


def validate_claims(claims: list[str]) -> list[str]:
    """Remove empty, too-short, or duplicate claims."""
    seen = set()
    valid = []
    for claim in claims:
        claim = claim.strip()
        if len(claim) < 10:
            continue
        key = claim.lower()[:50]
        if key in seen:
            continue
        seen.add(key)
        valid.append(claim)
    return valid
```

---

### Task 3.2 — Tavily Fact-Checker (45 min)

```python
# backend/services/fact_checker.py
import os
import asyncio
import logging
from tavily import TavilyClient
from models.schemas import ClaimResult, ClaimStatus

logger = logging.getLogger(__name__)
MAX_RESULTS = int(os.getenv("MAX_TAVILY_RESULTS", "3"))

# Synchronous Tavily client (wrap in thread executor for async use)
tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))


async def fact_check_claim(claim: str) -> ClaimResult:
    """
    Fact-checks a single claim against web sources.
    Returns a ClaimResult with status and source URL.
    Never raises — returns UNCERTAIN on any failure.
    """
    try:
        # Tavily is synchronous — run in thread executor to avoid blocking
        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(
            None,
            lambda: tavily_client.search(
                query=claim,
                max_results=MAX_RESULTS,
                search_depth="basic"   # Use "advanced" for better results (costs more credits)
            )
        )

        if not results or not results.get("results"):
            logger.warning(f"No Tavily results for claim: {claim[:50]}")
            return ClaimResult(
                text=claim,
                status=ClaimStatus.UNCERTAIN,
                source_url=None,
                source_title="No sources found"
            )

        top_result = results["results"][0]
        source_url   = top_result.get("url", "")
        source_title = top_result.get("title", "")
        source_body  = top_result.get("content", "")

        # Classify the claim based on source content relevance
        status = classify_claim(claim, source_body)

        logger.info(f"Claim: '{claim[:40]}...' → {status} | source: {source_url[:50]}")
        return ClaimResult(
            text=claim,
            status=status,
            source_url=source_url,
            source_title=source_title
        )

    except Exception as e:
        logger.error(f"Fact-check failed for '{claim[:40]}': {e}")
        return ClaimResult(
            text=claim,
            status=ClaimStatus.UNCERTAIN,
            source_url=None,
            source_title="Fact-check unavailable"
        )


def classify_claim(claim: str, source_content: str) -> ClaimStatus:
    """
    Determines VERIFIED / UNCERTAIN / CONTRADICTED based on
    overlap between the claim and source content.

    This is a heuristic — for production, replace with an LLM-based
    classification call for higher accuracy.
    """
    claim_words  = set(claim.lower().split())
    source_words = set(source_content.lower().split())
    overlap = len(claim_words & source_words) / max(len(claim_words), 1)

    if overlap >= 0.35:
        return ClaimStatus.VERIFIED
    if overlap >= 0.15:
        return ClaimStatus.UNCERTAIN
    return ClaimStatus.CONTRADICTED


async def fact_check_all_claims(claims: list[str]) -> list[ClaimResult]:
    """
    Fact-checks all claims concurrently for speed.
    Returns results in the same order as input claims.
    """
    tasks = [fact_check_claim(c) for c in claims]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Replace any exceptions with UNCERTAIN fallback
    clean_results = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            logger.error(f"Fact-check task {i} raised: {result}")
            clean_results.append(ClaimResult(
                text=claims[i],
                status=ClaimStatus.UNCERTAIN,
                source_url=None
            ))
        else:
            clean_results.append(result)

    return clean_results
```

---

### Task 3.3 — Trust Score Engine (40 min)

The core algorithm. Every signal feeds into this function.

```python
# backend/services/trust_score.py
import logging
from models.schemas import ClaimResult, ClaimStatus

logger = logging.getLogger(__name__)

# Signal weights — must sum to 1.0
WEIGHT_CONFIDENCE   = 0.30   # Primary LLM self-assessment
WEIGHT_CONSISTENCY  = 0.25   # LLM-to-LLM agreement (only when gate triggered)
WEIGHT_FACT_CHECK   = 0.45   # Web source verification (most reliable)

# Score penalties
PENALTY_CONTRADICTED = 15    # Deducted per CONTRADICTED claim
PENALTY_UNCERTAIN    = 5     # Deducted per UNCERTAIN claim
BONUS_VERIFIED       = 3     # Added per VERIFIED claim (small reward for clean claims)


def calculate_trust_score(
    primary_confidence: int,
    consistency_score:  float,          # 0.0–1.0, None if gate was skipped
    fact_results:       list[ClaimResult],
    verifier_used:      bool
) -> int:
    """
    Aggregates pipeline signals into a single Trust Score (0–100).

    Returns: int between 0 and 100
    """
    score = 100.0
    breakdown = {}

    # ── Signal 1: Primary model confidence ───────────────────────────────
    confidence_deduction = (100 - primary_confidence) * WEIGHT_CONFIDENCE
    score -= confidence_deduction
    breakdown["confidence_deduction"] = round(confidence_deduction, 1)

    # ── Signal 2: LLM consistency (only when verifier was used) ──────────
    if verifier_used and consistency_score is not None:
        consistency_deduction = (1.0 - consistency_score) * (100 * WEIGHT_CONSISTENCY)
        score -= consistency_deduction
        breakdown["consistency_deduction"] = round(consistency_deduction, 1)
    else:
        breakdown["consistency_deduction"] = 0  # Gate skipped, no penalty

    # ── Signal 3: Fact-check results ─────────────────────────────────────
    fact_deduction = 0
    fact_bonus     = 0

    for result in fact_results:
        if result.status == ClaimStatus.CONTRADICTED:
            fact_deduction += PENALTY_CONTRADICTED
        elif result.status == ClaimStatus.UNCERTAIN:
            fact_deduction += PENALTY_UNCERTAIN
        elif result.status == ClaimStatus.VERIFIED:
            fact_bonus += BONUS_VERIFIED

    score -= fact_deduction
    score += fact_bonus
    breakdown["fact_check_deduction"] = fact_deduction
    breakdown["fact_check_bonus"]     = fact_bonus

    # ── Clamp and finalize ────────────────────────────────────────────────
    final_score = max(0, min(100, int(score)))
    breakdown["final_score"] = final_score

    logger.info(f"Trust Score breakdown: {breakdown}")
    return final_score


def score_to_label(score: int) -> str:
    """Human-readable label for the trust score."""
    if score >= 85: return "HIGH CONFIDENCE"
    if score >= 65: return "MODERATE CONFIDENCE"
    if score >= 45: return "LOW CONFIDENCE"
    return "UNRELIABLE — VERIFY MANUALLY"


def score_to_color(score: int) -> str:
    """Hex color for the frontend to use when rendering the score."""
    if score >= 85: return "#00FF9D"   # Green
    if score >= 65: return "#FFD166"   # Yellow
    if score >= 45: return "#FF9A3C"   # Orange
    return "#FF4F6A"                   # Red
```

---

### ✅ Checkpoint 4 — Fact-Check Pipeline Live (@ 04:30)

```bash
python -c "
import asyncio
from services.claim_extractor import extract_claims, validate_claims
from services.fact_checker import fact_check_all_claims

async def test():
    test_text = '''
    The Eiffel Tower was built in 1889 for the World's Fair in Paris.
    It stands 330 meters tall and was designed by Gustave Eiffel.
    It was originally intended to be dismantled after 20 years.
    '''
    claims = await extract_claims(test_text)
    claims = validate_claims(claims)
    print(f'Extracted {len(claims)} claims:')
    for c in claims: print(f'  - {c}')

    results = await fact_check_all_claims(claims)
    print()
    for r in results:
        print(f'  [{r.status}] {r.text[:50]}...')
        if r.source_url: print(f'           → {r.source_url}')

asyncio.run(test())
"
```

| Test | Expected | If Failing |
|---|---|---|
| Extraction returns 3–5 claims | List of specific assertions | Check system prompt is emphasizing specificity |
| At least 1 `VERIFIED` claim for Eiffel Tower query | Status = VERIFIED | Tavily keyword overlap may need lowering; check `classify_claim()` threshold |
| Known false claim returns `CONTRADICTED` | Test: "Einstein failed math in school" → CONTRADICTED | Overlap threshold in `classify_claim()` may need adjusting |
| No exceptions raised on API failure | Falls back to UNCERTAIN | Check `try/except` in `fact_check_claim()` |

---

### ✅ Checkpoint 5 — Trust Score Validated (@ 05:30)

```bash
python -c "
import asyncio
from services.llm_primary import call_primary
from services.claim_extractor import extract_claims, validate_claims
from services.fact_checker import fact_check_all_claims
from services.trust_score import calculate_trust_score, score_to_label

async def test():
    queries = [
        ('Water boils at 100 degrees Celsius at sea level.', 'HIGH'),
        ('The moon is made entirely of green cheese.', 'LOW'),
    ]
    for q, expected in queries:
        primary = await call_primary(q)
        claims  = validate_claims(await extract_claims(primary['answer']))
        facts   = await fact_check_all_claims(claims)
        score   = calculate_trust_score(
            primary_confidence=primary['confidence'],
            consistency_score=None,
            fact_results=facts,
            verifier_used=False
        )
        label = score_to_label(score)
        result = '✓' if (expected=='HIGH' and score>=65) or (expected=='LOW' and score<65) else '✗'
        print(f'{result} [{expected} expected] Score={score} | {label}')

asyncio.run(test())
"
```

---

## 6. Phase 4 — Redis Cache & Full Integration (05:30–08:00)

**Goal:** Wire all services into a single endpoint, add the Redis cache layer, optimize with parallel async execution, and harden with error handling.

---

### Task 4.1 — Redis Cache Service (45 min)

```python
# backend/services/cache.py
import os
import json
import hashlib
import logging
import redis

logger = logging.getLogger(__name__)
CACHE_TTL = int(os.getenv("CACHE_TTL_SECONDS", "3600"))

# Initialize Redis client — gracefully disabled if connection fails
try:
    r = redis.from_url(os.getenv("REDIS_URL"), decode_responses=True)
    r.ping()  # Test connection immediately
    logger.info("Redis connected successfully")
    REDIS_AVAILABLE = True
except Exception as e:
    logger.warning(f"Redis unavailable ({e}) — caching disabled, pipeline will still work")
    REDIS_AVAILABLE = False
    r = None


def make_cache_key(query: str) -> str:
    """Generates a stable, normalized cache key for any query."""
    normalized = query.lower().strip()
    return "ats:query:" + hashlib.md5(normalized.encode()).hexdigest()


def get_cached(query: str) -> dict | None:
    """Returns cached result dict or None if not found."""
    if not REDIS_AVAILABLE:
        return None
    try:
        key  = make_cache_key(query)
        data = r.get(key)
        if data:
            logger.info(f"Cache HIT for query: '{query[:40]}'")
            result = json.loads(data)
            result["from_cache"] = True
            return result
        logger.info(f"Cache MISS for query: '{query[:40]}'")
        return None
    except Exception as e:
        logger.warning(f"Cache read failed: {e}")
        return None


def set_cached(query: str, result: dict) -> None:
    """Stores result in cache with TTL. Never raises."""
    if not REDIS_AVAILABLE:
        return
    try:
        key  = make_cache_key(query)
        data = json.dumps(result)
        r.setex(key, CACHE_TTL, data)
        logger.info(f"Cached query '{query[:40]}' for {CACHE_TTL}s")
    except Exception as e:
        logger.warning(f"Cache write failed: {e} — continuing without cache")


def get_cache_stats() -> dict:
    """Returns basic cache stats for debugging."""
    if not REDIS_AVAILABLE:
        return {"status": "disabled"}
    try:
        keys = r.keys("ats:query:*")
        return {"status": "connected", "cached_queries": len(keys)}
    except Exception:
        return {"status": "error"}
```

---

### Task 4.2 — Full Pipeline Orchestrator (45 min)

```python
# backend/services/pipeline.py
import time
import asyncio
import logging
from services.llm_primary    import call_primary
from services.llm_verifier   import call_verifier
from services.gate           import should_escalate, calculate_consistency_score
from services.claim_extractor import extract_claims, validate_claims
from services.fact_checker   import fact_check_all_claims
from services.trust_score    import calculate_trust_score, score_to_label, score_to_color
from services.cache          import get_cached, set_cached
from models.schemas          import VerifyResponse, ClaimResult, ClaimStatus

logger = logging.getLogger(__name__)


async def run_verification_pipeline(query: str) -> VerifyResponse:
    """
    Master orchestration function. Runs the full 7-stage pipeline.
    Returns a complete VerifyResponse. Never raises.
    """
    start_time = time.time()

    # ── Stage 1: Cache check ─────────────────────────────────────────────
    cached = get_cached(query)
    if cached:
        return VerifyResponse(**cached)

    # ── Stage 2: Primary LLM call ────────────────────────────────────────
    try:
        primary = await call_primary(query)
    except Exception as e:
        logger.error(f"Pipeline failed at primary LLM: {e}")
        return VerifyResponse(
            trust_score=0, answer="Service temporarily unavailable.",
            confidence=0, verifier_used=False, claims=[],
            from_cache=False, latency_ms=0,
            error=str(e)
        )

    # ── Stage 3: Confidence gate decision ────────────────────────────────
    escalate = should_escalate(primary["confidence"])

    # ── Stage 4 & 5: Parallel — Verifier LLM + Claim extraction ─────────
    # Run claim extraction in parallel with verifier call (if triggered)
    verifier_task = call_verifier(query) if escalate else asyncio.sleep(0, result=None)
    extractor_task = extract_claims(primary["answer"])

    verifier_raw, raw_claims = await asyncio.gather(
        verifier_task,
        extractor_task,
        return_exceptions=True
    )

    # Handle potential exceptions from parallel tasks
    verifier_answer  = verifier_raw["answer"] if isinstance(verifier_raw, dict) else None
    verifier_used    = escalate and verifier_answer is not None
    claims           = validate_claims(raw_claims if isinstance(raw_claims, list) else [])

    # ── Stage 5: Calculate consistency score ─────────────────────────────
    consistency = None
    if verifier_used and verifier_answer:
        consistency = calculate_consistency_score(primary["answer"], verifier_answer)

    # ── Stage 6: Fact-check all claims (concurrent) ──────────────────────
    fact_results = await fact_check_all_claims(claims) if claims else []

    # ── Stage 7: Trust score + finalize ──────────────────────────────────
    trust_score = calculate_trust_score(
        primary_confidence=primary["confidence"],
        consistency_score=consistency,
        fact_results=fact_results,
        verifier_used=verifier_used
    )

    elapsed_ms = int((time.time() - start_time) * 1000)

    result = VerifyResponse(
        trust_score   = trust_score,
        answer        = primary["answer"],
        confidence    = primary["confidence"],
        verifier_used = verifier_used,
        claims        = fact_results,
        from_cache    = False,
        latency_ms    = elapsed_ms,
    )

    # Cache result for future identical queries
    set_cached(query, result.model_dump())

    logger.info(
        f"Pipeline complete | score={trust_score} | verifier={verifier_used} "
        f"| claims={len(fact_results)} | latency={elapsed_ms}ms | cached=True"
    )

    return result
```

---

### Task 4.3 — Wire the /verify Endpoint (30 min)

```python
# backend/routers/verify.py  — FINAL VERSION
import logging
from fastapi import APIRouter, HTTPException
from models.schemas import VerifyRequest, VerifyResponse
from services.pipeline import run_verification_pipeline
from services.cache import get_cache_stats

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/verify", response_model=VerifyResponse)
async def verify_query(payload: VerifyRequest):
    """
    Main verification endpoint. Accepts a query, runs the full trust pipeline,
    returns an enriched response with trust score, claims, and source chain.
    """
    query = payload.query.strip()

    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    if len(query) > 2000:
        raise HTTPException(status_code=400, detail="Query too long (max 2000 chars)")

    logger.info(f"Verifying: '{query[:60]}'")
    return await run_verification_pipeline(query)


@router.get("/cache/stats")
async def cache_stats():
    """Debug endpoint — shows cache status and entry count."""
    return get_cache_stats()
```

---

### Task 4.4 — Parallel Async Optimization (30 min)

Add `asyncio.timeout()` guards to prevent any single slow API from stalling the whole pipeline.

```python
# Add these timeout guards inside run_verification_pipeline()
# Wrap each external call section:

import asyncio

# Timeout the entire pipeline
async def run_verification_pipeline(query: str) -> VerifyResponse:
    try:
        async with asyncio.timeout(20):  # 20 second hard timeout
            # ... pipeline logic ...
    except asyncio.TimeoutError:
        logger.error("Pipeline timed out after 20s")
        return VerifyResponse(
            trust_score=0, answer="Request timed out. Please try again.",
            confidence=0, verifier_used=False, claims=[],
            from_cache=False, latency_ms=20000,
            error="Pipeline timeout"
        )
```

---

### ✅ Checkpoint 6 — Cache Verified (@ 06:30)

```bash
# Test 1: First request (should be slow — hitting APIs)
time curl -s -X POST http://localhost:8000/api/verify \
  -H "Content-Type: application/json" \
  -d '{"query": "Who invented the telephone?"}' \
  | python -m json.tool | grep -E '"from_cache"|"latency_ms"|"trust_score"'

# Test 2: Same request (should be instant — from cache)
time curl -s -X POST http://localhost:8000/api/verify \
  -H "Content-Type: application/json" \
  -d '{"query": "Who invented the telephone?"}' \
  | python -m json.tool | grep -E '"from_cache"|"latency_ms"|"trust_score"'

# Test 3: Check cache stats
curl http://localhost:8000/api/cache/stats
```

| Test | Expected | If Failing |
|---|---|---|
| First request latency | 800–3000ms | Acceptable range |
| Second request `from_cache` | `true` | Check Redis URL uses `rediss://`, check `set_cached()` is being called |
| Second request latency | < 100ms | Cache write may have failed silently — check logs |
| Cache stats `cached_queries` | ≥ 1 | Check Redis connection in logs |

---

### ✅ Checkpoint 7 — Foundation Complete (@ 08:00)

This is the full acceptance test. Run every check before handing the API to the frontend team.

```bash
# Full acceptance test suite
python -c "
import asyncio, httpx, json

BASE = 'http://localhost:8000'

async def run_all_tests():
    async with httpx.AsyncClient(timeout=30) as client:
        passed = 0
        failed = 0

        def check(name, condition, got):
            nonlocal passed, failed
            if condition:
                print(f'  ✓ {name}')
                passed += 1
            else:
                print(f'  ✗ {name} | got: {got}')
                failed += 1

        print('=== CHECKPOINT 7: Foundation Acceptance Tests ===')
        print()

        # 1. Health check
        print('[1] Server health')
        r = await client.get(f'{BASE}/health')
        check('Health returns 200', r.status_code == 200, r.status_code)
        check('Status is ok', r.json()['status'] == 'ok', r.json())

        # 2. Basic verify
        print()
        print('[2] Basic verification')
        r = await client.post(f'{BASE}/api/verify', json={'query': 'What is the speed of light?'})
        data = r.json()
        check('Returns 200', r.status_code == 200, r.status_code)
        check('Has trust_score', 'trust_score' in data, data.keys())
        check('trust_score in range 0-100', 0 <= data.get('trust_score', -1) <= 100, data.get('trust_score'))
        check('Has answer', bool(data.get('answer')), data.get('answer', '')[:20])
        check('Has confidence', 'confidence' in data, data.keys())
        check('Has claims list', isinstance(data.get('claims'), list), type(data.get('claims')))
        check('Has from_cache', 'from_cache' in data, data.keys())
        check('Has latency_ms', 'latency_ms' in data, data.keys())

        # 3. Cache behavior
        print()
        print('[3] Cache behavior')
        r2 = await client.post(f'{BASE}/api/verify', json={'query': 'What is the speed of light?'})
        check('Second request returns 200', r2.status_code == 200, r2.status_code)
        check('Second request is from cache', r2.json().get('from_cache') == True, r2.json().get('from_cache'))

        # 4. Input validation
        print()
        print('[4] Input validation')
        r3 = await client.post(f'{BASE}/api/verify', json={'query': ''})
        check('Empty query returns 400', r3.status_code == 400, r3.status_code)

        # 5. Fact check claims present
        print()
        print('[5] Fact-check pipeline')
        r4 = await client.post(f'{BASE}/api/verify', json={'query': 'Tell me about the Eiffel Tower.'})
        data4 = r4.json()
        check('Claims list is non-empty', len(data4.get('claims', [])) > 0, len(data4.get('claims', [])))
        if data4.get('claims'):
            c = data4['claims'][0]
            check('Claim has text', bool(c.get('text')), c.keys())
            check('Claim has valid status', c.get('status') in ['VERIFIED','UNCERTAIN','CONTRADICTED'], c.get('status'))

        print()
        print(f'Result: {passed} passed, {failed} failed')
        if failed == 0:
            print('🚀 FOUNDATION COMPLETE — HANDOFF TO FRONTEND TEAM')
        else:
            print('⚠  FIX FAILURES BEFORE PROCEEDING')

asyncio.run(run_all_tests())
"
```

---

## 7. Master Checkpoint Summary

| Checkpoint | Time | Critical Tests | Blocker? |
|---|---|---|---|
| **CP1** — Environment Ready | 01:30 | Server starts, .env loads, all imports resolve | Yes |
| **CP2** — LLM Services Verified | 02:30 | Primary returns confidence, Gemini returns answer | Yes |
| **CP3** — Gate Logic Verified | 03:30 | Gate correctly routes high vs low confidence queries | Yes |
| **CP4** — Fact-Check Live | 04:30 | Tavily returns sources, claims extracted successfully | Yes |
| **CP5** — Trust Score Validated | 05:30 | Known-true ≥ 65, known-false ≤ 50 | Yes |
| **CP6** — Cache Verified | 06:30 | Second identical query returns from cache < 100ms | Yes |
| **CP7** — Foundation Complete | 08:00 | Full acceptance test suite passes | Yes |

> ⚠️ **Do not advance to the next phase if the current checkpoint has failures.** Upstream bugs compound downstream.

---

## 8. Error Reference Handbook

A comprehensive lookup table for every error likely to appear during Hours 0–8.

---

### 8.1 Environment Errors

| Error | Cause | Fix |
|---|---|---|
| `ModuleNotFoundError: No module named 'fastapi'` | Wrong virtual environment | `source venv/bin/activate` then `pip install -r requirements.txt` |
| `KeyError: 'OPENAI_API_KEY'` | `.env` not loaded | Add `load_dotenv()` at the very top of `main.py`, before any `os.getenv()` |
| `Address already in use: 8000` | Port taken | `lsof -i :8000`, `kill -9 <PID>`, or run with `--port 8001` |
| `WARNING: dotenv path not found` | `.env` in wrong directory | Confirm `.env` is in the same directory as `main.py` |
| `error: No module named pip` | Python env broken | `python -m ensurepip --upgrade` |

---

### 8.2 OpenAI / GPT Errors

| Error | Cause | Fix |
|---|---|---|
| `JSONDecodeError` on GPT response | Model added markdown fences despite JSON mode | Verify `response_format={"type": "json_object"}` is in the API call, not just the prompt |
| `AuthenticationError: 401` | Wrong or expired API key | Regenerate key at platform.openai.com, update `.env` |
| `RateLimitError: 429` | Too many requests | Add `await asyncio.sleep(1)` between test calls during development |
| `InsufficientQuotaError` | No credits | Top up billing at platform.openai.com/billing |
| Confidence always returns `100` | System prompt not strict enough | Add to prompt: "NEVER score 100 unless it is a mathematical identity or universal constant" |
| Confidence always returns `50–55` | Model is too conservative | Add: "Factual questions you know well should score 85–95. Reserve low scores for genuine uncertainty" |
| Response missing `confidence` key | Model ignored JSON schema | Add a one-shot example to system prompt showing the exact JSON structure |

---

### 8.3 Gemini / Google AI Errors

| Error | Cause | Fix |
|---|---|---|
| `google.api_core.exceptions.ResourceExhausted: 429` | Free tier quota hit | Switch to Ollama fallback immediately. Run: `ollama serve` + `ollama pull llama3` |
| `ValueError: API key not valid` | Wrong Gemini key | Get key from aistudio.google.com, not Google Cloud Console |
| `TypeError: generate_content() missing argument` | API version mismatch | Check `google-generativeai` version matches requirements.txt |
| Gemini returns empty string | Safety filter triggered | Query may have triggered content filters; test with neutral factual queries |
| Ollama fallback: `Connection refused` | Ollama not running | Run `ollama serve` in a separate terminal; keep it running throughout hackathon |

---

### 8.4 Tavily Errors

| Error | Cause | Fix |
|---|---|---|
| `TavilyError: Invalid API key` | Wrong key | Regenerate at app.tavily.com |
| All claims return `UNCERTAIN` | Claims too abstract for web search | Update extraction prompt to require "named entities, dates, or statistics" in claims |
| `ReadTimeout` on Tavily call | Slow network | Increase timeout in `run_in_executor` call, or set `search_depth="basic"` |
| Empty `results` list | Very obscure claim | Add fallback: if results empty, return `UNCERTAIN` not error |
| `asyncio` errors with synchronous Tavily | Blocking call in async context | Always wrap in `loop.run_in_executor(None, lambda: tavily_client.search(...))` |

---

### 8.5 Redis Errors

| Error | Cause | Fix |
|---|---|---|
| `ConnectionError: Connection refused` | Upstash URL wrong | Verify URL starts with `rediss://` (double s). Plain `redis://` won't work with Upstash TLS |
| `AuthenticationError` | Wrong Redis password | Copy the full connection string from Upstash dashboard, including the `:password@` part |
| Cache not working (always MISS) | `decode_responses=True` missing | Add `decode_responses=True` to `redis.from_url()` call |
| `TypeError: Object of type ClaimResult is not JSON serializable` | Pydantic model not converted to dict before caching | Call `result.model_dump()` before `json.dumps()` in `set_cached()` |
| Cache works locally but not on Railway | Environment variable not set in Railway | Set `REDIS_URL` in Railway environment variables panel |

---

### 8.6 FastAPI / Async Errors

| Error | Cause | Fix |
|---|---|---|
| `CORS error` in browser | CORSMiddleware not configured | Confirm `app.add_middleware(CORSMiddleware, allow_origins=["*"])` is before route includes |
| `RuntimeError: no running event loop` | Sync function called in async context | Use `asyncio.get_event_loop().run_in_executor()` for any synchronous library calls |
| `TypeError: object Response can't be used in 'await'` | Using sync OpenAI client instead of async | Import `AsyncOpenAI` not `OpenAI` |
| Pydantic `ValidationError` on response | Response dict missing required field | Check `VerifyResponse` schema matches what `run_verification_pipeline()` returns |
| `422 Unprocessable Entity` on POST | Request body doesn't match `VerifyRequest` schema | Confirm client sends `{"query": "..."}` not `{"text": "..."}` |

---

### 8.7 Trust Score & Logic Errors

| Error | Cause | Fix |
|---|---|---|
| Trust score always = 100 | Deductions not applying | Check that `calculate_trust_score()` receives populated `fact_results` list |
| Trust score always = 0 | Over-penalizing | Check `PENALTY_CONTRADICTED` × number of claims doesn't exceed 100 |
| `ValueError: score out of range` | No clamp applied | Add `return max(0, min(100, int(score)))` as final line of `calculate_trust_score()` |
| Consistency score always = 1.0 | Comparing identical strings | Verify `call_verifier()` is not returning `primary["answer"]` accidentally |
| `from_cache: true` but stale data | TTL too long | Reduce `CACHE_TTL_SECONDS` to 300 (5 min) during development |

---

## 9. Final API Contract

This is the exact JSON schema the frontend team should code against. Do not change field names after handing this off.

### Request

```
POST /api/verify
Content-Type: application/json

{
  "query": "string (required, 1–2000 chars)"
}
```

### Response

```json
{
  "trust_score": 82,
  "answer": "Full answer text from the primary LLM model...",
  "confidence": 88,
  "verifier_used": false,
  "claims": [
    {
      "text": "The Eiffel Tower was completed in 1889",
      "status": "VERIFIED",
      "source_url": "https://en.wikipedia.org/wiki/Eiffel_Tower",
      "source_title": "Eiffel Tower — Wikipedia"
    },
    {
      "text": "It stands 330 meters tall",
      "status": "VERIFIED",
      "source_url": "https://www.toureiffel.paris/en/the-monument/key-figures",
      "source_title": "Eiffel Tower — Official Site"
    },
    {
      "text": "Originally planned for demolition in 1909",
      "status": "UNCERTAIN",
      "source_url": null,
      "source_title": "No sources found"
    }
  ],
  "from_cache": false,
  "latency_ms": 1842,
  "error": null
}
```

### Status Reference

| Field | Type | Notes |
|---|---|---|
| `trust_score` | `int` 0–100 | 85+ = green, 65–84 = yellow, 45–64 = orange, 0–44 = red |
| `answer` | `string` | Full primary LLM answer |
| `confidence` | `int` 0–100 | Primary model's self-assessed certainty |
| `verifier_used` | `bool` | If `false`, Gemini was not called (gate skipped) |
| `claims[].status` | `enum` | One of: `VERIFIED`, `UNCERTAIN`, `CONTRADICTED` |
| `from_cache` | `bool` | If `true`, no API calls were made — instant response |
| `latency_ms` | `int` | Total pipeline time in milliseconds |
| `error` | `string\|null` | Populated only on pipeline failure; `null` on success |

---

## 10. If You Fall Behind Schedule

Use this decision tree if you reach a checkpoint behind schedule.

```
Are you at Checkpoint 1 (01:30) and not done?
├── YES → Stop adding features. Get the server running and all imports
│         working first. Nothing else matters until CP1 passes.
└── NO ↓

Are you at Checkpoint 3 (03:30) with LLMs not working?
├── YES → DROP GEMINI entirely. Single-LLM pipeline is still a viable demo.
│         The Trust Score will use only confidence + fact-check signals.
│         Remove the gate logic, simplify to: call_primary() → fact_check → score.
└── NO ↓

Are you at Checkpoint 5 (05:30) with fact-check not working?
├── YES → DROP TAVILY. Return mock statuses (all UNCERTAIN) for now.
│         The Trust Score will rely entirely on the primary confidence score.
│         A trust score from one signal is still a functional demo.
│         Come back to Tavily in Hours 20-36 if time allows.
└── NO ↓

Are you at Checkpoint 7 (08:00) with cache not working?
├── YES → SKIP REDIS. The pipeline works without it. Cache is an optimization
│         not a core feature. Every query will just hit APIs. Budget ~$0.50
│         for demo queries instead of $0.10. That is acceptable.
└── NO → You are on track. Proceed to Hours 8–20 (Frontend).
```

### Absolute Priorities — Never Cut These

| Feature | Why |
|---|---|
| **Trust Score (0–100)** | This is the headline demo moment. Judges need to see this number. |
| **Sentence-level status** | Green/yellow/red highlighting is the visual differentiator. Cannot be cut. |
| **Source Chain URLs** | Clickable evidence is what separates you from ModelProof. Must be present. |

### Safe to Cut Under Time Pressure

| Feature | Impact of Cutting |
|---|---|
| Gemini Flash (verifier) | Trust Score still works from confidence + fact-check. Minor accuracy loss. |
| Redis cache | Queries hit APIs every time. Budget slightly higher. |
| Consistency score | Trust Score remains valid with two remaining signals. |
| Ollama fallback | Only matters if Gemini hits rate limits. Low risk for short demo. |

---

*End of Foundation Roadmap — AI Trust Sentinel v1.0*
*Prepared for: Hackathon Hours 0–8 | Track: AI/ML*
