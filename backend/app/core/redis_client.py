import json
from typing import Any

import redis

from app.core.config import settings


redis_client = redis.Redis.from_url(settings.get_redis_url(), decode_responses=True)


def cache_get_json(key: str) -> Any | None:
    value = redis_client.get(key)
    if value is None:
        return None
    return json.loads(value)


def cache_set_json(key: str, payload: Any, ttl_seconds: int) -> None:
    redis_client.setex(key, ttl_seconds, json.dumps(payload))
