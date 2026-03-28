import asyncio
import logging
import os
import time

from models.schemas import ConversationTurn, VerifyResponse
from services.bias_scanner import scan_response
from services.cache import get_cached, set_cached
from services.claim_extractor import extract_claims, validate_claims
from services.context_resolver import resolve_query
from services.fact_checker import fact_check_all_claims
from services.gate import calculate_consistency_score, should_escalate
from services.intent_checker import check_intent_alignment
from services.llm_primary import call_primary
from services.llm_verifier import call_verifier
from services.offline_demo import get_offline_response
from services.sentence_segmenter import annotate_sentences, split_into_sentences
from services.trust_score import calculate_trust_score, score_to_color, score_to_label

logger = logging.getLogger(__name__)

PIPELINE_TIMEOUT_SECONDS = 20


class PipelineTimer:
    def __init__(self):
        self.start = time.time()
        self.stages = {}

    def mark(self, stage: str):
        self.stages[stage] = round((time.time() - self.start) * 1000)
        logger.info(f"[PIPELINE] {stage}: {self.stages[stage]}ms elapsed")

    def summary(self) -> dict:
        return self.stages


def _build_error_response(message: str, error: str, latency_ms: int = 0) -> VerifyResponse:
    return VerifyResponse(
        trust_score=0,
        answer=message,
        confidence=0,
        verifier_used=False,
        claims=[],
        sentences=[],
        from_cache=False,
        latency_ms=latency_ms,
        error=error,
        trust_label="UNRELIABLE - VERIFY MANUALLY" if message != "An error occurred during verification." else "ERROR",
        trust_color="#FF4F6A" if message != "An error occurred during verification." else "#EF4444",
        resolved_query=None,
        used_context=False,
        context_turns_used=0,
    )


async def run_verification_pipeline(
    query: str,
    history: list[ConversationTurn] | None = None,
) -> VerifyResponse:
    try:
        async with asyncio.timeout(PIPELINE_TIMEOUT_SECONDS):
            return await _run_pipeline(query, history or [])
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
            trust_label="UNRELIABLE - VERIFY MANUALLY",
            trust_color="#FF4F6A",
            resolved_query=None,
            used_context=False,
            context_turns_used=0,
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
            resolved_query=None,
            used_context=False,
            context_turns_used=0,
        )


async def _run_pipeline(query: str, history: list[ConversationTurn]) -> VerifyResponse:
    start_time = time.time()
    timer = PipelineTimer()

    resolution = await resolve_query(query, history)
    resolved_query = resolution.resolved_query
    logger.info(
        f"Verifying raw='{query[:80]}' | resolved='{resolved_query[:120]}' | used_context={resolution.used_context}"
    )
    timer.mark("resolve_query")

    offline = get_offline_response(resolved_query)
    if offline and os.getenv("OFFLINE_MODE", "false").lower() == "true":
        logger.info(f"OFFLINE MODE: returning pre-baked response for '{resolved_query[:40]}'")
        return VerifyResponse(
            **offline,
            resolved_query=resolved_query,
            used_context=resolution.used_context,
            context_turns_used=resolution.context_turns_used,
        )

    cached = get_cached(resolved_query)
    timer.mark("cache_check")
    if cached:
        cached["resolved_query"] = resolved_query
        cached["used_context"] = resolution.used_context
        cached["context_turns_used"] = resolution.context_turns_used
        return VerifyResponse(**cached)

    try:
        primary = await call_primary(resolved_query)
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
            trust_label="UNRELIABLE - VERIFY MANUALLY",
            trust_color="#FF4F6A",
            resolved_query=resolved_query,
            used_context=resolution.used_context,
            context_turns_used=resolution.context_turns_used,
        )
    timer.mark("primary_llm")

    escalate = should_escalate(primary["confidence"])
    timer.mark("gate_decision")

    verifier_task = call_verifier(resolved_query) if escalate else asyncio.sleep(0, result=None)
    extractor_task = extract_claims(primary["answer"])

    verifier_raw, raw_claims = await asyncio.gather(
        verifier_task,
        extractor_task,
        return_exceptions=True,
    )
    timer.mark("parallel_llm_and_extraction")

    verifier_answer = verifier_raw["answer"] if isinstance(verifier_raw, dict) else None
    verifier_used = escalate and verifier_answer is not None
    claims = validate_claims(raw_claims if isinstance(raw_claims, list) else [])

    consistency = None
    if verifier_used and verifier_answer:
        consistency = calculate_consistency_score(primary["answer"], verifier_answer)

    bias_task = scan_response(primary["answer"])
    intent_task = check_intent_alignment(resolved_query, primary["answer"])
    factcheck_task = fact_check_all_claims(claims) if claims else asyncio.sleep(0, result=[])

    bias_raw, intent_raw, fact_results_raw = await asyncio.gather(
        bias_task,
        intent_task,
        factcheck_task,
        return_exceptions=True,
    )
    timer.mark("parallel_factcheck_bias_intent")

    bias = bias_raw if isinstance(bias_raw, dict) else {}
    intent = intent_raw if isinstance(intent_raw, dict) else {}
    fact_results = fact_results_raw if isinstance(fact_results_raw, list) else []

    trust_score = calculate_trust_score(
        primary_confidence=primary["confidence"],
        consistency_score=consistency,
        fact_results=fact_results,
        verifier_used=verifier_used,
    )

    sentences_raw = split_into_sentences(primary["answer"])
    sentences_ann = annotate_sentences(sentences_raw, fact_results)
    timer.mark("score_and_segment")

    elapsed_ms = int((time.time() - start_time) * 1000)

    result = VerifyResponse(
        trust_score=trust_score,
        answer=primary["answer"],
        confidence=primary["confidence"],
        verifier_used=verifier_used,
        claims=fact_results,
        sentences=sentences_ann,
        from_cache=False,
        latency_ms=elapsed_ms,
        trust_label=score_to_label(trust_score),
        trust_color=score_to_color(trust_score),
        bias_score=bias.get("bias_score"),
        toxicity_score=bias.get("toxicity_score"),
        bias_flags=bias.get("flags", []),
        intent_aligned=intent.get("aligned"),
        alignment_score=intent.get("alignment_score"),
        resolved_query=resolved_query,
        used_context=resolution.used_context,
        context_turns_used=resolution.context_turns_used,
    )

    set_cached(resolved_query, result.model_dump())

    logger.info(
        f"Pipeline complete | score={trust_score} | verifier={verifier_used} "
        f"| claims={len(fact_results)} | latency={elapsed_ms}ms | cached=True"
    )
    logger.info(f"[PIPELINE SUMMARY] {timer.summary()}")

    return result
