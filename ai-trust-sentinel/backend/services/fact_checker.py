# backend/services/fact_checker.py
import os
import asyncio
import logging
from tavily import TavilyClient
from models.schemas import ClaimResult, ClaimStatus

logger = logging.getLogger(__name__)
MAX_RESULTS = int(os.getenv("MAX_TAVILY_RESULTS", "3"))

# Synchronous Tavily client — wrapped in run_in_executor for async use
tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))


async def fact_check_claim(claim: str) -> ClaimResult:
    """
    Fact-checks a single claim against live web sources via Tavily.
    Returns a ClaimResult with VERIFIED / UNCERTAIN / CONTRADICTED status.
    Never raises — returns UNCERTAIN on any failure.
    """
    try:
        # Tavily is synchronous — run in thread executor to avoid blocking the event loop
        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(
            None,
            lambda: tavily_client.search(
                query=claim,
                max_results=MAX_RESULTS,
                search_depth="basic"  # Use "advanced" for better results (costs more API credits)
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

        top_result  = results["results"][0]
        source_url   = top_result.get("url", "")
        source_title = top_result.get("title", "")
        source_body  = top_result.get("content", "")

        # Classify based on keyword overlap with source content
        status = classify_claim(claim, source_body)

        logger.info(f"Claim: '{claim[:40]}...' → {status} | {source_url[:50]}")
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
    Determines VERIFIED / UNCERTAIN / CONTRADICTED based on word overlap
    between the claim and search result content.

    Thresholds:
    - overlap ≥ 0.35 → VERIFIED   (strong keyword match)
    - overlap ≥ 0.15 → UNCERTAIN  (weak match, can't confirm or deny)
    - overlap < 0.15 → CONTRADICTED (source doesn't support the claim)

    Note: This is a heuristic baseline. For production accuracy, replace with
    an LLM-based classification call.
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
    Any individual failure is caught and returned as UNCERTAIN.
    """
    tasks = [fact_check_claim(c) for c in claims]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    clean_results = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            logger.error(f"Fact-check task {i} raised: {result}")
            clean_results.append(ClaimResult(
                text=claims[i],
                status=ClaimStatus.UNCERTAIN,
                source_url=None,
                source_title="Fact-check error"
            ))
        else:
            clean_results.append(result)

    return clean_results
