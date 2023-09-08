import json
import redis
import re
import random
import string

from datetime import datetime

from app import CACHE_HOST, CACHE_PASSWORD, CACHE_PORT, CACHE_TTL

cache = redis.Redis(
    host=CACHE_HOST,
    port=CACHE_PORT,
    password=CACHE_PASSWORD,
)


def get_key():
    key = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")
    salt = "".join(random.choices(string.ascii_uppercase, k=6))
    return str(re.sub("[^0-9]", "", key)) + salt


def update_cache(laws, ttl=int(CACHE_TTL)):
    for law in laws:
        key = get_key()
        try:
            cache.set(key, json.dumps(law), ex=ttl)
        except redis.ConnectionError:
            continue
