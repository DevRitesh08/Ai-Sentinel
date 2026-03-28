# backend/services/prompt_calibration.py
# Run this to calibrate confidence scoring. Helps tune the system prompt.
#
# Usage (from backend/ with venv active):
#   python -m services.prompt_calibration
#
# Expected output: all rows show ✓ (correct calibration)
# If rows show ✗ RECALIBRATE, adjust the system prompt in llm_primary.py.

import asyncio
import os
from dotenv import load_dotenv
load_dotenv()

from services.llm_primary import call_primary

# Test queries categorized by expected confidence range
TEST_QUERIES = [
    # Expected HIGH confidence (≥ 85) — mathematical facts, well-documented science
    ("What is 2 + 2?",                                    "MATH",       85),
    ("What element has atomic number 8?",                 "SCIENCE",    85),
    ("Who wrote Romeo and Juliet?",                       "LITERATURE", 85),

    # Expected MEDIUM confidence (50–84) — history, complex science topics
    ("What are the main causes of World War I?",          "HISTORY",    50),
    ("How does photosynthesis work?",                     "SCIENCE",    50),

    # Expected LOW confidence (< 60) — obscure, future, impossible to know
    ("What was the exact GDP of the Roman Empire?",       "OBSCURE",    None),
    ("What will the stock market do next week?",          "FUTURE",     None),
    ("What is the population of every city in India?",   "IMPOSSIBLE", None),
]

# Thresholds used for pass/fail judgment
HIGH_MIN   = 85
MEDIUM_MIN = 50
LOW_MAX    = 60


async def calibrate():
    print("\n" + "=" * 90)
    print("  AI Trust Sentinel — Confidence Calibration Test")
    print("=" * 90)
    print(f"\n{'Query':<55} {'Type':<12} {'Score':<8} {'Status'}")
    print("-" * 90)

    passed = 0
    failed = 0

    for query, qtype, min_expected in TEST_QUERIES:
        try:
            result = await call_primary(query)
            score = result["confidence"]

            if qtype in ["MATH", "SCIENCE", "LITERATURE"] and score >= HIGH_MIN:
                status = "✓ CORRECT"
                passed += 1
            elif qtype in ["HISTORY"] and score >= MEDIUM_MIN:
                status = "✓ CORRECT"
                passed += 1
            elif qtype in ["OBSCURE", "FUTURE", "IMPOSSIBLE"] and score < LOW_MAX:
                status = "✓ CORRECT"
                passed += 1
            else:
                status = "✗ RECALIBRATE"
                failed += 1

            print(f"{query[:53]:<55} {qtype:<12} {score:<8} {status}")
        except Exception as e:
            print(f"{query[:53]:<55} {qtype:<12} {'ERROR':<8} ✗ {e}")
            failed += 1

    print("\n" + "=" * 90)
    print(f"  Results: {passed} passed, {failed} failed")
    if failed == 0:
        print("  ✓ Confidence scoring well calibrated!")
    else:
        print("\n  Calibration tips:")
        print("  - All scores clustering at 95–100 → add 'Reserve 90+ for absolute certainties only'")
        print("  - All scores clustering at 50–60 → add 'Well-known facts should score 80–90'")
        print("  - Scores inconsistent → lower temperature to 0.1 in llm_primary.py")
    print("=" * 90 + "\n")


if __name__ == "__main__":
    asyncio.run(calibrate())
