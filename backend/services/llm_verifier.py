import logging
import os

import google.generativeai as genai

logger = logging.getLogger(__name__)
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
VERIFIER_MODEL = os.getenv("GEMINI_VERIFIER_MODEL", "gemini-2.5-pro")

VERIFIER_SYSTEM = """
You are an independent factual verifier. Answer the question directly and
accurately. Be concise. Do not add caveats or disclaimers unless genuinely
important. Your answer will be compared against another AI's answer to
detect inconsistencies.
"""


async def call_verifier(query: str) -> dict:
    """
    Calls Gemini as an independent second-opinion verifier.
    Falls back to Ollama if Gemini fails.
    """
    try:
        model = genai.GenerativeModel(
            model_name=VERIFIER_MODEL,
            system_instruction=VERIFIER_SYSTEM,
        )
        response = await model.generate_content_async(
            query,
            generation_config=genai.GenerationConfig(
                temperature=0.3,
                max_output_tokens=600,
            ),
        )
        answer = response.text.strip()

        if not answer:
            logger.warning("Gemini returned empty response - falling back to Ollama")
            return await _call_ollama_fallback(query)

        logger.info(f"Verifier LLM ({VERIFIER_MODEL}) | answer_len={len(answer)}")
        return {"answer": answer}
    except Exception as e:
        logger.warning(f"Gemini failed ({e}) - attempting Ollama fallback")
        return await _call_ollama_fallback(query)


async def _call_ollama_fallback(query: str) -> dict:
    import httpx

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "llama3",
                    "prompt": query,
                    "stream": False,
                    "options": {"temperature": 0.3},
                },
            )
            data = response.json()
            answer = data["response"].strip()
            logger.info(f"Verifier LLM (Ollama fallback) | answer_len={len(answer)}")
            return {"answer": answer}
    except Exception as e:
        logger.error(f"Ollama fallback also failed: {e}")
        return {"answer": None}
