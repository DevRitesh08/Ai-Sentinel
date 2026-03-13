# AI Trust Sentinel

> An AI fact-checking backend that verifies claims in real-time using multiple LLMs,
> live web search, and a composite Trust Score (0–100).

## Architecture

```
User Query → Redis Cache (HIT: instant return)
                   ↓ MISS
           GPT-4o-mini (primary answer + confidence score)
                   ↓
           Confidence Gate (threshold = 75)
              ↙              ↘
        ≥ 75: SKIP       < 75: ESCALATE
              ↓                  ↓
              └──────────────────┘
              ↓ (parallel execution below)
   Gemini Flash (verifier)   +   Claim Extractor (GPT-4o-mini)
              ↓
         Tavily Fact-Check (per claim, concurrent)
              ↓
      Trust Score Engine (0–100)
              ↓
     Cache + Return Full JSON
```

## Quick Start

### Prerequisites

- Python 3.11+
- 4 API keys (see below)

### 1. Get API Keys

| Service | Free? | URL |
|---|---|---|
| OpenAI (GPT-4o-mini) | No — ~$0.05 total for build | platform.openai.com |
| Google AI Studio (Gemini) | Yes | aistudio.google.com |
| Tavily | Yes (1,000 calls/month) | tavily.com |
| Upstash Redis | Yes | upstash.com |

### 2. Set Up Environment

```bash
# Clone / navigate to project
cd "ai-trust-sentinel/backend"

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Verify all imports work
python -c "import fastapi, openai, google.generativeai, tavily, redis; print('All imports OK')"
```

### 3. Configure API Keys

```bash
# Copy the template
cp .env.template .env

# Edit .env and fill in your real keys
notepad .env   # Windows
nano .env      # Mac/Linux
```

> ⚠️ **Critical:** The Upstash Redis URL must start with `rediss://` (double `s`). Plain `redis://` will fail on the free TLS-required tier.

### 4. Verify All Keys Work

```bash
# From project root
python test_keys.py
```

Expected output:
```
✓ OpenAI: KEY_OK
✓ Gemini: KEY_OK
✓ Tavily: <article title>
✓ Redis: KEY_OK
Result: 4/4 passed
🚀 All keys verified — safe to start building!
```

### 5. Start the Server

```bash
# From backend/ directory with venv active
uvicorn main:app --reload --port 8000
```

### 6. Test the Server

```bash
# Health check
curl http://localhost:8000/health
# → {"status":"ok","version":"1.0.0"}

# Verify a query
curl -X POST http://localhost:8000/api/verify \
  -H "Content-Type: application/json" \
  -d '{"query": "Who built the Eiffel Tower?"}'
```

## API Reference

### `POST /api/verify`

**Request:**
```json
{ "query": "Your question here (max 2000 chars)" }
```

**Response:**
```json
{
  "trust_score": 82,
  "answer": "The primary LLM answer...",
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

**Trust Score Colors:**

| Score | Label | Color |
|---|---|---|
| 85–100 | HIGH CONFIDENCE | 🟢 `#00FF9D` |
| 65–84 | MODERATE CONFIDENCE | 🟡 `#FFD166` |
| 45–64 | LOW CONFIDENCE | 🟠 `#FF9A3C` |
| 0–44 | UNRELIABLE | 🔴 `#FF4F6A` |

### `GET /health`
Returns `{"status": "ok"}` — use this to verify the server is running.

### `GET /api/cache/stats`
Returns Redis connection status and cached query count.

## Project Structure

```
ai-trust-sentinel/
├── backend/
│   ├── main.py                   # FastAPI app entry point
│   ├── requirements.txt
│   ├── .env.template             # Copy to .env and fill in keys
│   ├── routers/
│   │   └── verify.py             # /verify and /cache/stats endpoints
│   ├── services/
│   │   ├── llm_primary.py        # GPT-4o-mini with JSON mode
│   │   ├── llm_verifier.py       # Gemini Flash + Ollama fallback
│   │   ├── gate.py               # Confidence gate (threshold=75)
│   │   ├── claim_extractor.py    # Claim extraction (GPT-4o-mini)
│   │   ├── fact_checker.py       # Tavily fact-check integration
│   │   ├── trust_score.py        # Score aggregation (0–100)
│   │   ├── cache.py              # Redis cache layer
│   │   ├── pipeline.py           # 7-stage orchestrator
│   │   └── prompt_calibration.py # Confidence tuning script
│   └── models/
│       └── schemas.py            # Pydantic request/response models
├── frontend/
│   ├── package.json
│   └── src/
│       ├── services/
│       │   └── api.js            # Backend API client
│       └── components/
│           ├── ChatInput.jsx     # Query input form
│           ├── TrustScore.jsx    # Score badge display
│           ├── ResponseHighlight.jsx  # Answer with claim highlights
│           └── SourceChain.jsx   # Claim + source list
├── test_keys.py                  # API key ping test
└── .gitignore
```

## Tunable Parameters

Edit `backend/.env` to adjust behavior:

| Parameter | Default | Effect |
|---|---|---|
| `CONFIDENCE_THRESHOLD` | 75 | Below this → Gemini is called as verifier |
| `CACHE_TTL_SECONDS` | 3600 | How long results are cached (1 hour) |
| `MAX_CLAIMS` | 5 | Max claims extracted per answer |
| `MAX_TAVILY_RESULTS` | 3 | Search results per claim |

## Development Notes

- Run confidence calibration: `python -m services.prompt_calibration` (from `backend/`)
- If Gemini hits rate limits: start `ollama serve` for automatic local fallback
- If Redis is unavailable: pipeline still works, just without caching
- The 20-second pipeline timeout prevents slow APIs from blocking requests
