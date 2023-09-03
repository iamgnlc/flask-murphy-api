import json
import redis
import hashlib

from app import CACHE_HOST, CACHE_PASSWORD, CACHE_PORT, CACHE_TTL

cache = redis.Redis(
    host=CACHE_HOST,
    port=CACHE_PORT,
    password=CACHE_PASSWORD,
)


def set_key(text):
    key = hashlib.sha256(str(text).encode("UTF-8"))
    return key.hexdigest()


def update_cache(laws):
    for law in laws:
        key = set_key(law)
        cache.set(key, json.dumps(law), ex=int(CACHE_TTL))
