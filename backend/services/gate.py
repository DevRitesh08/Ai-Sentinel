# backend/services/gate.py
import os
import logging
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)
THRESHOLD = int(os.getenv("CONFIDENCE_THRESHOLD", "75"))


def should_escalate(confidence: int) -> bool:
    """
    Returns True if the primary model's confidence warrants a second opinion
    from the Gemini verifier.

    Logic: if confidence < threshold → escalate to Gemini
           if confidence >= threshold → skip Gemini (gate=SKIP)
    """
    decision = confidence < THRESHOLD
    gate_state = "ESCALATE" if decision else "SKIP"
    logger.info(f"Gate decision: confidence={confidence}, threshold={THRESHOLD}, gate={gate_state}")
    return decision


def calculate_consistency_score(answer_a: str, answer_b: str) -> float:
    """
    Returns a 0.0–1.0 similarity score between two answers.

    High score (≥ 0.8) = HIGH_AGREEMENT   → models agree → lower hallucination risk
    Medium score (0.5–0.8) = PARTIAL_AGREEMENT
    Low score (< 0.5) = SIGNIFICANT_DIVERGENCE → models disagree → higher risk

    Note: Uses sequence matching as a baseline heuristic.
    For production quality: replace with cosine similarity on embeddings.
    """
    # Normalize both answers before comparison
    a = answer_a.lower().strip()
    b = answer_b.lower().strip()

    ratio = SequenceMatcher(None, a, b).ratio()
    logger.info(f"Consistency score: {ratio:.3f} | {interpret_consistency(ratio)}")
    return ratio


def interpret_consistency(score: float) -> str:
    """Human-readable interpretation of the consistency score."""
    if score >= 0.8: return "HIGH_AGREEMENT"
    if score >= 0.5: return "PARTIAL_AGREEMENT"
    return "SIGNIFICANT_DIVERGENCE"
