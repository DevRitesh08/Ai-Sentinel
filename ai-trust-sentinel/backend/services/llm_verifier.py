# backend/services/llm_verifier.py
import os
import logging
import google.generativeai as genai

logger = logging.getLogger(__name__)
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

VERIFIER_SYSTEM = """
You are an independent factual verifier. Answer the question directly and
accurately. Be concise. Do not add caveats or disclaimers unless genuinely
important. Your answer will be compared against another AI's answer to
detect inconsistencies.
"""


async def call_verifier(query: str) -> dict:
    """
    Calls Gemini Flash as an independent second-opinion verifier.
    Returns: {"answer": str}
    Falls back to Ollama (local) if Gemini fails.
    """
    try:
        model = genai.GenerativeModel(
            model_name="gemini-2.5-pro",
            system_instruction=VERIFIER_SYSTEM
        )
        response = model.generate_content(
            query,
            generation_config=genai.GenerationConfig(
                temperature=0.3,
                max_output_tokens=600,
            )
        )
        answer = response.text.strip()

        if not answer:
            logger.warning("Gemini returned empty response — falling back to Ollama")
            return await _call_ollama_fallback(query)

        logger.info(f"Verifier LLM (Gemini) | answer_len={len(answer)}")
        return {"answer": answer}

    except Exception as e:
        logger.warning(f"Gemini failed ({e}) — attempting Ollama fallback")
        return await _call_ollama_fallback(query)


async def _call_ollama_fallback(query: str) -> dict:
    """
    Local Llama 3 via Ollama — zero API cost, works offline.
    Requires: ollama pull llama3 (run once before using)
    Note: Download ~4.7GB — do NOT try on slow WiFi.
    """
    import httpx
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "llama3",
                    "prompt": query,
                    "stream": False,
                    "options": {"temperature": 0.3}
                }
            )
            data = response.json()
            answer = data["response"].strip()
            logger.info(f"Verifier LLM (Ollama fallback) | answer_len={len(answer)}")
            return {"answer": answer}
    except Exception as e:
        logger.error(f"Ollama fallback also failed: {e}")
        # Graceful degradation — pipeline continues without verifier
        return {"answer": None}
