import asyncio
import logging
import os

from tavily import TavilyClient

from models.schemas import ClaimResult, ClaimStatus

logger = logging.getLogger(__name__)
MAX_RESULTS = int(os.getenv("MAX_TAVILY_RESULTS", "3"))


def get_tavily_client() -> TavilyClient | None:
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        return None
    return TavilyClient(api_key=api_key)


async def fact_check_claim(claim: str) -> ClaimResult:
    """
    Fact-checks a single claim via Tavily.
    Returns UNCERTAIN when live fact-checking is unavailable.
    """
    try:
        tavily_client = get_tavily_client()
        if tavily_client is None:
            logger.warning("TAVILY_API_KEY not set - skipping live fact-check")
            return ClaimResult(
                text=claim,
                status=ClaimStatus.UNCERTAIN,
                source_url=None,
                source_title="Tavily key missing",
            )

        loop = asyncio.get_running_loop()
        results = await loop.run_in_executor(
            None,
            lambda: tavily_client.search(
                query=claim,
                max_results=MAX_RESULTS,
                search_depth="basic",
            ),
        )

        if not results or not results.get("results"):
            logger.warning(f"No Tavily results for claim: {claim[:50]}")
            return ClaimResult(
                text=claim,
                status=ClaimStatus.UNCERTAIN,
                source_url=None,
                source_title="No sources found",
            )

        top_result = results["results"][0]
        source_url = top_result.get("url", "")
        source_title = top_result.get("title", "")
        source_body = top_result.get("content", "")
        status = classify_claim(claim, source_body)

        logger.info(f"Claim: '{claim[:40]}...' -> {status} | {source_url[:50]}")
        return ClaimResult(
            text=claim,
            status=status,
            source_url=source_url,
            source_title=source_title,
        )
    except Exception as e:
        logger.error(f"Fact-check failed for '{claim[:40]}': {e}")
        return ClaimResult(
            text=claim,
            status=ClaimStatus.UNCERTAIN,
            source_url=None,
            source_title="Fact-check unavailable",
        )


def classify_claim(claim: str, source_content: str) -> ClaimStatus:
    """
    Baseline overlap heuristic:
    - overlap >= 0.35 -> VERIFIED
    - overlap >= 0.15 -> UNCERTAIN
    - overlap < 0.15 -> CONTRADICTED
    """
    claim_words = set(claim.lower().split())
    source_words = set(source_content.lower().split())
    overlap = len(claim_words & source_words) / max(len(claim_words), 1)

    if overlap >= 0.35:
        return ClaimStatus.VERIFIED
    if overlap >= 0.15:
        return ClaimStatus.UNCERTAIN
    return ClaimStatus.CONTRADICTED


async def fact_check_all_claims(claims: list[str]) -> list[ClaimResult]:
    tasks = [fact_check_claim(claim) for claim in claims]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    clean_results = []
    for index, result in enumerate(results):
        if isinstance(result, Exception):
            logger.error(f"Fact-check task {index} raised: {result}")
            clean_results.append(
                ClaimResult(
                    text=claims[index],
                    status=ClaimStatus.UNCERTAIN,
                    source_url=None,
                    source_title="Fact-check error",
                )
            )
        else:
            clean_results.append(result)

    return clean_results
