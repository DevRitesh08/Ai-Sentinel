import asyncio
import logging
import os

import redis
from fastapi import APIRouter

logger = logging.getLogger(__name__)
router = APIRouter()
PRIMARY_MODEL = os.getenv("GEMINI_PRIMARY_MODEL", "gemini-2.5-flash")


def has_real_value(name: str) -> bool:
    value = os.getenv(name)
    return bool(value and "YOUR_KEY_HERE" not in value)


@router.get("/health")
async def basic_health():
    return {"status": "ok", "version": "1.0.0"}


@router.get("/health/full")
async def full_health_check():
    results = {}

    redis_url = os.getenv("REDIS_URL")
    if redis_url:
        try:
            client = redis.from_url(redis_url, socket_timeout=2)
            client.ping()
            results["redis"] = {"status": "ok"}
        except Exception as e:
            results["redis"] = {"status": "error", "message": str(e)}
    else:
        results["redis"] = {"status": "disabled", "message": "No REDIS_URL provided"}

    try:
        from openai import AsyncOpenAI

        if has_real_value("OPENAI_API_KEY"):
            client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            await asyncio.wait_for(
                client.chat.completions.create(
                    model=os.getenv("OPENAI_EXTRACTION_MODEL", "gpt-4o-mini"),
                    messages=[{"role": "user", "content": "ping"}],
                    max_tokens=3,
                ),
                timeout=5.0,
            )
            results["openai"] = {"status": "ok"}
        else:
            results["openai"] = {"status": "disabled", "message": "No OPENAI_API_KEY provided"}
    except Exception as e:
        results["openai"] = {"status": "error", "message": str(e)}

    try:
        if has_real_value("GEMINI_API_KEY"):
            import google.generativeai as genai

            genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
            model = genai.GenerativeModel(PRIMARY_MODEL)
            model.generate_content("ping", generation_config={"max_output_tokens": 3})
            results["gemini"] = {"status": "ok", "model": PRIMARY_MODEL}
        else:
            results["gemini"] = {"status": "disabled", "message": "No GEMINI_API_KEY provided"}
    except Exception as e:
        results["gemini"] = {"status": "error", "message": str(e)}

    try:
        if has_real_value("TAVILY_API_KEY"):
            from tavily import TavilyClient

            client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
            client.search("test", max_results=1)
            results["tavily"] = {"status": "ok"}
        else:
            results["tavily"] = {"status": "disabled", "message": "No TAVILY_API_KEY provided"}
    except Exception as e:
        results["tavily"] = {"status": "error", "message": str(e)}

    try:
        import httpx

        async with httpx.AsyncClient(timeout=2) as client:
            response = await client.get("http://localhost:11434/api/tags")
            results["ollama"] = {
                "status": "ok",
                "models": [model["name"] for model in response.json().get("models", [])],
            }
    except Exception:
        results["ollama"] = {"status": "offline", "message": "Local fallback unavailable"}

    all_critical_ok = all(
        results.get(name, {}).get("status") in ["ok", "disabled"]
        for name in ["redis", "gemini", "tavily"]
    )

    return {
        "overall": "healthy" if all_critical_ok else "degraded",
        "services": results,
    }
