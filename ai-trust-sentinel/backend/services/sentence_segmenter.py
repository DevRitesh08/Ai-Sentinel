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
    sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z"\'\(])', protected)

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
