# backend/services/llm_primary.py
import os
import json
import logging
import google.generativeai as genai

logger = logging.getLogger(__name__)
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

SYSTEM_PROMPT = """
You are a precise factual assistant. Your job is to answer questions
accurately AND provide an honest self-assessment of your confidence.

Respond ONLY as valid JSON with this exact structure:
{
  "answer": "Your complete, well-reasoned answer here",
  "confidence": 82,
  "reasoning": "Brief explanation of your confidence level"
}

Confidence scoring rules:
- 90–100: Mathematical facts, universal scientific laws, verified historical events
- 75–89:  Well-documented facts with broad consensus
- 50–74:  Partial knowledge, some uncertainty, topic may have conflicting info
- 25–49:  Limited knowledge, significant uncertainty
- 0–24:   Largely unknown to you — say so clearly in the answer

CRITICAL: Be genuinely honest about uncertainty. Overconfident wrong answers
are worse than honest uncertainty. Never score above 75 for niche topics,
recent events, or anything you are not fully certain about.
Most topics should score 60–80. Reserve 90+ for absolute certainties only.
Confidence reflects your certainty about factual accuracy, NOT your
completeness or answer length.
"""


async def call_primary(query: str) -> dict:
    """
    Calls Gemini Flash with JSON mode enforced.
    Returns: {"answer": str, "confidence": int, "reasoning": str}
    Raises:  RuntimeError on API failure
    """
    try:
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            system_instruction=SYSTEM_PROMPT
        )
        response = await model.generate_content_async(
            query,
            generation_config=genai.GenerationConfig(
                temperature=0.3,
                max_output_tokens=800,
                response_mime_type="application/json",
            )
        )
        raw = response.text
        result = json.loads(raw)

        # Validate required fields
        assert "answer"     in result, "Missing 'answer' field"
        assert "confidence" in result, "Missing 'confidence' field"
        assert 0 <= result["confidence"] <= 100, f"Confidence out of range: {result['confidence']}"

        logger.info(f"Primary LLM (Gemini) | confidence={result['confidence']} | query_len={len(query)}")
        return result

    except json.JSONDecodeError as e:
        logger.error(f"Primary LLM JSON parse error: {e}")
        raise RuntimeError("Primary LLM returned malformed JSON")
    except AssertionError as e:
        logger.error(f"Primary LLM response validation failed: {e}")
        raise RuntimeError(f"Primary LLM response invalid: {str(e)}")
    except Exception as e:
        logger.error(f"Primary LLM API error: {e}")
        raise RuntimeError(f"Primary LLM failed: {str(e)}")
