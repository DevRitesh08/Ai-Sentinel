# backend/services/trust_score.py
import logging
from models.schemas import ClaimResult, ClaimStatus

logger = logging.getLogger(__name__)

# Signal weights — must sum to 1.0
WEIGHT_CONFIDENCE  = 0.30   # Primary LLM self-assessment (30%)
WEIGHT_CONSISTENCY = 0.25   # LLM-to-LLM agreement — only when gate triggered (25%)
WEIGHT_FACT_CHECK  = 0.45   # Web source verification — most reliable signal (45%)

# Per-claim scoring adjustments
PENALTY_CONTRADICTED = 15   # Deducted per CONTRADICTED claim
PENALTY_UNCERTAIN    = 5    # Deducted per UNCERTAIN claim
BONUS_VERIFIED       = 3    # Added per VERIFIED claim (small reward for all-green claims)


def calculate_trust_score(
    primary_confidence: int,
    consistency_score:  float,          # 0.0–1.0, or None if gate was skipped
    fact_results:       list[ClaimResult],
    verifier_used:      bool
) -> int:
    """
    Aggregates all pipeline signals into a single Trust Score (0–100).

    Signals:
    1. Primary LLM self-confidence (30%) — how sure was the model?
    2. LLM-to-LLM consistency (25%) — do GPT and Gemini agree? (only when gate fires)
    3. Fact-check results (45%) — what does the live web say?

    Returns: int clamped to 0–100
    """
    score = 100.0
    breakdown = {}

    # ── Signal 1: Primary model confidence ───────────────────────────────────
    confidence_deduction = (100 - primary_confidence) * WEIGHT_CONFIDENCE
    score -= confidence_deduction
    breakdown["confidence_deduction"] = round(confidence_deduction, 1)

    # ── Signal 2: LLM consistency (only when verifier was triggered) ──────────
    if verifier_used and consistency_score is not None:
        consistency_deduction = (1.0 - consistency_score) * (100 * WEIGHT_CONSISTENCY)
        score -= consistency_deduction
        breakdown["consistency_deduction"] = round(consistency_deduction, 1)
    else:
        # Gate was skipped (high confidence) — no consistency penalty applied
        breakdown["consistency_deduction"] = 0

    # ── Signal 3: Fact-check results ─────────────────────────────────────────
    fact_deduction = 0
    fact_bonus     = 0

    for result in fact_results:
        if result.status == ClaimStatus.CONTRADICTED:
            fact_deduction += PENALTY_CONTRADICTED
        elif result.status == ClaimStatus.UNCERTAIN:
            fact_deduction += PENALTY_UNCERTAIN
        elif result.status == ClaimStatus.VERIFIED:
            fact_bonus += BONUS_VERIFIED

    score -= fact_deduction
    score += fact_bonus
    breakdown["fact_check_deduction"] = fact_deduction
    breakdown["fact_check_bonus"]     = fact_bonus

    # ── Clamp and finalize ────────────────────────────────────────────────────
    final_score = max(0, min(100, int(score)))
    breakdown["final_score"] = final_score

    logger.info(f"Trust Score breakdown: {breakdown}")
    return final_score


def score_to_label(score: int) -> str:
    """Human-readable label for the trust score."""
    if score >= 85: return "HIGH CONFIDENCE"
    if score >= 65: return "MODERATE CONFIDENCE"
    if score >= 45: return "LOW CONFIDENCE"
    return "UNRELIABLE — VERIFY MANUALLY"


def score_to_color(score: int) -> str:
    """
    Hex color for the frontend to use when rendering the score badge.
    Green → Yellow → Orange → Red as trust decreases.
    """
    if score >= 85: return "#00FF9D"   # Green
    if score >= 65: return "#FFD166"   # Yellow
    if score >= 45: return "#FF9A3C"   # Orange
    return "#FF4F6A"                   # Red
