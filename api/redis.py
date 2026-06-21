from functools import wraps
import json

from redis import asyncio as aioredis


redis_connection = aioredis.Redis(host="redis", port=6379, db=1)


def cache_it(key_name: str):
    def Inner(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache = await redis_connection.get(key_name)
            if cache:
                return json.loads(cache)
            result = await func(*args, **kwargs)
            await redis_connection.set(key_name, json.dumps(result))
            await redis_connection.expire(key_name, 300)
            return result
        return wrapper
    return Inner


def drop_cache(key_name: str):
    def Inner(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache = await redis_connection.get(key_name)
            if cache:
                await redis_connection.delete(key_name)
            return await func(*args, **kwargs)
        return wrapper
    return Inner
