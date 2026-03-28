# backend/services/intent_checker.py
import os
import json
import logging
import google.generativeai as genai

logger = logging.getLogger(__name__)
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

INTENT_PROMPT = """
You are an intent alignment evaluator. Determine whether the given
answer actually addresses the user's question.

Respond ONLY as valid JSON:
{
  "aligned": true or false,
  "alignment_score": 0-100,
  "reason": "Brief explanation if not aligned, null if aligned"
}
"""


async def check_intent_alignment(query: str, answer: str) -> dict:
    """
    Returns alignment score and whether the answer addresses the question.
    Always returns — never raises.
    """
    try:
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            system_instruction=INTENT_PROMPT
        )
        response = await model.generate_content_async(
            f"QUESTION: {query}\n\nANSWER: {answer[:800]}",
            generation_config=genai.GenerationConfig(
                temperature=0.1,
                max_output_tokens=150,
                response_mime_type="application/json",
            )
        )
        result = json.loads(response.text)
        logger.info(f"Intent alignment (Gemini): {result.get('alignment_score')} | aligned={result.get('aligned')}")
        return result
    except Exception as e:
        logger.warning(f"Intent check (Gemini) failed: {e}")
        return {"aligned": True, "alignment_score": 100, "reason": None}
