# backend/services/cache.py
import os
import json
import hashlib
import logging
import redis

logger = logging.getLogger(__name__)
CACHE_TTL = int(os.getenv("CACHE_TTL_SECONDS", "3600"))

# Initialize Redis client — gracefully disabled if connection fails
# This means the full pipeline still works even without Redis
try:
    r = redis.from_url(os.getenv("REDIS_URL"), decode_responses=True)
    r.ping()  # Immediately test connection
    logger.info("Redis connected successfully")
    REDIS_AVAILABLE = True
except Exception as e:
    logger.warning(f"Redis unavailable ({e}) — caching disabled, pipeline will still work")
    REDIS_AVAILABLE = False
    r = None


def make_cache_key(query: str) -> str:
    """
    Generates a stable, normalized cache key for any query.
    Normalizes to lowercase + stripped to ensure case-insensitive cache hits.
    Prefix 'ats:query:' namespaces keys in Redis.
    """
    normalized = query.lower().strip()
    return "ats:query:" + hashlib.md5(normalized.encode()).hexdigest()


def get_cached(query: str) -> dict | None:
    """
    Returns the cached result dict for a query, or None if not found.
    Automatically adds from_cache=True to returned results.
    """
    if not REDIS_AVAILABLE:
        return None
    try:
        key  = make_cache_key(query)
        data = r.get(key)
        if data:
            logger.info(f"Cache HIT for query: '{query[:40]}'")
            result = json.loads(data)
            result["from_cache"] = True
            return result
        logger.info(f"Cache MISS for query: '{query[:40]}'")
        return None
    except Exception as e:
        logger.warning(f"Cache read failed: {e} — continuing without cache")
        return None


def set_cached(query: str, result: dict) -> None:
    """
    Stores a result dict in cache with TTL. Never raises.
    Call with result.model_dump() to convert Pydantic model to dict first.
    """
    if not REDIS_AVAILABLE:
        return
    try:
        key  = make_cache_key(query)
        data = json.dumps(result)
        r.setex(key, CACHE_TTL, data)
        logger.info(f"Cached query '{query[:40]}' for {CACHE_TTL}s")
    except Exception as e:
        logger.warning(f"Cache write failed: {e} — continuing without cache")


def get_cache_stats() -> dict:
    """Returns basic cache stats for the /cache/stats debug endpoint."""
    if not REDIS_AVAILABLE:
        return {"status": "disabled", "cached_queries": 0}
    try:
        keys = r.keys("ats:query:*")
        return {"status": "connected", "cached_queries": len(keys), "ttl_seconds": CACHE_TTL}
    except Exception:
        return {"status": "error", "cached_queries": 0}
