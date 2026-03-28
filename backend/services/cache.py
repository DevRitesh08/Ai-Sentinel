import hashlib
import json
import logging
import os

import redis

logger = logging.getLogger(__name__)
CACHE_TTL = int(os.getenv("CACHE_TTL_SECONDS", "3600"))
REDIS_URL = os.getenv("REDIS_URL")

if REDIS_URL:
    try:
        r = redis.from_url(REDIS_URL, decode_responses=True)
        r.ping()
        logger.info("Redis connected successfully")
        REDIS_AVAILABLE = True
    except Exception as e:
        logger.warning(f"Redis unavailable ({e}) - caching disabled, pipeline will still work")
        REDIS_AVAILABLE = False
        r = None
else:
    logger.info("REDIS_URL not set - caching disabled")
    REDIS_AVAILABLE = False
    r = None


def make_cache_key(query: str) -> str:
    normalized = query.lower().strip()
    return "ats:query:" + hashlib.md5(normalized.encode()).hexdigest()


def get_cached(query: str) -> dict | None:
    if not REDIS_AVAILABLE:
        return None

    try:
        key = make_cache_key(query)
        data = r.get(key)
        if data:
            logger.info(f"Cache HIT for query: '{query[:40]}'")
            result = json.loads(data)
            result["from_cache"] = True
            return result

        logger.info(f"Cache MISS for query: '{query[:40]}'")
        return None
    except Exception as e:
        logger.warning(f"Cache read failed: {e} - continuing without cache")
        return None


def set_cached(query: str, result: dict) -> None:
    if not REDIS_AVAILABLE:
        return

    try:
        key = make_cache_key(query)
        data = json.dumps(result)
        r.setex(key, CACHE_TTL, data)
        logger.info(f"Cached query '{query[:40]}' for {CACHE_TTL}s")
    except Exception as e:
        logger.warning(f"Cache write failed: {e} - continuing without cache")


def get_cache_stats() -> dict:
    if not REDIS_AVAILABLE:
        return {"status": "disabled", "cached_queries": 0}

    try:
        keys = r.keys("ats:query:*")
        return {"status": "connected", "cached_queries": len(keys), "ttl_seconds": CACHE_TTL}
    except Exception:
        return {"status": "error", "cached_queries": 0}
