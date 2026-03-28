# backend/routers/verify.py
import re
import html
import logging
import json
import time
import asyncio
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from models.schemas import VerifyRequest, VerifyResponse
from services.pipeline import run_verification_pipeline
from services.cache import get_cached, get_cache_stats

logger = logging.getLogger(__name__)
router = APIRouter()


def sanitize_query(query: str) -> str:
    """
    Sanitizes query input before processing.
    - Strips leading/trailing whitespace
    - Removes HTML tags (XSS prevention)
    - Normalizes internal whitespace
    - Truncates at MAX_LENGTH
    """
    MAX_LENGTH = 2000

    # Strip whitespace
    query = query.strip()

    # Remove HTML tags
    query = re.sub(r'<[^>]+>', '', query)

    # Decode HTML entities
    query = html.unescape(query)

    # Normalize whitespace
    query = re.sub(r'\s+', ' ', query)

    # Truncate
    if len(query) > MAX_LENGTH:
        query = query[:MAX_LENGTH]

    return query


@router.post("/verify", response_model=VerifyResponse)
async def verify_query(payload: VerifyRequest):
    """
    Main verification endpoint with input sanitization.
    """
    query = sanitize_query(payload.query)

    if len(query) < 2:
        raise HTTPException(status_code=400, detail="Query too short (minimum 2 characters)")

    if len(query) > 2000:
        raise HTTPException(status_code=400, detail="Query too long (maximum 2000 characters)")

    # Check for purely non-semantic input
    meaningful_chars = re.sub(r'[^a-zA-Z0-9\u3000-\u9fff\u4e00-\u9fff]', '', query)
    if len(meaningful_chars) < 2:
        raise HTTPException(status_code=400, detail="Query must contain meaningful text")

    logger.info(f"Verifying: '{query[:60]}'")
    return await run_verification_pipeline(query)


@router.post("/verify/stream")
async def verify_stream(payload: VerifyRequest):
    """
    Server-Sent Events streaming endpoint.
    Emits pipeline stage events as they complete, then the final result.
    """
    query = sanitize_query(payload.query)

    if len(query) < 2:
        raise HTTPException(status_code=400, detail="Query too short")

    async def event_generator():
        try:
            yield f"event: start\ndata: {json.dumps({'stage': 'started', 'query': query})}\n\n"
            await asyncio.sleep(0)

            # Stage 1: Cache check
            cached = get_cached(query)
            if cached:
                yield f"event: cache_hit\ndata: {json.dumps({'from_cache': True})}\n\n"
                yield f"event: complete\ndata: {json.dumps(cached)}\n\n"
                return

            yield f"event: stage\ndata: {json.dumps({'stage': 'calling_primary_llm'})}\n\n"

            # Run the full pipeline
            result = await run_verification_pipeline(query)
            result_dict = result.model_dump()

            yield f"event: complete\ndata: {json.dumps(result_dict)}\n\n"

        except Exception as e:
            logger.error(f"Streaming error: {e}")
            yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        }
    )


@router.get("/cache/stats")
async def cache_stats():
    """Debug endpoint — shows Redis connection status and cached entry count."""
    return get_cache_stats()
