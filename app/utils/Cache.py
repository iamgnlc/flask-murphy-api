import hashlib
import json
import logging
import time
import redis

from app import CACHE_HOST, CACHE_PASSWORD, CACHE_PORT, CACHE_TTL, CACHE_ENABLED

logger = logging.getLogger(__name__)

PING_TTL = 5  # seconds between Redis ping checks


class Cache:
    def __init__(self):
        self.cache = redis.Redis(
            host=CACHE_HOST,
            port=CACHE_PORT,
            password=CACHE_PASSWORD,
        )
        self._ping_result = False
        self._ping_checked_at = 0

    @property
    def is_enabled(self):
        return bool(int(CACHE_ENABLED))

    @property
    def ping(self):
        now = time.monotonic()
        if now - self._ping_checked_at < PING_TTL:
            return self._ping_result
        try:
            self.cache.ping()
            self._ping_result = True
        except Exception as e:
            logger.error("Redis ping failed: %s", e)
            self._ping_result = False
        self._ping_checked_at = now
        return self._ping_result

    @property
    def flush(self):
        return self.cache.flushall()

    def update(self, laws, ttl: int = CACHE_TTL):
        if not laws:
            return

        pipe = self.cache.pipeline()
        for law in laws:
            serialized = json.dumps(law, sort_keys=True)
            key = "murphy:" + hashlib.md5(serialized.encode()).hexdigest()
            pipe.set(key, serialized, ex=ttl)

        try:
            pipe.execute()
        except redis.ConnectionError as e:
            logger.error("Redis pipeline failed: %s", e)
