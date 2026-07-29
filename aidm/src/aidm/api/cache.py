"""Optional Redis-based API response cache with graceful degradation."""
import os
import json
import hashlib
from typing import Optional

_redis_client = None
_cache_enabled = False


def init_cache():
    """Initialize Redis cache if available. Fails silently if Redis is not configured."""
    global _redis_client, _cache_enabled
    redis_url = os.getenv("REDIS_URL", "")
    if not redis_url:
        return
    try:
        import redis
        _redis_client = redis.from_url(redis_url, decode_responses=True)
        _redis_client.ping()
        _cache_enabled = True
    except Exception:
        _redis_client = None
        _cache_enabled = False


def get_cached(key: str) -> Optional[str]:
    """Get cached value by key. Returns None if cache miss or cache disabled."""
    if not _cache_enabled or not _redis_client:
        return None
    try:
        return _redis_client.get(key)
    except Exception:
        return None


def set_cached(key: str, value: str, ttl: int = 60):
    """Cache a value with TTL in seconds. No-op if cache disabled."""
    if not _cache_enabled or not _redis_client:
        return
    try:
        _redis_client.setex(key, ttl, value)
    except Exception:
        pass


def make_cache_key(prefix: str, **kwargs) -> str:
    """Generate a cache key from prefix and kwargs."""
    raw = json.dumps(kwargs, sort_keys=True, default=str)
    return f"{prefix}:{hashlib.md5(raw.encode()).hexdigest()}"


def is_cache_enabled() -> bool:
    return _cache_enabled
