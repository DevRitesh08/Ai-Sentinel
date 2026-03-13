# backend/services/pipeline.py
import time
import asyncio
import logging
from services.llm_primary     import call_primary
from services.llm_verifier    import call_verifier
from services.gate            import should_escalate, calculate_consistency_score
from services.claim_extractor import extract_claims, validate_claims
from services.fact_checker    import fact_check_all_claims
from services.trust_score     import calculate_trust_score, score_to_label, score_to_color
from services.cache           import get_cached, set_cached
from services.sentence_segmenter import split_into_sentences, annotate_sentences
from services.bias_scanner    import scan_response
from services.intent_checker  import check_intent_alignment
from services.offline_demo    import get_offline_response
import os
from models.schemas           import VerifyResponse, ClaimResult, ClaimStatus

logger = logging.getLogger(__name__)

PIPELINE_TIMEOUT_SECONDS = 20  # Hard cap to prevent slow APIs from stalling the endpoint


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


async def run_verification_pipeline(query: str) -> VerifyResponse:
    """
    Master orchestrator for the 7-stage AI Trust Sentinel pipeline.

    Stages:
    1. Redis cache check — instant return if seen before
    2. GPT-4o-mini primary answer with confidence score
    3. Confidence gate decision (threshold = 75)
    4. Gemini Flash verifier (only if gate triggers) — parallel with stage 5
    5. Claim extraction from primary answer — parallel with stage 4
    6. Tavily fact-check all claims concurrently
    7. Sentence segmentation + Trust Score aggregation + cache write + return

    Returns a complete VerifyResponse. Never raises.
    """
    try:
        async with asyncio.timeout(PIPELINE_TIMEOUT_SECONDS):
            return await _run_pipeline(query)
    except asyncio.TimeoutError:
        logger.error("Pipeline timed out after 20s")
        return VerifyResponse(
            trust_score=0,
            answer="Request timed out. Please try again.",
            confidence=0,
            verifier_used=False,
            claims=[],
            sentences=[],
            from_cache=False,
            latency_ms=PIPELINE_TIMEOUT_SECONDS * 1000,
            error="Pipeline timeout",
            trust_label="UNRELIABLE — VERIFY MANUALLY",
            trust_color="#FF4F6A",
        )
    except Exception as e:
        logger.error(f"Pipeline error: {e}")
        return VerifyResponse(
            trust_score=0,
            answer=f"An error occurred during verification: {str(e)}",
            confidence=0,
            verifier_used=False,
            claims=[],
            sentences=[],
            from_cache=False,
            latency_ms=0,
            error=str(e),
            trust_label="ERROR",
            trust_color="#EF4444",
        )


async def _run_pipeline(query: str) -> VerifyResponse:
    """Internal pipeline — called inside timeout wrapper."""
    start_time = time.time()
    timer = PipelineTimer()

    # Check offline demo cache first (useful when all APIs down)
    offline = get_offline_response(query)
    if offline and os.getenv("OFFLINE_MODE", "false").lower() == "true":
        logger.info(f"OFFLINE MODE: returning pre-baked response for '{query[:40]}'")
        # offline is already formatted like VerifyResponse output data
        return VerifyResponse(**offline)

    # ── Stage 1: Cache check ─────────────────────────────────────────────────
    cached = get_cached(query)
    timer.mark("cache_check")
    if cached:
        return VerifyResponse(**cached)

    # ── Stage 2: Primary LLM call ────────────────────────────────────────────
    try:
        primary = await call_primary(query)
    except Exception as e:
        logger.error(f"Pipeline failed at primary LLM: {e}")
        return VerifyResponse(
            trust_score=0,
            answer="Service temporarily unavailable. Please try again.",
            confidence=0,
            verifier_used=False,
            claims=[],
            sentences=[],
            from_cache=False,
            latency_ms=int((time.time() - start_time) * 1000),
            error=str(e),
            trust_label="UNRELIABLE — VERIFY MANUALLY",
            trust_color="#FF4F6A",
        )
    timer.mark("primary_llm")

    # ── Stage 3: Confidence gate decision ────────────────────────────────────
    escalate = should_escalate(primary["confidence"])
    timer.mark("gate_decision")

    # ── Stage 4 & 5: Run verifier and claim extraction in parallel ───────────
    verifier_task  = call_verifier(query) if escalate else asyncio.sleep(0, result=None)
    extractor_task = extract_claims(primary["answer"])

    verifier_raw, raw_claims = await asyncio.gather(
        verifier_task,
        extractor_task,
        return_exceptions=True
    )
    timer.mark("parallel_llm_and_extraction")

    # ── Stage 5: Post-gather processing ──────────────────────────────────────
    verifier_answer = verifier_raw["answer"] if isinstance(verifier_raw, dict) else None
    verifier_used   = escalate and verifier_answer is not None
    claims          = validate_claims(raw_claims if isinstance(raw_claims, list) else [])

    # ── Stage 5b: Consistency score (only when verifier was actually used) ───
    consistency = None
    if verifier_used and verifier_answer:
        consistency = calculate_consistency_score(primary["answer"], verifier_answer)

    # ── Stage 6: Fact-check + bias scan + intent check (all parallel) ────────
    bias_task    = scan_response(primary["answer"])
    intent_task  = check_intent_alignment(query, primary["answer"])
    factcheck_task = fact_check_all_claims(claims) if claims else asyncio.sleep(0, result=[])

    bias_raw, intent_raw, fact_results_raw = await asyncio.gather(
        bias_task, intent_task, factcheck_task,
        return_exceptions=True
    )
    timer.mark("parallel_factcheck_bias_intent")

    # Safe extraction
    bias   = bias_raw   if isinstance(bias_raw, dict)   else {}
    intent = intent_raw if isinstance(intent_raw, dict) else {}
    fact_results = fact_results_raw if isinstance(fact_results_raw, list) else []

    # ── Stage 7: Sentence segmentation + Trust score + finalize ──────────────
    trust_score = calculate_trust_score(
        primary_confidence=primary["confidence"],
        consistency_score=consistency,
        fact_results=fact_results,
        verifier_used=verifier_used
    )

    # Segment and annotate sentences
    sentences_raw = split_into_sentences(primary["answer"])
    sentences_ann = annotate_sentences(sentences_raw, fact_results)
    timer.mark("score_and_segment")

    elapsed_ms = int((time.time() - start_time) * 1000)

    result = VerifyResponse(
        trust_score     = trust_score,
        answer          = primary["answer"],
        confidence      = primary["confidence"],
        verifier_used   = verifier_used,
        claims          = fact_results,
        sentences       = sentences_ann,
        from_cache      = False,
        latency_ms      = elapsed_ms,
        trust_label     = score_to_label(trust_score),
        trust_color     = score_to_color(trust_score),
        bias_score      = bias.get("bias_score"),
        toxicity_score  = bias.get("toxicity_score"),
        bias_flags      = bias.get("flags", []),
        intent_aligned  = intent.get("aligned"),
        alignment_score = intent.get("alignment_score"),
    )

    # Cache the result for future identical queries
    set_cached(query, result.model_dump())

    logger.info(
        f"Pipeline complete | score={trust_score} | verifier={verifier_used} "
        f"| claims={len(fact_results)} | latency={elapsed_ms}ms | cached=True"
    )
    logger.info(f"[PIPELINE SUMMARY] {timer.summary()}")

    return result
