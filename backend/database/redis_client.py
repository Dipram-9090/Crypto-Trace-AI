"""Redis Client for Fast Cache, Session Storage, and Real-Time Event Pub/Sub."""

import os
import json
import logging
from typing import Any, Optional

logger = logging.getLogger("cryptotrace.backend.database.redis")


class RedisClientWrapper:
    """Handles high-throughput caching of risk scores and real-time transaction broadcast pub/sub."""

    def __init__(self, host: str = "localhost", port: int = 6379):
        self.redis_url = os.getenv("REDIS_URL", f"redis://{host}:{port}/0")
        self.client = None
        self._local_cache = {}
        self._connect()

    def _connect(self):
        try:
            import redis
            self.client = redis.from_url(self.redis_url, socket_timeout=2)
            self.client.ping()
            logger.info("Redis cache client connected.")
        except Exception:
            logger.debug("Redis not available; falling back to high-speed in-memory dict cache.")

    def get(self, key: str) -> Optional[Any]:
        if self.client:
            try:
                val = self.client.get(key)
                return json.loads(val) if val else None
            except Exception:
                pass
        return self._local_cache.get(key)

    def set(self, key: str, value: Any, ttl_seconds: int = 3600):
        if self.client:
            try:
                self.client.setex(key, ttl_seconds, json.dumps(value))
                return
            except Exception:
                pass
        self._local_cache[key] = value
