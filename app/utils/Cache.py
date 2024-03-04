import json
import random
import re
import redis
import string

from datetime import datetime

from app import CACHE_HOST, CACHE_PASSWORD, CACHE_PORT, CACHE_TTL, CACHE_ENABLED


class Cache:
    def __init__(self):
        self.cache = redis.Redis(
            host=CACHE_HOST,
            port=CACHE_PORT,
            password=CACHE_PASSWORD,
        )

    @property
    def is_enabled(self):
        return bool(int(CACHE_ENABLED))

    @property
    def ping(self):
        try:
            self.cache.ping
            return True
        except Exception:
            return False

    @property
    def flush(self):
        return self.cache.flushall()

    def update(self, laws, ttl: int = CACHE_TTL):
        for law in laws:
            key = self.__get_key()
            try:
                self.cache.set(key, json.dumps(law), ex=ttl)
            except redis.ConnectionError:
                continue

    def __get_key(self):
        key = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")
        salt = "".join(random.choices(string.ascii_uppercase, k=6))
        return str(re.sub("[^0-9]", "", key)) + salt
