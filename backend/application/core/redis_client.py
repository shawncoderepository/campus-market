from __future__ import annotations

import json
from enum import StrEnum
from typing import Any

import redis.asyncio as redis
from redis.asyncio.lock import Lock
from redis.exceptions import ConnectionError, TimeoutError

from application.common.config import RedisConfig, config
from application.core.logger_util import logger


class TimeUnit(StrEnum):
    SECONDS = "seconds"
    MINUTES = "minutes"
    HOURS = "hours"
    DAYS = "days"

    def to_seconds(self, value: int) -> int:
        multiplier = {
            TimeUnit.SECONDS: 1,
            TimeUnit.MINUTES: 60,
            TimeUnit.HOURS: 3600,
            TimeUnit.DAYS: 86400,
        }
        return value * multiplier[self]


class AsyncRedisClient:
    """Lifecycle-managed Redis helper with JSON serialization and key namespacing."""

    def __init__(self, redis_config: RedisConfig) -> None:
        self.config = redis_config
        self._pool: redis.ConnectionPool | None = None
        self._client: redis.Redis | None = None

    @property
    def is_connected(self) -> bool:
        return self._client is not None

    @property
    def client(self) -> redis.Redis:
        if self._client is None:
            raise RuntimeError("Redis is not connected; enable it and use the application lifespan")
        return self._client

    def namespaced_key(self, key: str) -> str:
        prefix = self.config.key_prefix.strip(":")
        return f"{prefix}:{key}" if prefix else key

    async def connect(self) -> bool:
        if not self.config.enabled:
            logger.info("Redis is disabled")
            return False
        if self._client is not None:
            return True

        self._pool = redis.ConnectionPool(
            host=self.config.host,
            port=self.config.port,
            db=self.config.db,
            password=self.config.password or None,
            decode_responses=True,
            encoding="utf-8",
            max_connections=self.config.max_connections,
            socket_connect_timeout=self.config.socket_connect_timeout,
            socket_timeout=self.config.socket_timeout,
        )
        self._client = redis.Redis(connection_pool=self._pool)
        try:
            await self._client.ping()
        except (ConnectionError, TimeoutError) as exc:
            await self.close()
            if self.config.fail_fast:
                raise
            logger.warning("Redis connection failed; continuing without cache: %s", exc)
            return False
        logger.info("Redis connected")
        return True

    async def close(self) -> None:
        if self._client is not None:
            await self._client.aclose()
        if self._pool is not None:
            await self._pool.disconnect()
        self._client = None
        self._pool = None
        logger.info("Redis connections closed")

    @staticmethod
    def _serialize(value: Any) -> str | bytes | int | float:
        if isinstance(value, bytes | str | int | float):
            return value
        if isinstance(value, set):
            value = sorted(value, key=str)
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))

    @staticmethod
    def _deserialize(value: str | bytes | None) -> Any:
        if value is None:
            return None
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return value

    async def set(
        self,
        key: str,
        value: Any,
        time: int | None = None,
        unit: TimeUnit = TimeUnit.SECONDS,
    ) -> bool:
        expires_in = unit.to_seconds(time) if time is not None else None
        result = await self.client.set(
            self.namespaced_key(key), self._serialize(value), ex=expires_in
        )
        return bool(result)

    async def get(self, key: str) -> Any:
        value = await self.client.get(self.namespaced_key(key))
        return self._deserialize(value)

    async def delete(self, *keys: str) -> int:
        if not keys:
            return 0
        return int(await self.client.delete(*(self.namespaced_key(key) for key in keys)))

    async def incr(self, key: str, amount: int = 1) -> int:
        return int(await self.client.incrby(self.namespaced_key(key), amount))

    async def expire(self, key: str, time: int, unit: TimeUnit = TimeUnit.SECONDS) -> bool:
        return bool(await self.client.expire(self.namespaced_key(key), unit.to_seconds(time)))

    async def exists(self, key: str) -> bool:
        return bool(await self.client.exists(self.namespaced_key(key)))

    async def sadd(self, key: str, *values: str | int | float) -> int:
        return int(await self.client.sadd(self.namespaced_key(key), *values))

    async def srem(self, key: str, *values: str | int | float) -> int:
        return int(await self.client.srem(self.namespaced_key(key), *values))

    async def smembers(self, key: str) -> set[str]:
        return set(await self.client.smembers(self.namespaced_key(key)))

    async def sismember(self, key: str, value: str | int | float) -> bool:
        return bool(await self.client.sismember(self.namespaced_key(key), value))

    async def keys(self, pattern: str = "*") -> list[str]:
        """Return matching namespaced keys; prefer scan_iter for large keyspaces."""
        return list(await self.client.keys(self.namespaced_key(pattern)))

    async def scan_iter(self, pattern: str = "*", count: int = 100):
        async for key in self.client.scan_iter(match=self.namespaced_key(pattern), count=count):
            yield key

    def lock(
        self,
        key: str,
        expire: float = 10,
        blocking_timeout: float | None = None,
    ) -> Lock:
        """Create an async distributed lock usable with ``async with``."""
        return self.client.lock(
            self.namespaced_key(f"lock:{key}"),
            timeout=expire,
            blocking_timeout=blocking_timeout,
        )


redis_client = AsyncRedisClient(config.redis)
