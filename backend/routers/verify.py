import asyncio
import html
import json
import logging
import re

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from models.schemas import ConversationTurn, VerifyRequest, VerifyResponse
from services.cache import get_cached, get_cache_stats
from services.context_resolver import MAX_CONTEXT_TURNS, resolve_query
from services.pipeline import run_verification_pipeline

logger = logging.getLogger(__name__)
router = APIRouter()


def sanitize_query(query: str) -> str:
    max_length = 2000
    query = query.strip()
    query = re.sub(r"<[^>]+>", "", query)
    query = html.unescape(query)
    query = re.sub(r"\s+", " ", query)
    if len(query) > max_length:
        query = query[:max_length]
    return query


def sanitize_history(history: list[ConversationTurn]) -> list[ConversationTurn]:
    cleaned = []
    for turn in history[-MAX_CONTEXT_TURNS:]:
        content = sanitize_query(turn.content)
        if len(content) < 2:
            continue
        cleaned.append(ConversationTurn(role=turn.role, content=content))
    return cleaned


def validate_meaningful_query(query: str) -> None:
    if len(query) < 2:
        raise HTTPException(status_code=400, detail="Query too short (minimum 2 characters)")

    if len(query) > 2000:
        raise HTTPException(status_code=400, detail="Query too long (maximum 2000 characters)")

    meaningful_chars = re.sub(r"[^a-zA-Z0-9\u3000-\u9fff\u4e00-\u9fff]", "", query)
    if len(meaningful_chars) < 2:
        raise HTTPException(status_code=400, detail="Query must contain meaningful text")


@router.post("/verify", response_model=VerifyResponse)
async def verify_query(payload: VerifyRequest):
    query = sanitize_query(payload.query)
    validate_meaningful_query(query)
    history = sanitize_history(payload.history)

    logger.info(f"Verifying: '{query[:60]}'")
    return await run_verification_pipeline(query, history=history)


@router.post("/verify/stream")
async def verify_stream(payload: VerifyRequest):
    query = sanitize_query(payload.query)
    validate_meaningful_query(query)
    history = sanitize_history(payload.history)

    async def event_generator():
        try:
            resolution = await resolve_query(query, history)
            resolved_query = resolution.resolved_query

            yield f"event: start\ndata: {json.dumps({'stage': 'started', 'query': query, 'resolved_query': resolved_query, 'used_context': resolution.used_context})}\n\n"
            await asyncio.sleep(0)

            cached = get_cached(resolved_query)
            if cached:
                cached["resolved_query"] = resolved_query
                cached["used_context"] = resolution.used_context
                cached["context_turns_used"] = resolution.context_turns_used
                yield f"event: cache_hit\ndata: {json.dumps({'from_cache': True})}\n\n"
                yield f"event: complete\ndata: {json.dumps(cached)}\n\n"
                return

            yield f"event: stage\ndata: {json.dumps({'stage': 'calling_primary_llm'})}\n\n"

            result = await run_verification_pipeline(query, history=history)
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
        },
    )


@router.get("/cache/stats")
async def cache_stats():
    return get_cache_stats()
