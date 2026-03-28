import json
import logging
import os

from openai import AsyncOpenAI

logger = logging.getLogger(__name__)
MAX_CLAIMS = int(os.getenv("MAX_CLAIMS", "5"))
EXTRACTION_MODEL = os.getenv("OPENAI_EXTRACTION_MODEL", "gpt-4o-mini")

EXTRACTION_PROMPT = f"""
You are a claim extraction specialist. Given a piece of text, extract the
{MAX_CLAIMS} most specific, independently verifiable factual claims.

Rules for extraction:
1. Only extract claims with concrete, checkable facts (names, dates, numbers, events)
2. Exclude opinions, predictions, and general statements
3. Exclude meta-commentary ("This is an interesting topic...")
4. Each claim must be self-contained and understandable without the original text
5. If fewer than 3 good claims exist, return only what is genuinely factual

Respond ONLY as valid JSON:
{{"claims": ["specific claim 1", "specific claim 2", "specific claim 3"]}}
"""


async def extract_claims(text: str) -> list[str]:
    """
    Extracts 1-5 factual claims from an answer.
    Always returns a list and falls back to the full answer when extraction fails.
    """
    try:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.warning("OPENAI_API_KEY not set - using the full answer as one fallback claim")
            return [text[:300]]

        client = AsyncOpenAI(api_key=api_key)
        response = await client.chat.completions.create(
            model=EXTRACTION_MODEL,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": EXTRACTION_PROMPT},
                {"role": "user", "content": f"Extract claims from:\n\n{text}"},
            ],
            max_tokens=400,
            temperature=0.1,
        )
        raw = json.loads(response.choices[0].message.content)
        claims = raw.get("claims", [])

        if not claims:
            logger.warning("Claim extractor returned no claims - using full text as fallback")
            return [text[:300]]

        logger.info(f"Extracted {len(claims)} claims with {EXTRACTION_MODEL}")
        return claims[:MAX_CLAIMS]
    except Exception as e:
        logger.error(f"Claim extraction failed: {e} - using fallback")
        return [text[:300]]


def validate_claims(claims: list[str]) -> list[str]:
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
