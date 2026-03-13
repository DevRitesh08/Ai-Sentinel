# backend/routers/health.py — comprehensive health endpoint
from fastapi import APIRouter
import asyncio
import redis
import os
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/health")
async def basic_health():
    """Quick health check — used by Railway for liveness probe."""
    return {"status": "ok", "version": "1.0.0"}


@router.get("/health/full")
async def full_health_check():
    """
    Checks all external dependencies and returns their status.
    Use this to verify production environment before demo.
    """
    results = {}

    # 1. Redis
    try:
        r = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"), socket_timeout=2)
        r.ping()
        results["redis"] = {"status": "ok"}
    except Exception as e:
        results["redis"] = {"status": "error", "message": str(e)}

    # 2. OpenAI (Optional)
    try:
        from openai import AsyncOpenAI
        if os.getenv("OPENAI_API_KEY") and not os.getenv("OPENAI_API_KEY").startswith("sk-your"):
            client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            await asyncio.wait_for(
                client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": "ping"}],
                    max_tokens=3
                ),
                timeout=5.0
            )
            results["openai"] = {"status": "ok"}
        else:
            results["openai"] = {"status": "disabled", "message": "No OPENAI_API_KEY provided"}
    except Exception as e:
        results["openai"] = {"status": "error", "message": str(e)}

    # 3. Gemini
    try:
        import google.generativeai as genai
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        model = genai.GenerativeModel("gemini-2.5-flash")
        model.generate_content("ping", generation_config={"max_output_tokens": 3})
        results["gemini"] = {"status": "ok"}
    except Exception as e:
        results["gemini"] = {"status": "error", "message": str(e)}

    # 4. Tavily
    try:
        from tavily import TavilyClient
        tc = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
        tc.search("test", max_results=1)
        results["tavily"] = {"status": "ok"}
    except Exception as e:
        results["tavily"] = {"status": "error", "message": str(e)}

    # 5. Ollama (local fallback)
    try:
        import httpx
        async with httpx.AsyncClient(timeout=2) as client:
            r = await client.get("http://localhost:11434/api/tags")
            results["ollama"] = {"status": "ok", "models": [m["name"] for m in r.json().get("models", [])]}
    except Exception:
        results["ollama"] = {"status": "offline", "message": "Local fallback unavailable"}

    all_critical_ok = all(
        results.get(k, {}).get("status") in ["ok", "disabled"]
        for k in ["redis", "gemini", "tavily"]
    )

    return {
        "overall": "healthy" if all_critical_ok else "degraded",
        "services": results
    }
