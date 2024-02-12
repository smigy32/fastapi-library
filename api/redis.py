from functools import wraps

import json
import redis


redis_connection = redis.Redis(host="redis", port=6379, db=1)


def cache_it(key_name: str):
    def Inner(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache = redis_connection.get(key_name)
            if cache:
                return json.loads(cache)
            else:
                result = func(*args, **kwargs)
                string_result = json.dumps(result)
                redis_connection.set(key_name, string_result)
                redis_connection.expire(key_name, 300)
                return result
        return wrapper
    return Inner


def drop_cache(key_name: str):
    def Inner(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache = redis_connection.get(key_name)
            if cache:
                redis_connection.delete(key_name)
            result = func(*args, **kwargs)
            return result
        return wrapper
    return Inner
