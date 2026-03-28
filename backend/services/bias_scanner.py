# backend/services/bias_scanner.py
import os
import json
import logging
import google.generativeai as genai

logger = logging.getLogger(__name__)
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

BIAS_SCAN_PROMPT = """
You are an objective content safety and bias analyzer.
Analyze the given text for the following signals:

1. BIAS INDICATORS: Strong political, cultural, or ideological slant
   that presents one perspective as fact
2. UNVERIFIED STATISTICS: Numbers presented without source attribution
3. LOADED LANGUAGE: Emotionally charged terms that influence perception
4. OVERGENERALIZATION: "Always", "never", "all X people", etc.
5. RECENCY ISSUES: References to events that may be outdated

Respond ONLY as valid JSON:
{
  "bias_score": 0-100,
  "toxicity_score": 0-100,
  "flags": [
    {
      "type": "BIAS|TOXICITY|STATISTICS|LANGUAGE|GENERALIZATION",
      "text": "the flagged phrase",
      "reason": "why this is flagged"
    }
  ],
  "summary": "One-sentence overall assessment"
}

Return {"bias_score": 0, "toxicity_score": 0, "flags": [], "summary": "No issues detected"}
if no concerns are found.
"""

CLEAN_RESULT = {
    "bias_score": 0,
    "toxicity_score": 0,
    "flags": [],
    "summary": "Scan unavailable"
}


async def scan_response(text: str) -> dict:
    """
    Scans AI response text for bias, toxicity, and content issues.
    Always returns — never raises.
    """
    try:
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            system_instruction=BIAS_SCAN_PROMPT
        )
        response = await model.generate_content_async(
            f"Analyze:\n\n{text[:1500]}",
            generation_config=genai.GenerationConfig(
                temperature=0.1,
                max_output_tokens=400,
                response_mime_type="application/json",
            )
        )
        result = json.loads(response.text)
        logger.info(
            f"Bias scan (Gemini) | bias={result.get('bias_score')} "
            f"| toxicity={result.get('toxicity_score')} "
            f"| flags={len(result.get('flags', []))}"
        )
        return result

    except Exception as e:
        logger.warning(f"Bias scanner (Gemini) failed: {e} — returning clean result")
        return CLEAN_RESULT
