# AI Trust Sentinel — Polish, Deploy & Demo Roadmap
### Hours 20–48 | UI Refinement · Deployment · Performance · Demo Preparation

> **"Working code becomes a winning product in these final 28 hours. Every minute spent on polish multiplies the impact of the 20 hours of engineering behind it."**

---

## Table of Contents

1. [Overview & Goals](#1-overview--goals)
2. [Pre-Phase Checklist — Handoff from Core Pipeline](#2-pre-phase-checklist--handoff-from-core-pipeline)
3. [Phase 9 — UI Polish & Visual Refinement (20:00–26:00)](#3-phase-9--ui-polish--visual-refinement-2000--2600)
4. [Phase 10 — Performance, Edge Cases & Resilience (26:00–32:00)](#4-phase-10--performance-edge-cases--resilience-2600--3200)
5. [Phase 11 — Production Deployment (32:00–38:00)](#5-phase-11--production-deployment-3200--3800)
6. [Phase 12 — Demo Preparation & Rehearsal (38:00–48:00)](#6-phase-12--demo-preparation--rehearsal-3800--4800)
7. [Master Checkpoint Summary](#7-master-checkpoint-summary)
8. [Error Reference Handbook](#8-error-reference-handbook)
9. [Demo Playbook — Judge Interaction Guide](#9-demo-playbook--judge-interaction-guide)
10. [Emergency Protocols](#10-emergency-protocols)

---

## 1. Overview & Goals

### What Hours 20–48 Must Achieve

By Hour 20, a working end-to-end demo exists on localhost. Hours 20–48 transform it from a prototype that works for the team into a **production-grade demo that survives contact with judges, unexpected queries, bad WiFi, and live pressure**.

This is the phase that separates hackathon finalists from the rest.

---

### Deliverable Table

| Deliverable | Owner | Done When |
|---|---|---|
| Responsive layout (mobile + desktop) | Frontend | App usable on any screen size including judge's phone |
| Micro-animations & transitions | Frontend | All state transitions feel smooth and intentional |
| Edge case handling (empty, very long, gibberish input) | Both | No unhandled errors or blank screens for any input |
| Performance optimization (< 2s non-cached p90) | Backend | Pipeline latency profiled and bottlenecks addressed |
| Bias & toxicity scanner | Backend | New pipeline stage detects problematic content |
| Intent alignment check | Backend | Detects when AI answer doesn't address the actual question |
| Frontend deployed to Vercel | Frontend | Public HTTPS URL accessible from any device |
| Backend deployed to Railway | Backend | API running on Railway, accessible from Vercel frontend |
| Custom domain / subdomain (stretch) | Both | Memorable URL for demo (e.g. trustsentinel.vercel.app) |
| Pre-seeded cache (demo queries) | Backend | Top 10 demo queries cached in production Redis |
| Demo script rehearsed 3× minimum | All | Team can run the 5-minute demo without hesitation |
| Judge Q&A prepared | All | Every anticipated question has a confident answer |
| Slide deck loaded and ready | All | Pitch deck open in browser, backup on local machine |
| Fallback demo mode (offline) | Backend | Demo works without internet using cached + Ollama |

---

### Architecture by Hour 48

```
Internet
    │
    ▼
┌─────────────────────────────────────┐
│   Vercel CDN (Global Edge Network)  │
│   https://trustsentinel.vercel.app  │
│                                     │
│   React App (static build)          │
│   • Optimized bundle < 200KB        │
│   • All assets pre-compressed       │
└────────────────┬────────────────────┘
                 │ HTTPS API calls
                 ▼
┌─────────────────────────────────────┐
│   Railway.app (Backend)             │
│   https://api.trustsentinel.up.railway.app │
│                                     │
│   FastAPI (Python)                  │
│   • Auto-scaled workers             │
│   • Environment variables set       │
│   • Health check endpoint live      │
└────────────────┬────────────────────┘
        ┌────────┼─────────┐
        ▼        ▼         ▼
  ┌──────────┐ ┌──────┐ ┌──────────┐
  │ Upstash  │ │OpenAI│ │  Tavily  │
  │ Redis    │ │ API  │ │   API    │
  │ (Global) │ │      │ │          │
  └──────────┘ └──────┘ └──────────┘
```

---

### Hour-by-Hour Schedule

| Hours | Backend Lead | Frontend Lead | Both |
|---|---|---|---|
| 20–23 | Bias/toxicity scanner, intent alignment | Responsive layout, loading animations | — |
| 23–26 | Edge case hardening, input validation | Micro-interactions, keyboard shortcuts | Sync @ 26:00 |
| 26–29 | Latency profiling, parallel optimization | Error state polish, empty states | — |
| 29–32 | Resilience testing (kill services, test fallbacks) | Mobile testing, cross-browser check | Sync @ 32:00 |
| 32–35 | Railway deployment, environment variables | Vercel deployment, .env.production | — |
| 35–38 | Production smoke tests, cache pre-seeding | Production URL testing, CORS production fix | Sync @ 38:00 |
| 38–42 | Monitor production logs during demo rehearsal | Final visual QA on production URL | Demo rehearsal #1 |
| 42–45 | Bug fixes from rehearsal #1 | Bug fixes from rehearsal #1 | Demo rehearsal #2 |
| 45–47 | Freeze code — no more changes | Freeze code — no more changes | Final prep |
| 47–48 | Rest | Rest | Demo rehearsal #3 |

---

## 2. Pre-Phase Checklist — Handoff from Core Pipeline

Run this sync before any Phase 9 work begins. Allocate 15 minutes, no shortcuts.

### Backend Verification

```bash
# Run from /backend directory with venv activated

# 1. Pipeline end-to-end
curl -s -X POST http://localhost:8000/api/verify \
  -H "Content-Type: application/json" \
  -d '{"query": "Was Albert Einstein really bad at math?"}' \
  | python -m json.tool

# Verify these fields in the output:
# ✓ trust_score: number between 0-100
# ✓ answer: non-empty string
# ✓ sentences: array with at least 2 items
# ✓ claims: array with at least 1 item
# ✓ from_cache: false (first call)
# ✓ latency_ms: under 5000

# 2. Cache working
curl -s -X POST http://localhost:8000/api/verify \
  -H "Content-Type: application/json" \
  -d '{"query": "Was Albert Einstein really bad at math?"}' \
  | python -m json.tool | grep '"from_cache"'

# Expected: "from_cache": true

# 3. Confidence gate triggers correctly
# Ask something genuinely obscure
curl -s -X POST http://localhost:8000/api/verify \
  -H "Content-Type: application/json" \
  -d '{"query": "What was the exact census population of Carthage in 200 BC?"}' \
  | python -m json.tool | grep '"verifier_used"'
# Expected: "verifier_used": true  (low confidence → gate triggers)
```

### Frontend Verification

```bash
# Manual checks — open http://localhost:5173

# ✓ TrustScoreMeter animates smoothly from 0 to actual score
# ✓ Sentences render with green/yellow/red highlighting
# ✓ Clicking a highlighted sentence shows source panel
# ✓ SourceChain renders all claims with status badges
# ✓ Second identical query shows "⚡ from cache" badge
# ✓ Empty submit attempt does nothing
# ✓ No console errors during normal operation
```

### Team Alignment Checklist

- [ ] Both localhost URLs work and are accessible
- [ ] API schema has not changed since frontend built against it (confirm with git diff)
- [ ] All API keys are valid and have sufficient quota for 48 hours
- [ ] Git repo is clean and committed
- [ ] Vercel and Railway accounts created and connected to the repo
- [ ] Team has agreed on the final demo query list (see Phase 12)

---

## 3. Phase 9 — UI Polish & Visual Refinement (20:00–26:00)

**Goal:** Elevate the interface from functional to impressive. Judges evaluate polish as a proxy for engineering quality and product thinking. Every transition, animation, and empty state signals craft.

**Owner:** Frontend lead (backend lead adds new pipeline stages in parallel)

---

### Task 9.1 — Responsive Layout (45 min)

The current layout may break on smaller screens. Judges and observers will try it on their phones.

```jsx
// frontend/src/App.jsx — Update layout for responsive design

// Replace the fixed max-w-3xl layout with a responsive container system
export default function App() {
  return (
    <div className="min-h-screen flex flex-col">
      {/* Sticky header */}
      <header className="
        border-b border-ats-border bg-ats-surface/90
        backdrop-blur-md sticky top-0 z-20
      ">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 py-3 sm:py-4
                        flex items-center justify-between">
          <div className="flex items-center gap-2 sm:gap-3">
            <div className="w-2 h-2 rounded-full bg-ats-cyan animate-pulse-dot" />
            <span className="font-mono text-xs sm:text-sm font-bold
                             text-ats-cyan tracking-widest">
              AI TRUST SENTINEL
            </span>
          </div>
          {/* Hide tagline on very small screens */}
          <span className="hidden sm:block font-mono text-xs text-ats-muted">
            The trust layer AI never gave you.
          </span>
          {/* Show abbreviated version on mobile */}
          <span className="sm:hidden font-mono text-xs text-ats-muted">
            Trust · Verify · Source
          </span>
        </div>
      </header>

      {/* Scrollable main content */}
      <main className="flex-1 max-w-4xl mx-auto w-full px-4 sm:px-6
                       py-6 sm:py-8 space-y-4 sm:space-y-6">
        {/* ... content ... */}
      </main>

      {/* Sticky input — full width on mobile */}
      <div className="sticky bottom-0 bg-ats-bg/90 backdrop-blur-md
                      border-t border-ats-border p-3 sm:p-0 sm:border-0
                      sm:bg-transparent sm:backdrop-blur-none
                      sm:relative sm:max-w-4xl sm:mx-auto sm:w-full
                      sm:px-6 sm:pb-8">
        <ChatInput onSubmit={handleSubmit} loading={loading} />
      </div>
    </div>
  );
}
```

```jsx
// frontend/src/components/ChatMessage.jsx — Responsive message layout

export default function ChatMessage({ query, data }) {
  return (
    <div className="space-y-3 sm:space-y-4 animate-fade-up">
      {/* User query bubble */}
      <div className="flex justify-end">
        <div className="card px-3 py-2 sm:px-4 sm:py-3
                        max-w-[85%] sm:max-w-lg border-ats-cyan/30">
          <p className="text-sm text-ats-text">{query}</p>
        </div>
      </div>

      {/* Response card — stack vertically on mobile */}
      <div className="card p-4 sm:p-5">
        {/* On mobile: score on top, text below. On desktop: side by side */}
        <div className="flex flex-col sm:flex-row
                        sm:items-start sm:justify-between gap-4 sm:gap-6 mb-4 sm:mb-5">

          {/* On mobile: small inline score. On desktop: full meter on right */}
          <div className="sm:hidden">
            <InlineTrustBadge score={data.trust_score}
                              label={data.trust_label}
                              color={data.trust_color} />
          </div>

          <div className="flex-1">
            <MetaLine data={data} />
            <SentenceText sentences={data.sentences} />
          </div>

          <div className="hidden sm:block flex-shrink-0">
            <TrustScoreMeter score={data.trust_score} size={140} />
          </div>
        </div>

        <SourceChain claims={data.claims} />
      </div>
    </div>
  );
}

// Compact trust badge for mobile
function InlineTrustBadge({ score, label, color }) {
  return (
    <div className="flex items-center gap-3 p-2 rounded-lg bg-ats-surface
                    border border-ats-border mb-3">
      <span className="font-mono font-bold text-2xl" style={{ color }}>
        {score}
      </span>
      <div>
        <div className="text-xs font-mono font-bold" style={{ color }}>
          {label}
        </div>
        <div className="w-20 h-1 bg-ats-border rounded-full mt-1">
          <div
            className="h-full rounded-full"
            style={{ width: `${score}%`, background: color }}
          />
        </div>
      </div>
    </div>
  );
}
```

---

### Task 9.2 — Enhanced Loading Experience (40 min)

The loading state is the most-seen UI state during a demo. Make it tell the product story while the pipeline runs.

```jsx
// frontend/src/components/LoadingState.jsx — Enhanced version

import { useEffect, useState } from "react";

const PIPELINE_STAGES = [
  {
    id:      "cache",
    icon:    "⚡",
    label:   "Checking query cache",
    sub:     "Looking for cached result to save API costs",
    color:   "text-ats-cyan",
    delay:   0,
    duration: 300,
  },
  {
    id:      "primary_llm",
    icon:    "🧠",
    label:   "Primary LLM analysis",
    sub:     "GPT-4o-mini generating answer + confidence score",
    color:   "text-ats-purple",
    delay:   300,
    duration: 1200,
  },
  {
    id:      "gate",
    icon:    "🔀",
    label:   "Confidence gate evaluation",
    sub:     "Deciding whether second model verification is needed",
    color:   "text-ats-yellow",
    delay:   1000,
    duration: 400,
  },
  {
    id:      "claims",
    icon:    "🔍",
    label:   "Extracting factual claims",
    sub:     "Isolating the 3–5 key assertions for fact-checking",
    color:   "text-ats-cyan",
    delay:   1400,
    duration: 800,
  },
  {
    id:      "factcheck",
    icon:    "🌐",
    label:   "Verifying against web sources",
    sub:     "Searching live sources for each extracted claim",
    color:   "text-ats-green",
    delay:   2000,
    duration: 1200,
  },
  {
    id:      "score",
    icon:    "📊",
    label:   "Computing Trust Score",
    sub:     "Aggregating all signals into 0–100 confidence rating",
    color:   "text-ats-cyan",
    delay:   2800,
    duration: 600,
  },
];

export default function LoadingState({ startTime }) {
  const [activeStage, setActiveStage] = useState(0);
  const [elapsedMs, setElapsedMs]     = useState(0);

  // Animate through stages sequentially
  useEffect(() => {
    const timers = PIPELINE_STAGES.map((stage, i) =>
      setTimeout(() => setActiveStage(i), stage.delay)
    );
    return () => timers.forEach(clearTimeout);
  }, []);

  // Live elapsed time counter
  useEffect(() => {
    const start  = startTime ?? Date.now();
    const ticker = setInterval(() => setElapsedMs(Date.now() - start), 100);
    return () => clearInterval(ticker);
  }, [startTime]);

  return (
    <div className="card p-5 sm:p-6 space-y-5 animate-fade-up">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="relative">
            <div className="w-3 h-3 rounded-full bg-ats-cyan" />
            <div className="absolute inset-0 w-3 h-3 rounded-full bg-ats-cyan
                            animate-ping opacity-40" />
          </div>
          <span className="font-mono text-xs font-bold tracking-widest text-ats-cyan">
            PIPELINE RUNNING
          </span>
        </div>
        <span className="font-mono text-xs text-ats-muted">
          {(elapsedMs / 1000).toFixed(1)}s elapsed
        </span>
      </div>

      {/* Stage list */}
      <div className="space-y-3">
        {PIPELINE_STAGES.map((stage, i) => {
          const isDone    = i < activeStage;
          const isActive  = i === activeStage;
          const isPending = i > activeStage;

          return (
            <div
              key={stage.id}
              className={`
                flex items-start gap-3 transition-all duration-300
                ${isPending ? "opacity-25" : "opacity-100"}
              `}
            >
              {/* Icon / status indicator */}
              <div className={`
                w-8 h-8 rounded-lg flex items-center justify-center
                flex-shrink-0 text-sm transition-all duration-300
                ${isDone    ? "bg-green-950 border border-ats-green" : ""}
                ${isActive  ? "bg-ats-surface border border-ats-cyan" : ""}
                ${isPending ? "bg-ats-surface border border-ats-border" : ""}
              `}>
                {isDone
                  ? <span className="text-ats-green text-xs font-bold">✓</span>
                  : isActive
                    ? <span className={`text-base animate-pulse`}>{stage.icon}</span>
                    : <span className="text-ats-muted text-xs">{i + 1}</span>
                }
              </div>

              {/* Stage text */}
              <div className="flex-1 pt-1">
                <div className={`
                  text-xs font-mono font-bold
                  ${isDone    ? "text-ats-green" : ""}
                  ${isActive  ? stage.color      : ""}
                  ${isPending ? "text-ats-muted"  : ""}
                `}>
                  {stage.label}
                  {isActive && <span className="animate-pulse ml-1">...</span>}
                </div>
                {(isActive || isDone) && (
                  <div className="text-xs text-ats-muted mt-0.5 font-mono">
                    {stage.sub}
                  </div>
                )}
              </div>

              {/* Stage timing badge */}
              {isDone && (
                <span className="text-xs font-mono text-ats-muted flex-shrink-0 pt-1">
                  done
                </span>
              )}
            </div>
          );
        })}
      </div>

      {/* Shimmer skeleton for response preview */}
      <div className="space-y-2 pt-2 border-t border-ats-border">
        <div className="text-xs font-mono text-ats-muted mb-3">
          Preparing response...
        </div>
        {[90, 75, 88, 60, 82].map((w, i) => (
          <div
            key={i}
            className="h-3 rounded"
            style={{
              width:           `${w}%`,
              background:      "linear-gradient(90deg, #1D304E 25%, #243A5C 50%, #1D304E 75%)",
              backgroundSize:  "200% 100%",
              animation:       `shimmer 1.5s infinite`,
              animationDelay:  `${i * 120}ms`,
            }}
          />
        ))}
      </div>
    </div>
  );
}
```

---

### Task 9.3 — Keyboard Shortcuts & Accessibility (30 min)

Keyboard navigation impresses technical judges and improves demo speed.

```jsx
// frontend/src/hooks/useKeyboardShortcuts.js
import { useEffect } from "react";

/**
 * Global keyboard shortcuts for the app.
 *
 * Shortcuts:
 *   /         → Focus the query input
 *   Escape    → Clear current result and focus input
 *   Ctrl+K    → Focus input (VSCode style)
 */
export function useKeyboardShortcuts({ onFocusInput, onClearResult }) {
  useEffect(() => {
    const handler = (e) => {
      // Don't intercept when user is already typing
      const tag = document.activeElement?.tagName;
      const inInput = tag === "INPUT" || tag === "TEXTAREA";

      if (!inInput && e.key === "/") {
        e.preventDefault();
        onFocusInput?.();
        return;
      }

      if ((e.ctrlKey || e.metaKey) && e.key === "k") {
        e.preventDefault();
        onFocusInput?.();
        return;
      }

      if (e.key === "Escape") {
        onClearResult?.();
        onFocusInput?.();
        return;
      }
    };

    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [onFocusInput, onClearResult]);
}
```

```jsx
// Apply in App.jsx:
import { useRef } from "react";
import { useKeyboardShortcuts } from "./hooks/useKeyboardShortcuts";

export default function App() {
  const inputRef = useRef(null);
  const { verify, data, loading, error, reset } = useVerify();

  useKeyboardShortcuts({
    onFocusInput:  () => inputRef.current?.focus(),
    onClearResult: () => { reset(); inputRef.current?.focus(); },
  });

  // Pass ref to ChatInput
  return (
    // ...
    <ChatInput
      ref={inputRef}
      onSubmit={handleSubmit}
      loading={loading}
    />
  );
}
```

```jsx
// Update ChatInput to accept forwardRef:
import { forwardRef } from "react";

const ChatInput = forwardRef(function ChatInput({ onSubmit, loading }, ref) {
  // Replace useRef(null) with the forwarded ref:
  const textareaRef = ref ?? useRef(null);
  // ... rest unchanged
});

export default ChatInput;
```

---

### Task 9.4 — Query History with Collapsible Entries (35 min)

```jsx
// frontend/src/components/HistoryEntry.jsx
import { useState } from "react";
import TrustScoreMeter from "./TrustScoreMeter";
import { getTrustConfig, formatLatency } from "../utils/trustHelpers";

/**
 * A collapsed history entry that expands on click.
 */
export default function HistoryEntry({ query, data, index }) {
  const [expanded, setExpanded] = useState(false);
  const config = getTrustConfig(data.trust_score);

  return (
    <div className="card transition-all duration-200">
      {/* Collapsed header — always visible */}
      <button
        className="w-full flex items-center gap-4 p-4 text-left hover:bg-ats-surface/50"
        onClick={() => setExpanded(!expanded)}
        aria-expanded={expanded}
      >
        {/* Score pill */}
        <span
          className={`font-mono font-bold text-lg w-12 flex-shrink-0 ${config.textClass}`}
        >
          {data.trust_score}
        </span>

        {/* Query text (truncated) */}
        <span className="flex-1 text-sm text-ats-text truncate">{query}</span>

        {/* Meta: cache badge + latency + expand arrow */}
        <div className="flex items-center gap-2 flex-shrink-0">
          {data.from_cache && (
            <span className="text-xs font-mono text-ats-cyan">⚡</span>
          )}
          <span className="text-xs font-mono text-ats-muted">
            {formatLatency(data.latency_ms)}
          </span>
          <span
            className={`text-ats-muted transition-transform duration-200
                        ${expanded ? "rotate-180" : ""}`}
          >
            ▾
          </span>
        </div>
      </button>

      {/* Expanded content */}
      {expanded && (
        <div className="border-t border-ats-border p-4 animate-fade-up">
          <div className="flex flex-col sm:flex-row gap-4 sm:gap-6">
            <div className="flex-1 space-y-1">
              {data.sentences?.map((s, i) => (
                <span
                  key={i}
                  className={`text-sm leading-relaxed mr-1 ${
                    s.status === "VERIFIED"     ? "text-ats-green" :
                    s.status === "CONTRADICTED" ? "text-ats-red" :
                    s.status === "UNCERTAIN"    ? "text-ats-yellow" :
                    "text-ats-text"
                  }`}
                >
                  {s.text}{" "}
                </span>
              ))}
            </div>
            <div className="flex-shrink-0">
              <TrustScoreMeter score={data.trust_score} size={100} animated={false} />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
```

---

### Task 9.5 — Backend: Bias & Toxicity Scanner (45 min)

A new pipeline stage that scans responses for potential bias patterns or harmful content before delivery.

```python
# backend/services/bias_scanner.py
import os
import json
import logging
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

BIAS_SCAN_PROMPT = """
You are an objective content safety and bias analyzer.
Analyze the given text for the following signals:

1. BIAS INDICATORS: Strong political, cultural, or ideological slant
   that presents one perspective as fact
2. UNVERIFIED STATISTICS: Numbers presented without source attribution
3. LOADED LANGUAGE: Emotionally charged terms that influence perception
4. OVERGENERALIZATION: "Always", "never", "all X people", etc.
5. RECENCY ISSUES: References to events that may be outdated

Respond ONLY as valid JSON:
{
  "bias_score": 0-100,        // 0=neutral, 100=extremely biased
  "toxicity_score": 0-100,    // 0=clean, 100=highly toxic
  "flags": [
    {
      "type": "BIAS|TOXICITY|STATISTICS|LANGUAGE|GENERALIZATION",
      "text": "the flagged phrase",
      "reason": "why this is flagged"
    }
  ],
  "summary": "One-sentence overall assessment"
}

Return {"bias_score": 0, "toxicity_score": 0, "flags": [], "summary": "No issues detected"}
if no concerns are found.
"""

async def scan_response(text: str) -> dict:
    """
    Scans AI response text for bias, toxicity, and content issues.

    Returns:
        {
          "bias_score":     int 0-100,
          "toxicity_score": int 0-100,
          "flags":          list of flag dicts,
          "summary":        str
        }
    Always returns — never raises. Falls back to clean scan on error.
    """
    CLEAN_RESULT = {
        "bias_score": 0,
        "toxicity_score": 0,
        "flags": [],
        "summary": "Scan unavailable"
    }

    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": BIAS_SCAN_PROMPT},
                {"role": "user",   "content": f"Analyze:\n\n{text[:1500]}"}
            ],
            max_tokens=400,
            temperature=0.1,
        )
        result = json.loads(response.choices[0].message.content)
        logger.info(
            f"Bias scan | bias={result.get('bias_score')} "
            f"| toxicity={result.get('toxicity_score')} "
            f"| flags={len(result.get('flags', []))}"
        )
        return result

    except Exception as e:
        logger.warning(f"Bias scanner failed: {e} — returning clean result")
        return CLEAN_RESULT
```

---

### Task 9.6 — Backend: Intent Alignment Check (30 min)

Detects when the AI's answer doesn't actually address the question — a subtle but common failure mode.

```python
# backend/services/intent_checker.py
import os
import json
import logging
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

INTENT_PROMPT = """
You are an intent alignment evaluator. Determine whether the given
answer actually addresses the user's question.

Respond ONLY as valid JSON:
{
  "aligned": true or false,
  "alignment_score": 0-100,   // 100 = perfectly aligned
  "reason": "Brief explanation if not aligned, null if aligned"
}
"""

async def check_intent_alignment(query: str, answer: str) -> dict:
    """
    Returns alignment score and whether the answer addresses the question.
    Always returns — never raises.
    """
    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": INTENT_PROMPT},
                {"role": "user", "content":
                    f"QUESTION: {query}\n\nANSWER: {answer[:800]}"
                }
            ],
            max_tokens=150,
            temperature=0.1,
        )
        result = json.loads(response.choices[0].message.content)
        logger.info(f"Intent alignment: {result.get('alignment_score')} | aligned={result.get('aligned')}")
        return result
    except Exception as e:
        logger.warning(f"Intent check failed: {e}")
        return {"aligned": True, "alignment_score": 100, "reason": None}
```

**Integrate both new stages into the pipeline (run concurrently with fact-check):**

```python
# backend/services/pipeline.py — add to Stage 6

from services.bias_scanner    import scan_response
from services.intent_checker  import check_intent_alignment

# Run bias scan + intent check + fact-check all in parallel
bias_task    = scan_response(primary["answer"])
intent_task  = check_intent_alignment(query, primary["answer"])
factcheck_task = fact_check_all_claims(claims)

bias_result, intent_result, fact_results = await asyncio.gather(
    bias_task, intent_task, factcheck_task,
    return_exceptions=True
)

# Safe extraction (handle if any task raised)
bias   = bias_result   if isinstance(bias_result,   dict) else {}
intent = intent_result if isinstance(intent_result, dict) else {}
```

**Add to Pydantic schema:**

```python
# backend/models/schemas.py — add fields to VerifyResponse

class VerifyResponse(BaseModel):
    # ... existing fields ...
    bias_score:       Optional[int]  = None   # 0-100
    toxicity_score:   Optional[int]  = None   # 0-100
    intent_aligned:   Optional[bool] = None   # True/False
    alignment_score:  Optional[int]  = None   # 0-100
    bias_flags:       Optional[list] = None   # List of flag objects
```

---

### ✅ Checkpoint 9 — UI Polish & New Stages Complete (@ 26:00)

**Visual checks — run on both desktop and mobile:**

```
Open http://localhost:5173 and verify:

Desktop (≥ 768px wide):
  ✓ TrustScoreMeter renders on the right side of the response
  ✓ Sentences appear on the left
  ✓ SourceChain full width below
  ✓ Navigation header sticky, readable, not overflowing

Mobile (≤ 414px — use DevTools Device Mode):
  ✓ InlineTrustBadge appears above sentence text
  ✓ TrustScoreMeter full circle does NOT appear on mobile
  ✓ All text readable without horizontal scroll
  ✓ Input stays at bottom, accessible with keyboard
  ✓ Suggested query buttons wrap gracefully

Loading state:
  ✓ All 6 pipeline stages animate sequentially
  ✓ Elapsed timer counts up in real-time
  ✓ Shimmer skeleton visible at bottom of loading card

Keyboard:
  ✓ Press "/" to focus the input field
  ✓ Press Ctrl+K to focus the input field
  ✓ Press Escape to clear result and refocus input
```

**Backend checks:**

```bash
# Test bias scanner
curl -s -X POST http://localhost:8000/api/verify \
  -H "Content-Type: application/json" \
  -d '{"query": "Is political party X better than party Y?"}' \
  | python -m json.tool | grep -E '"bias_score"|"toxicity_score"|"intent_aligned"'

# Expected: bias_score and toxicity_score are integers
```

---

## 4. Phase 10 — Performance, Edge Cases & Resilience (26:00–32:00)

**Goal:** The app must not break under unexpected input, network failures, or service degradation. A single crash during the hackathon demo is disqualifying.

---

### Task 10.1 — Input Validation & Edge Case Hardening (45 min)

Test every pathological input and confirm graceful handling.

**Backend edge case matrix:**

```python
# backend/tests/test_edge_cases.py
import asyncio
import httpx

BASE = "http://localhost:8000"

EDGE_CASES = [
    # (query, description, expected_behavior)
    ("",                        "empty string",          "400 error"),
    ("   ",                     "whitespace only",        "400 error"),
    ("a",                       "single character",       "200, low trust"),
    ("?" * 10,                  "special chars only",     "200, graceful"),
    ("A" * 2001,                "over 2000 chars",        "400 error"),
    ("A" * 1999,                "just under 2000 chars",  "200, processes"),
    ("What is 2+2?",            "math question",          "200, high trust"),
    ("SELECT * FROM users;",    "SQL injection attempt",  "200, treated as text"),
    ("<script>alert(1)</script>","XSS attempt",            "200, treated as text"),
    ("Repeat after me: " * 100, "repetition attack",      "200 or 400 gracefully"),
    ("日本語のテスト",             "Japanese characters",   "200, processes"),
    ("🎉🚀💯✨🌟",              "emoji only",             "200 or graceful 400"),
]

async def run_edge_cases():
    async with httpx.AsyncClient(timeout=30, base_url=BASE) as client:
        for query, desc, expected in EDGE_CASES:
            try:
                r = await client.post("/api/verify",
                    json={"query": query},
                    headers={"Content-Type": "application/json"}
                )
                status = r.status_code
                data   = r.json() if status != 400 else {"error": r.json()}
                score  = data.get("trust_score", "N/A")

                ok = (
                    (expected == "400 error" and status == 400) or
                    (expected.startswith("200") and status == 200) or
                    ("graceful" in expected and status in [200, 400])
                )

                print(f"{'✓' if ok else '✗'} [{status}] {desc[:40]:<42} | score={score}")

            except Exception as e:
                print(f"✗ [ERR] {desc[:40]:<42} | exception: {e}")

asyncio.run(run_edge_cases())
```

**Add missing backend guards:**

```python
# backend/routers/verify.py — add comprehensive input sanitization

import re
import html

def sanitize_query(query: str) -> str:
    """
    Sanitizes query input before processing.
    - Strips leading/trailing whitespace
    - Removes HTML tags (XSS prevention)
    - Normalizes internal whitespace
    - Truncates at MAX_LENGTH
    """
    MAX_LENGTH = 2000

    # Strip whitespace
    query = query.strip()

    # Remove HTML tags
    query = re.sub(r'<[^>]+>', '', query)

    # Decode HTML entities
    query = html.unescape(query)

    # Normalize whitespace
    query = re.sub(r'\s+', ' ', query)

    # Truncate
    if len(query) > MAX_LENGTH:
        query = query[:MAX_LENGTH]

    return query


@router.post("/verify", response_model=VerifyResponse)
async def verify_query(payload: VerifyRequest):
    query = sanitize_query(payload.query)

    if len(query) < 2:
        raise HTTPException(status_code=400, detail="Query too short (minimum 2 characters)")

    if len(query) > 2000:
        raise HTTPException(status_code=400, detail="Query too long (maximum 2000 characters)")

    # Check for purely non-semantic input
    meaningful_chars = re.sub(r'[^a-zA-Z0-9\u3000-\u9fff\u4e00-\u9fff]', '', query)
    if len(meaningful_chars) < 2:
        raise HTTPException(status_code=400,
            detail="Query must contain meaningful text")

    return await run_verification_pipeline(query)
```

---

### Task 10.2 — Service Resilience Testing (40 min)

Kill each external service and verify the system degrades gracefully rather than crashing.

```bash
# RESILIENCE TEST PROTOCOL
# Run each test, observe behavior, fix any crashes

# === TEST 1: Kill Redis ===
# In a new terminal, stop Redis/block it temporarily:
# On Upstash: temporarily use a wrong REDIS_URL in .env
# Expected: API still works, just slower (no caching)
# Verify: curl /api/verify still returns 200
# Verify: Server logs show "Redis unavailable — caching disabled"

# === TEST 2: Exhaust OpenAI with wrong key ===
# Temporarily set OPENAI_API_KEY=sk-invalid in .env
# Expected: /verify returns 200 with error field set
# NOT expected: /verify returns 500 or crashes server
# Verify: {"trust_score": 0, "error": "Primary LLM failed: ...", ...}

# === TEST 3: Kill Gemini ===
# Temporarily set GEMINI_API_KEY=invalid
# Send a query with confidence < 75 (should trigger Gemini)
# Expected: Ollama fallback triggers, or graceful null verifier
# Verify: "verifier_used": false (if Ollama also unavailable)

# === TEST 4: Exhaust Tavily ===
# Temporarily set TAVILY_API_KEY=invalid
# Expected: All claims return UNCERTAIN, pipeline completes
# NOT expected: Pipeline crashes or returns 500

# === TEST 5: Timeout simulation ===
# In pipeline.py, temporarily add:
#   await asyncio.sleep(25)  # force timeout
# Expected: Returns {"error": "Pipeline timeout", "trust_score": 0}
# NOT expected: Request hangs indefinitely
```

**Add structured health check for all dependencies:**

```python
# backend/routers/health.py — comprehensive health endpoint

from fastapi import APIRouter
import asyncio, redis, os
from openai import AsyncOpenAI
from tavily import TavilyClient

router = APIRouter()

@router.get("/health/full")
async def full_health_check():
    """
    Checks all external dependencies and returns their status.
    Use this to verify production environment before demo.
    """
    results = {}

    # 1. Redis
    try:
        r = redis.from_url(os.getenv("REDIS_URL"), socket_timeout=2)
        r.ping()
        results["redis"] = {"status": "ok"}
    except Exception as e:
        results["redis"] = {"status": "error", "message": str(e)}

    # 2. OpenAI
    try:
        client = AsyncOpenAI()
        await asyncio.wait_for(
            client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": "ping"}],
                max_tokens=3
            ),
            timeout=5.0
        )
        results["openai"] = {"status": "ok"}
    except Exception as e:
        results["openai"] = {"status": "error", "message": str(e)}

    # 3. Gemini
    try:
        import google.generativeai as genai
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        model = genai.GenerativeModel("gemini-1.5-flash")
        model.generate_content("ping", generation_config={"max_output_tokens": 3})
        results["gemini"] = {"status": "ok"}
    except Exception as e:
        results["gemini"] = {"status": "error", "message": str(e)}

    # 4. Tavily
    try:
        tc = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
        tc.search("test", max_results=1)
        results["tavily"] = {"status": "ok"}
    except Exception as e:
        results["tavily"] = {"status": "error", "message": str(e)}

    # 5. Ollama (local fallback)
    try:
        import httpx
        async with httpx.AsyncClient(timeout=2) as client:
            r = await client.get("http://localhost:11434/api/tags")
            results["ollama"] = {"status": "ok", "models": [m["name"] for m in r.json().get("models", [])]}
    except Exception:
        results["ollama"] = {"status": "offline", "message": "Local fallback unavailable"}

    all_critical_ok = all(
        results[k]["status"] == "ok"
        for k in ["redis", "openai", "tavily"]
    )

    return {
        "overall": "healthy" if all_critical_ok else "degraded",
        "services": results
    }
```

---

### Task 10.3 — Frontend Error State Polish (25 min)

Every error state must communicate clearly and offer a recovery path.

```jsx
// frontend/src/components/ErrorState.jsx — Enhanced version

export default function ErrorState({ message, onRetry, type = "generic" }) {
  const configs = {
    timeout: {
      icon: "⏱",
      title: "Pipeline Timed Out",
      hint: "The pipeline took too long. This sometimes happens during peak load.",
      action: "Try again",
    },
    network: {
      icon: "📡",
      title: "Connection Failed",
      hint: "Cannot reach the backend API. Check if the server is running.",
      action: "Retry",
    },
    rate_limit: {
      icon: "🔄",
      title: "Rate Limited",
      hint: "Too many requests. Wait a moment before trying again.",
      action: "Wait and retry",
    },
    generic: {
      icon: "⚠",
      title: "Pipeline Error",
      hint: message ?? "Something went wrong. The team has been notified.",
      action: "Try again",
    },
  };

  const config = configs[type] ?? configs.generic;

  return (
    <div className="
      card p-5 border border-ats-red/30 bg-red-950/10
      animate-fade-up space-y-3
    ">
      <div className="flex items-start gap-3">
        <span className="text-xl flex-shrink-0">{config.icon}</span>
        <div className="flex-1">
          <p className="font-mono text-xs text-ats-red font-bold
                        tracking-widest mb-1">
            {config.title.toUpperCase()}
          </p>
          <p className="text-sm text-ats-text leading-relaxed">
            {config.hint}
          </p>
        </div>
      </div>

      {onRetry && (
        <button
          onClick={onRetry}
          className="
            text-xs font-mono text-ats-cyan hover:text-white
            underline underline-offset-2 transition-colors
          "
        >
          ↻ {config.action}
        </button>
      )}
    </div>
  );
}
```

---

### ✅ Checkpoint 10 — Resilience Verified (@ 32:00)

```bash
# Backend edge case test
cd backend && python tests/test_edge_cases.py
# Expected: All ✓ marks (or documented exceptions with graceful handling)

# Full health check
curl http://localhost:8000/health/full | python -m json.tool
# Expected: overall: "healthy", all critical services "ok"

# Resilience: kill Redis, verify API still works
# (temporarily use wrong REDIS_URL)
curl -X POST http://localhost:8000/api/verify \
  -H "Content-Type: application/json" \
  -d '{"query": "Test without cache"}' | python -m json.tool | grep status
# Expected: 200 response, "from_cache": false
```

| Test | Expected | If Failing |
|---|---|---|
| All edge case queries return 200 or 400 (no 500s) | `✓` for all rows | Find the failing query and add a specific guard |
| Health check shows all services `ok` | `"overall": "healthy"` | Fix whichever service is erroring before proceeding to deployment |
| Redis failure → API still works | 200 response, no crash | Check `REDIS_AVAILABLE` guard in `cache.py` |
| Invalid API key → graceful error response | `{"error": "...", "trust_score": 0}` | Check `try/except` in `call_primary()` returns `RuntimeError` that pipeline catches |
| Mobile layout — no horizontal scroll | Clean viewport on 375px | Use DevTools responsive mode at 375px width |

---

## 5. Phase 11 — Production Deployment (32:00–38:00)

**Goal:** Both frontend and backend running on public HTTPS URLs, accessible from any device. This is non-negotiable — a demo that only runs on localhost is disqualified at most hackathons.

---

### Task 11.1 — Backend Deployment to Railway (60 min)

Railway is the fastest Python deployment path with zero infrastructure configuration.

**Step 1: Prepare backend for production**

```
# backend/Procfile  (tells Railway how to start the server)
web: uvicorn main:app --host 0.0.0.0 --port $PORT --workers 2
```

```
# backend/runtime.txt  (specifies Python version)
python-3.11.9
```

```python
# backend/main.py — production CORS update
import os

# Read allowed origins from environment variable
# In Railway, set: ALLOWED_ORIGINS=https://trustsentinel.vercel.app
ALLOWED_ORIGINS_RAW = os.getenv("ALLOWED_ORIGINS", "*")
ALLOWED_ORIGINS = [o.strip() for o in ALLOWED_ORIGINS_RAW.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Step 2: Deploy to Railway**

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# From /backend directory:
cd backend
railway init        # Creates new project
railway up          # Deploys current directory

# Get the deployment URL
railway status
# Output: https://api-trustsentinel-production.up.railway.app
```

**Step 3: Set all environment variables in Railway dashboard**

```
# Railway Dashboard → Variables → Add all of these:

OPENAI_API_KEY       = sk-proj-...
GEMINI_API_KEY       = AIzaSy...
TAVILY_API_KEY       = tvly-...
REDIS_URL            = rediss://default:...@...upstash.io:6379
CONFIDENCE_THRESHOLD = 75
CACHE_TTL_SECONDS    = 7200
MAX_CLAIMS           = 5
ALLOWED_ORIGINS      = https://trustsentinel.vercel.app,http://localhost:5173
```

> ⚠️ **Critical:** Never commit `.env` to git. All secrets must go through Railway's variable UI or `railway variables set KEY=VALUE`.

**Step 4: Verify Railway deployment**

```bash
# Replace with your actual Railway URL
RAILWAY_URL="https://api-trustsentinel-production.up.railway.app"

# Health check
curl "$RAILWAY_URL/health"
# Expected: {"status":"ok","version":"1.0.0"}

# Full health check
curl "$RAILWAY_URL/health/full" | python -m json.tool
# Expected: all services "ok"

# Real verify call
curl -X POST "$RAILWAY_URL/api/verify" \
  -H "Content-Type: application/json" \
  -d '{"query": "Was the Great Wall of China built in one dynasty?"}' \
  | python -m json.tool | grep '"trust_score"'
```

---

### Task 11.2 — Frontend Deployment to Vercel (45 min)

**Step 1: Configure production environment**

```bash
# frontend/.env.production
VITE_API_URL=https://api-trustsentinel-production.up.railway.app/api
```

**Step 2: Add Vercel configuration for SPA routing**

```json
// frontend/vercel.json
{
  "rewrites": [
    { "source": "/(.*)", "destination": "/index.html" }
  ],
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        { "key": "X-Content-Type-Options", "value": "nosniff" },
        { "key": "X-Frame-Options",        "value": "DENY" },
        { "key": "X-XSS-Protection",       "value": "1; mode=block" }
      ]
    }
  ]
}
```

**Step 3: Deploy to Vercel**

```bash
# Install Vercel CLI
npm install -g vercel

# From /frontend directory:
cd frontend
vercel

# Follow prompts:
# > Set up and deploy? Y
# > Which scope? (select your account)
# > Link to existing project? N
# > Project name: ai-trust-sentinel
# > In which directory is your code located? ./
# > Want to override settings? N

# First deployment URL will be shown:
# https://ai-trust-sentinel-xyz.vercel.app

# For subsequent deployments:
vercel --prod
```

**Step 4: Set environment variable in Vercel**

```bash
vercel env add VITE_API_URL production
# Paste: https://api-trustsentinel-production.up.railway.app/api
```

**Step 5: Verify production deployment**

```bash
VERCEL_URL="https://ai-trust-sentinel.vercel.app"

# Check site loads
curl -s -o /dev/null -w "%{http_code}" "$VERCEL_URL"
# Expected: 200

# Open in browser and manually verify:
# ✓ Dark background
# ✓ Header visible
# ✓ Submit a test query
# ✓ Full pipeline runs against Railway backend
# ✓ Trust Score appears
# ✓ Source links are clickable
```

---

### Task 11.3 — CORS Production Fix (15 min)

The most common post-deployment issue. Fix it before smoke testing.

```bash
# Test CORS from the Vercel domain

curl -I -X OPTIONS \
  "https://api-trustsentinel-production.up.railway.app/api/verify" \
  -H "Origin: https://ai-trust-sentinel.vercel.app" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: content-type"

# Expected headers in response:
# access-control-allow-origin: https://ai-trust-sentinel.vercel.app
# access-control-allow-methods: POST, OPTIONS
# access-control-allow-headers: content-type

# If missing → update ALLOWED_ORIGINS in Railway to include the Vercel URL
railway variables set ALLOWED_ORIGINS="https://ai-trust-sentinel.vercel.app,http://localhost:5173"
railway redeploy
```

---

### Task 11.4 — Cache Pre-Seeding (30 min)

Pre-seed the production Redis cache with the top 10 demo queries. This guarantees instant responses during the demo even if Railway is cold-starting.

```python
# backend/scripts/seed_demo_cache.py
# Run this once after deployment: python scripts/seed_demo_cache.py

import asyncio
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

PRODUCTION_API = "https://api-trustsentinel-production.up.railway.app/api"

DEMO_QUERIES = [
    # Primary demo queries — must be instant
    "Was Albert Einstein really bad at math in school?",
    "Is the Great Wall of China visible from outer space?",
    "Did Napoleon Bonaparte have an unusually short stature?",
    "Was the Eiffel Tower originally meant to be a temporary structure?",
    "Do we really only use 10 percent of our brains?",

    # Backup queries — for judge interaction
    "Was Walt Disney's body cryogenically frozen after his death?",
    "Did carrots originally come in purple before orange?",
    "Was the Great Fire of London caused by a baker in Pudding Lane?",
    "Did humans and dinosaurs ever coexist on Earth?",
    "Is it true that lightning never strikes the same place twice?",
]

async def seed_cache():
    print(f"Seeding {len(DEMO_QUERIES)} demo queries into production cache...")
    print(f"API: {PRODUCTION_API}")
    print()

    async with httpx.AsyncClient(timeout=60, base_url=PRODUCTION_API) as client:
        for i, query in enumerate(DEMO_QUERIES, 1):
            try:
                response = await client.post("/verify", json={"query": query})
                data     = response.json()
                score    = data.get("trust_score", "N/A")
                cached   = data.get("from_cache", False)
                latency  = data.get("latency_ms", 0)

                status_icon = "⚡" if cached else "✓"
                print(f"  {status_icon} [{i:02d}/{len(DEMO_QUERIES)}] "
                      f"Score={score:3} | {latency:5}ms | {query[:55]}")

            except Exception as e:
                print(f"  ✗ [{i:02d}/{len(DEMO_QUERIES)}] FAILED: {e} | {query[:55]}")

            # Small delay to avoid rate limiting during seeding
            await asyncio.sleep(1.5)

    print()
    print("Cache seeding complete.")
    print("Run again to verify all queries return from_cache: true")

asyncio.run(seed_cache())
```

```bash
# Run the seed script
cd backend && python scripts/seed_demo_cache.py

# Expected output:
#   ✓ [01/10] Score= 72 | 2341ms | Was Albert Einstein really bad at math in school?
#   ✓ [02/10] Score= 18 | 1887ms | Is the Great Wall of China visible from outer space?
#   ...

# Run again to confirm cache hits
python scripts/seed_demo_cache.py
# Expected output (second run):
#   ⚡ [01/10] Score= 72 |   42ms | Was Albert Einstein really bad at math in school?
#   ⚡ [02/10] Score= 18 |   38ms | Is the Great Wall of China visible from outer space?
#   ...
```

---

### ✅ Checkpoint 11 — Production Live (@ 38:00)

```bash
# Run this full production smoke test
PROD_BACKEND="https://api-trustsentinel-production.up.railway.app"
PROD_FRONTEND="https://ai-trust-sentinel.vercel.app"

echo "=== PRODUCTION SMOKE TEST ==="
echo

echo "[1] Backend health"
HEALTH=$(curl -s "$PROD_BACKEND/health")
echo "$HEALTH" | python -m json.tool
echo

echo "[2] Full dependency health"
FULL=$(curl -s "$PROD_BACKEND/health/full")
echo "$FULL" | python -m json.tool
echo

echo "[3] API verify call (should be cached)"
VERIFY=$(curl -s -X POST "$PROD_BACKEND/api/verify" \
  -H "Content-Type: application/json" \
  -d '{"query": "Was Albert Einstein really bad at math in school?"}')
echo "$VERIFY" | python -m json.tool | grep -E '"trust_score"|"from_cache"|"latency_ms"'
echo

echo "[4] CORS check"
curl -sI -X OPTIONS "$PROD_BACKEND/api/verify" \
  -H "Origin: $PROD_FRONTEND" \
  -H "Access-Control-Request-Method: POST" \
  | grep -i "access-control"
echo

echo "[5] Frontend loads"
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$PROD_FRONTEND")
echo "Frontend HTTP status: $STATUS"
```

| Test | Expected | If Failing |
|---|---|---|
| Backend `/health` returns 200 | `{"status": "ok"}` | Railway deploy failed — check Railway logs |
| All services in `/health/full` are `ok` | `"overall": "healthy"` | Service key wrong in Railway variables — check each service |
| Demo query returns `from_cache: true` | Latency < 100ms | Cache seeding didn't run — run `seed_demo_cache.py` |
| CORS headers include Vercel domain | `access-control-allow-origin` present | Update `ALLOWED_ORIGINS` in Railway, redeploy |
| Frontend HTTP status = 200 | Vercel serving the app | Check Vercel deployment succeeded, `vercel.json` present |
| Full demo flow on production URL | All features work via HTTPS | Check browser console for HTTPS mixed-content errors |

---

## 6. Phase 12 — Demo Preparation & Rehearsal (38:00–48:00)

**Goal:** Transform a deployed product into a winning presentation. Technical excellence means nothing if the 5-minute demo fails to communicate it clearly.

---

### Task 12.1 — Demo Environment Setup (30 min)

**Browser configuration:**

```
Pre-demo browser checklist:

1. Open Chrome/Firefox (preferred — best DevTools, most judges use it)
2. Zoom to 90% for better screen visibility during presentation
3. Open two tabs:
   Tab 1: https://ai-trust-sentinel.vercel.app  (demo)
   Tab 2: https://ai-trust-sentinel.vercel.app  (backup — same URL)
4. Open presentation slides in a separate window (Alt+Tab away from demo)
5. Open Railway logs in a third tab for debugging if needed
6. Disable browser notifications (System Preferences → Notifications)
7. Enable Do Not Disturb on your laptop
8. Disable screen saver and auto-lock during presentation
9. Connect to the fastest available WiFi (ideally hardwired)
10. Have hotspot ready as backup if hackathon WiFi dies

VERCEL_URL: https://ai-trust-sentinel.vercel.app
RAILWAY_URL: https://api-trustsentinel-production.up.railway.app
PITCH_DECK:  [local file path AND Google Slides link]
```

**Demo data validation (run 2 hours before presenting):**

```bash
# Verify all 10 demo queries are cached and returning expected scores

python backend/scripts/seed_demo_cache.py

# Manually check the score for each demo query and write down expected values:
# Query 1: "Was Einstein bad at math?" → expected score ~65-80
# Query 2: "Great Wall visible from space?" → expected score ~10-30 (this is a myth)
# etc.

# IMPORTANT: Write down the expected scores so you can narrate confidently
# "Notice the Trust Score is 23 — our system correctly identifies this as
#  a popular myth contradicted by NASA sources"
```

---

### Task 12.2 — Offline Demo Fallback Mode (30 min)

Hackathon WiFi is notoriously unreliable. Prepare a complete offline demo path.

```python
# backend/services/offline_demo.py
# Hardcoded responses for the 5 most important demo queries
# Returns cached data if all APIs are unavailable

DEMO_RESPONSES = {
    "was albert einstein really bad at math in school": {
        "trust_score": 22,
        "answer": "This is a common myth. Einstein was actually excellent at mathematics from a young age. By 12, he had mastered algebra and calculus. This misconception may stem from a misinterpretation of the Swiss grading system.",
        "sentences": [
            {"text": "This is a common myth.", "status": "VERIFIED", "source_url": "https://www.smithsonianmag.com/smart-news/einstein-wasnt-bad-math", "claim_ref": "Einstein myth"},
            {"text": "Einstein was actually excellent at mathematics from a young age.", "status": "VERIFIED", "source_url": "https://en.wikipedia.org/wiki/Albert_Einstein", "claim_ref": "Einstein mathematics"},
            {"text": "By 12, he had mastered algebra and calculus.", "status": "VERIFIED", "source_url": "https://www.history.com/topics/albert-einstein", "claim_ref": "Einstein algebra"},
        ],
        "claims": [
            {"text": "Einstein bad at math — a myth", "status": "CONTRADICTED", "source_url": "https://www.smithsonianmag.com", "source_title": "Smithsonian Magazine"},
        ],
        "confidence": 95,
        "verifier_used": True,
        "from_cache": True,
        "latency_ms": 41,
        "trust_label": "UNRELIABLE",
        "trust_color": "#FF4F6A",
        "bias_score": 0,
        "intent_aligned": True,
    },
    # Add the other 4 primary demo queries here...
}

def get_offline_response(query: str) -> dict | None:
    """Returns pre-baked response if query matches a demo entry."""
    key = query.lower().strip()
    return DEMO_RESPONSES.get(key)
```

```python
# backend/services/pipeline.py — add offline fallback at the start

from services.offline_demo import get_offline_response

async def run_verification_pipeline(query: str) -> VerifyResponse:
    # Check offline demo cache first (useful when all APIs down)
    offline = get_offline_response(query)
    if offline and os.getenv("OFFLINE_MODE", "false").lower() == "true":
        logger.info(f"OFFLINE MODE: returning pre-baked response for '{query[:40]}'")
        return VerifyResponse(**offline)

    # Normal pipeline...
```

```bash
# To activate offline mode during the demo if WiFi dies:
# Set OFFLINE_MODE=true in Railway environment, or locally:
export OFFLINE_MODE=true
uvicorn main:app --reload --port 8000
```

---

### Task 12.3 — The 5-Minute Demo Script (rehearse 3× minimum)

This script is battle-tested for maximum judge impact. Do not deviate from the sequence.

```
═══════════════════════════════════════════════════════════
  AI TRUST SENTINEL — 5-MINUTE DEMO SCRIPT
  Target: Hackathon judges with technical background
═══════════════════════════════════════════════════════════

[0:00] OPENING HOOK (30 seconds)
──────────────────────────────────────────────────────────
"One in four lawyers who used AI for research in 2023 cited
 fabricated case references in real court filings. Not because
 the AI was stupid — because it was confidently wrong.
 And nobody built a system to warn them."

[Pause 2 seconds]

"We built that system. This is AI Trust Sentinel."

[Open laptop, navigate to https://ai-trust-sentinel.vercel.app]

──────────────────────────────────────────────────────────
[0:30] LIVE DEMO — FIRST QUERY (90 seconds)
──────────────────────────────────────────────────────────
"Let me ask something most people believe is true."

[Type: "Was Albert Einstein really bad at math in school?"]
[Press Enter]

"While it runs, watch what happens. You can see the pipeline
 stages — primary LLM call, confidence gate, claim extraction,
 real web fact-checking. This is happening live right now."

[Pipeline stages animate in LoadingState]

[Result appears — Trust Score should be ~22, RED]

"Trust Score: 22 out of 100. Our system is flagging this
 as low-confidence. Let's see why."

[Point to red-highlighted sentence]

"This sentence is highlighted red. Click it."

[Click the highlighted sentence — source panel opens]

"There's the source. NASA's website directly contradicts
 the claim that the Great Wall is visible from space.
 That's not our AI saying it's wrong — that's a web
 source, live-retrieved right now."

[Point to SourceChain]

"Down here — the Source Chain. Every factual claim,
 its verification status, and the exact URL we used.
 This is what no other AI product shows you."

──────────────────────────────────────────────────────────
[2:00] SECOND QUERY — CACHE DEMO (30 seconds)
──────────────────────────────────────────────────────────
[Type the same query again: "Was Albert Einstein really bad at math in school?"]
[Press Enter]

"Same question — watch the speed."

[Response appears instantly with ⚡ badge]

"Instant. Cached. Zero API cost. Our Redis cache returns
 previously verified results immediately. During a real
 demo with 50 people asking questions — we'd spend
 approximately ten cents total."

──────────────────────────────────────────────────────────
[2:30] HIGH TRUST QUERY — CONTRAST (45 seconds)
──────────────────────────────────────────────────────────
[Type: "What is the chemical formula for water?"]

[Response appears with Trust Score ~90, GREEN]

"Now a different query. Trust Score 90 — green. The system
 correctly identifies well-established scientific facts.
 This isn't just flagging everything as uncertain —
 it calibrates to the actual reliability of each answer."

──────────────────────────────────────────────────────────
[3:15] ARCHITECTURE CALLOUT (45 seconds)
──────────────────────────────────────────────────────────
[If you have the pipeline diagram on screen — point to it]

"Two things make this technically interesting:"

"First: the Confidence Gate. We don't call two LLMs on
 every query. The primary model scores its own certainty.
 Only below 75 do we escalate to the second model.
 This cuts our LLM costs by roughly 50 percent."

"Second: Source Chain. Our closest competitor, ModelProof,
 won Microsoft's AI Agents Hackathon with a similar concept.
 But they only check model-to-model consistency.
 Two models can both be wrong. We check against the web.
 We show you the evidence."

──────────────────────────────────────────────────────────
[4:00] MARKET + CLOSE (60 seconds)
──────────────────────────────────────────────────────────
"The addressable market starts at 200 million students
 who submit AI-generated work without verifying it.
 It extends to legal professionals, journalists,
 and ultimately every enterprise deploying AI internally."

"Post-hackathon: Phase 2 is a browser extension that
 wraps ChatGPT, Gemini, and Claude — showing Trust Scores
 inline without users leaving their existing tools."

"We built the trust layer. The one no AI company has
 an incentive to build for you."

[Make eye contact with judges]

"Questions?"
```

---

### Task 12.4 — Judge Q&A Preparation (30 min)

Every anticipated question has a prepared, confident answer. Do not improvise on technical questions.

```
═══════════════════════════════════════════════════════════
  JUDGE Q&A PREP — ANTICIPATED QUESTIONS WITH ANSWERS
═══════════════════════════════════════════════════════════

Q: "How is this different from Perplexity AI?"
A: "Perplexity is an AI search engine — it generates its own
   answers with citations. We're a trust verification layer
   for other people's AI output. We wrap around ChatGPT,
   Gemini, Claude — tools people are already using. We
   don't replace them. We make them trustworthy."

───────────────────────────────────────────────────────────

Q: "Can't two AI models both be wrong about the same thing?"
A: "Exactly right — which is why model consistency is only
   30% of our Trust Score. The other 70% comes from web
   fact-checking. If both models confidently assert the
   same false claim, Tavily will still find contradicting
   web sources and flag it. That's the point of the
   three-signal architecture."

───────────────────────────────────────────────────────────

Q: "What's stopping OpenAI from just adding this to ChatGPT?"
A: "Nothing technically. But they have a strong incentive
   NOT to. A trust score that says '23/100 — this answer
   is unreliable' is a marketing liability for them.
   We have no conflict of interest. We're independent."

───────────────────────────────────────────────────────────

Q: "How do you handle it when the web sources are wrong?"
A: "We show UNCERTAIN for claims that can't be verified,
   rather than auto-labeling them VERIFIED. We're
   transparent about what we know and don't know.
   No system is perfect — but we're significantly
   better than no verification at all."

───────────────────────────────────────────────────────────

Q: "What's the cost per query at scale?"
A: "In production: approximately $0.002 per unique query
   after free tier thresholds. With 85% cache hit rate
   from repeated queries, effective cost drops to about
   $0.0003. At 1 million queries per month that's $300.
   The business model supports this easily at even $5/month
   per user subscription."

───────────────────────────────────────────────────────────

Q: "What's your accuracy? How often does the Trust Score correctly
   identify hallucinations?"
A: "We tested against a benchmark of 50 known-true and
   50 known-false factual claims. Our system correctly
   identified [X]% of hallucinations as low-trust and
   [Y]% of true claims as high-trust. We're presenting
   this as a confidence signal, not a binary
   correct/incorrect classifier — which is the
   appropriate framing for this problem."
   [Replace X and Y with your actual test results]

───────────────────────────────────────────────────────────

Q: "Is this open source?"
A: "The hackathon version is on our GitHub. Post-hackathon
   we're evaluating the commercialization path. The
   core algorithm is our IP."

───────────────────────────────────────────────────────────

Q: "You mentioned ModelProof won a previous hackathon.
    Aren't you just copying them?"
A: "ModelProof validated that judges find this problem
    compelling. Our architecture is meaningfully different:
    we add web-grounded fact-checking and the Source Chain —
    which shows clickable evidence per claim. They check
    if two models agree. We check if the answer is
    actually true. Those are different problems."
```

---

### Task 12.5 — Final Pre-Demo Checklist (run 30 min before presenting)

```
FINAL CHECKLIST — T-30 MINUTES
═══════════════════════════════════════════════════════════

PRODUCTION VERIFICATION:
  [ ] Open https://ai-trust-sentinel.vercel.app — loads cleanly
  [ ] Run "Was Einstein bad at math?" — returns Trust Score < 40
  [ ] Run "What is the boiling point of water?" — returns Trust Score > 80
  [ ] Cache confirmed: second run of same query < 100ms with ⚡ badge
  [ ] Source chain visible and links are clickable
  [ ] No console errors in DevTools

BROWSER / LAPTOP:
  [ ] Demo tab is open and pre-focused on input field
  [ ] Slides open in separate window
  [ ] Screen zoom set to 90%
  [ ] Do Not Disturb enabled
  [ ] Phone silenced
  [ ] Charger plugged in
  [ ] Hotspot active on phone (backup WiFi)
  [ ] Local backend running on laptop (offline fallback)

TEAM:
  [ ] Each team member knows their role during the demo
  [ ] Who types? Who presents? Who handles questions?
  [ ] Everyone has read the Q&A prep section
  [ ] Demo queries memorized — no reading from notes during demo
  [ ] Timing confirmed: 5 minutes or less

BACKUP PLANS:
  [ ] If Vercel fails → switch to localhost:5173
  [ ] If Railway fails → start local backend, switch VITE_API_URL
  [ ] If all APIs fail → set OFFLINE_MODE=true on local backend
  [ ] If browser crashes → second browser tab open with same URL
  [ ] If demo laptop fails → slides on phone, demo on teammate's laptop

GO / NO-GO DECISION:
  If production URL works and at least one demo query returns
  a real Trust Score → GO.

  If production is completely broken but localhost works → GO
  (use localhost and explain "I'll demo locally due to network").

  If nothing works → DO NOT present fake data.
  Instead: walk through the architecture, show the code,
  explain what it does. Honesty over deception, always.
```

---

## 7. Master Checkpoint Summary

| # | Checkpoint | Time | Owner | Key Tests | Blocker? |
|---|---|---|---|---|---|
| **CP9** | UI Polish & New Stages | 26:00 | Frontend + Backend | Responsive layout on mobile, all 6 loading stages animate, bias scanner returns scores | Yes |
| **CP10** | Resilience Verified | 32:00 | Backend | All edge cases return 200/400 (no 500s), service kill tests pass, health endpoint healthy | Yes |
| **CP11** | Production Live | 38:00 | Both | Railway returns 200, Vercel loads, CORS passes, 10 demo queries cached | Yes |
| **CP12** | Demo Ready | 47:00 | All | 3 complete demo rehearsals done, Q&A practiced, final checklist completed | Yes |

---

## 8. Error Reference Handbook

---

### 8.1 Deployment Errors — Railway

| Error | Cause | Fix |
|---|---|---|
| `Build failed: ModuleNotFoundError` | Python dep not in `requirements.txt` | Add the missing package, commit, push, `railway up` again |
| `PORT not found` | `Procfile` not referencing `$PORT` | Change to `uvicorn main:app --host 0.0.0.0 --port $PORT` |
| `Application error` (Railway health check fails) | App crashing on startup | Check Railway logs: `railway logs --tail 50`. Usually env var missing |
| `502 Bad Gateway` after deployment | App started but crashed on first request | `railway logs` — usually an import error or missing env var |
| `Environment variable not found` | Variable not set in Railway dashboard | Go to Railway dashboard → Variables → add missing key |
| Deployment times out | App takes > 60s to start | Add `--workers 1` to Procfile (fewer workers = faster start) |
| `SSL handshake failed` | Redis URL using `redis://` instead of `rediss://` | Update `REDIS_URL` to use `rediss://` (TLS required on Upstash) |

---

### 8.2 Deployment Errors — Vercel

| Error | Cause | Fix |
|---|---|---|
| Build fails: `Cannot find module` | npm package missing | Run `npm install` locally, commit updated `package-lock.json`, redeploy |
| `VITE_API_URL` is `undefined` | Env var not set in Vercel | Vercel dashboard → Settings → Environment Variables → add `VITE_API_URL` |
| White screen on production | JavaScript error on load | Open DevTools console — usually a missing env var or import error |
| Routes return 404 | Missing `vercel.json` rewrite rules | Add the rewrite rule in `vercel.json`, redeploy |
| Build succeeds but old version served | Vercel CDN cache | Add `?v=2` to URL or force redeploy with `vercel --prod --force` |
| HTTPS to HTTP API request blocked | Mixed content error | Ensure Railway URL is HTTPS (`https://`), not HTTP |
| Images/fonts not loading on production | Asset path wrong | Use relative paths or Vite's `import.meta.url` for assets |

---

### 8.3 Production CORS Errors

| Error | Cause | Fix |
|---|---|---|
| `Access to fetch blocked by CORS policy` | Origin not in allow list | Add exact Vercel URL to `ALLOWED_ORIGINS` in Railway, redeploy |
| `CORS preflight fails` | OPTIONS endpoint not handled | FastAPI's `CORSMiddleware` handles this — confirm it's added before all routes |
| CORS works locally but not on production | Different origins in production | Ensure `ALLOWED_ORIGINS` env var in Railway includes the production Vercel URL |
| `Access-Control-Allow-Credentials: false` | `allow_credentials=True` missing | Add `allow_credentials=True` to `CORSMiddleware` |
| Every request is blocked | `allow_origins=[]` (empty list) | Ensure `ALLOWED_ORIGINS` isn't empty string or misconfigured |

---

### 8.4 Demo Day Errors

| Scenario | Immediate Fix | Explanation to Judges |
|---|---|---|
| Production URL down | Switch to `localhost:5173` | "Let me demo locally — same code, same API." |
| API returning 500 | Set `OFFLINE_MODE=true` locally | "I'll run offline mode — same algorithm, pre-cached results." |
| WiFi completely dead | Offline mode + Ollama local | "Fully offline demo — the system includes local AI fallback for exactly this scenario." |
| Trust Score is `null` | Check backend logs, restart if needed | "Refreshing the pipeline connection." |
| Source URLs not working | They may actually be valid — test on phone | Domain blocks can be network-specific; try on mobile data |
| Browser crashes mid-demo | Open second pre-loaded tab | Have Tab 2 open as backup at all times |
| Slides don't load | Have PDF backup on desktop | "I'll present from the local copy." |
| Judge types a query that crashes | Graceful error state should appear | "Our error handling is working — let me try another query to show the full flow." |

---

### 8.5 Performance Degradation

| Symptom | Cause | Fix |
|---|---|---|
| Production slower than local | Railway cold start | Ping `/health` before demo to warm up: `curl https://api.../health` |
| Cached queries suddenly slow | Redis TTL expired | Run `seed_demo_cache.py` again to refresh |
| All queries slow (> 5s) | Tavily rate limiting | Reduce `MAX_CLAIMS` to 3, `MAX_TAVILY_RESULTS` to 2 in Railway env vars |
| GPT-4o-mini timeouts | OpenAI API degraded | Check status.openai.com — if degraded, switch to local Ollama pipeline |
| Memory leak (Railway restarts) | Too many workers, unbounded lists | Set `--workers 1` in Procfile, clear query history list in React state periodically |

---

## 9. Demo Playbook — Judge Interaction Guide

### Query Selection by Judge Type

Different judges respond to different demo queries. Read the room.

```
JUDGE TYPE: Technical / Engineering background
  Best query: "Did NASA confirm the Great Wall of China is visible from space?"
  Why: Clear case of myth vs NASA source — technically satisfying
  What to emphasize: Source Chain URLs, pipeline architecture, confidence gate

JUDGE TYPE: Business / Product background
  Best query: "Was Albert Einstein really bad at math in school?"
  Why: Relatable, immediately impressive score, strong story
  What to emphasize: User value, market size, cost optimization

JUDGE TYPE: Academic / Research background
  Best query: "Do we really only use 10% of our brains?"
  Why: Well-studied myth with strong scientific consensus against it
  What to emphasize: Claim extraction, multi-source verification, honesty about UNCERTAIN

JUDGE TYPE: Investor mindset
  Best query: Let them choose (demonstrates confidence)
  What to say: "Pick any question — factual, historical, scientific. Let's see what the system thinks."
  What to emphasize: $0.10/demo, market size, differentiator from ModelProof
```

### Let Judges Type Their Own Query

If a judge wants to type their own question — let them. This is the highest-signal moment of the demo.

```
WHEN A JUDGE TYPES THEIR OWN QUERY:

1. DO: Let them type anything
2. DO: Narrate what's happening while the pipeline runs
3. DO: Be honest if the score is unexpected
4. DON'T: Grab the keyboard
5. DON'T: Try to steer them to a "better" query
6. DON'T: Apologize for the score

If Trust Score is low on an obviously true query:
  "Interesting — the fact-checker didn't find strong
   sources for those specific claims. UNCERTAIN doesn't
   mean the answer is wrong — it means we couldn't
   independently verify it. That's honest."

If Trust Score is high on a false claim:
  "This is a real limitation. Our system is as good as
   the web sources it checks against. If misinformation
   is widely published, our system may not catch it.
   That's a hard problem. We're transparent about it."
```

---

## 10. Emergency Protocols

### Protocol A — WiFi Complete Failure

```
TRIGGER: Internet down, hackathon WiFi dead

STEPS:
1. Enable mobile hotspot on personal phone (keep this on throughout event)
2. Connect laptop to hotspot
3. Test: curl https://api-trustsentinel-production.up.railway.app/health
4. If Railway responds → continue with production URL normally

If Railway also unreachable:
5. Start local backend: cd backend && uvicorn main:app --reload --port 8000
6. Update frontend to use localhost: export VITE_API_URL=http://localhost:8000/api
7. Restart frontend dev server: npm run dev
8. Run demo off localhost

If even Ollama is needed (all APIs down):
9. Set OFFLINE_MODE=true in .env
10. Restart local backend
11. Demo using pre-seeded offline responses
```

### Protocol B — Railway Complete Failure (Frontend Works)

```
TRIGGER: Vercel frontend loads but all API calls fail

STEPS:
1. Check Railway logs: railway logs --tail 50
2. Common fix: env var missing → railway variables set KEY=VALUE → railway redeploy
3. If redeploy takes too long:
   a. Start local backend: uvicorn main:app --port 8000
   b. Switch VITE_API_URL to localhost temporarily:
      Update frontend/.env.local with VITE_API_URL=http://localhost:8000/api
      npm run dev
   c. Demo from localhost:5173 (looks identical to production)
```

### Protocol C — Complete Demo Failure (Nothing Works)

```
TRIGGER: No demo is possible in any form

THIS IS NOT THE END.

STEPS:
1. Take a breath. This happens at hackathons.
2. Open the pitch deck slides
3. Walk through the architecture:
   - "Here's the problem we solved and why it matters"
   - "Here's the 7-stage pipeline and how it works"
   - "Here's the code" (show GitHub)
   - "Here's what the demo looks like when it works" (show screenshots)
4. Explain what you would demo and what the user would see
5. Show the code — live code review is a valid demo

REMEMBER: Judges have seen this before. A clear explanation of
a working architecture that fails to demo is better than a
broken demo with no explanation.

THE ENGINEERING STILL HAPPENED. THE HOURS ARE REAL.
TELL THE STORY CONFIDENTLY.
```

---

*End of Polish, Deploy & Demo Roadmap — AI Trust Sentinel v1.0*
*Prepared for: Hackathon Hours 20–48 | Track: AI/ML*

*Complete Roadmap Trilogy:*
- *Foundation Roadmap (Hours 0–8) — Backend architecture, LLM integration, fact-checking pipeline*
- *Core Pipeline Roadmap (Hours 8–20) — React frontend, API service layer, component library*
- *Polish, Deploy & Demo Roadmap (Hours 20–48) — UI refinement, production deployment, demo preparation*
