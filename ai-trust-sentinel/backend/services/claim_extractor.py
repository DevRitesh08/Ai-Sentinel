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
    Extracts 1–5 factual claim strings from an LLM answer.
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
            temperature=0.1,   # Very low temp for consistent, deterministic extraction
        )
        raw = json.loads(response.choices[0].message.content)
        claims = raw.get("claims", [])

        if not claims:
            logger.warning("Claim extractor returned empty list — using full text as fallback")
            return [text[:300]]  # Fallback: treat whole answer as one claim

        logger.info(f"Extracted {len(claims)} claims")
        return claims[:MAX_CLAIMS]

    except Exception as e:
        logger.error(f"Claim extraction failed: {e} — using fallback")
        return [text[:300]]  # Never fail silently — always return something


def validate_claims(claims: list[str]) -> list[str]:
    """
    Removes empty, too-short, or duplicate claims.
    Returns a clean deduplicated list ready for fact-checking.
    """
    seen = set()
    valid = []
    for claim in claims:
        claim = claim.strip()
        if len(claim) < 10:
            continue  # Skip trivially short claims
        key = claim.lower()[:50]
        if key in seen:
            continue  # Skip near-duplicates
        seen.add(key)
        valid.append(claim)
    return valid
