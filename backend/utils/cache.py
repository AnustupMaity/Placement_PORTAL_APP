#redis caching 
#llm help has been used here to generate the syntaxes and optimise the logic
import json
from functools import wraps
from typing import Any, Optional
from flask import request


def _get_redis():#livce redis connc..
    from extensions import redis_client
    return redis_client


def cache_get(key: str) -> Optional[Any]:#retrive info from catch
    client = _get_redis()
    try:
        if client is None:
            return None
        raw = client.get(key)
        if raw is None:
            return None
        return json.loads(raw)
    except Exception:
        return None


def cache_set(key: str, data: Any, expiry: int = 300) -> bool:#reset cache 5min interval
    client = _get_redis()
    try:
        if client is None:
            return False
        client.setex(key, expiry, json.dumps(data, default=str))
        return True
    except Exception:
        return False


def cache_delete(key: str) -> bool:#delete cache if data change

    client = _get_redis()
    try:
        if client is None:
            return False
        client.delete(key)
        return True
    except Exception:
        return False


def cache_delete_pattern(pattern: str) -> bool:#delete acc pattern
    client = _get_redis()
    try:
        if client is None:
            return False
        cursor = 0
        while True:
            cursor, keys = client.scan(cursor=cursor, match=pattern, count=100)
            if keys:
                client.delete(*keys)
            if cursor == 0:
                break
        return True
    except Exception:
        return False

def cached(key_prefix: str, expiry: int = 300):#decorator for caching
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            cache_key = f'{key_prefix}:{request.full_path}'
            hit = cache_get(cache_key)
            if hit is not None:
                return hit
            result = f(*args, **kwargs)
            if isinstance(result, (dict, list)):#cache stored in dict..full path
                cache_set(cache_key, result, expiry)

            return result
        return decorated
    return decorator
