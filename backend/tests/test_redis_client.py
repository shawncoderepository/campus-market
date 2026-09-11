from unittest.mock import AsyncMock, Mock

import pytest

from application.common.config import RedisConfig
from application.core.redis_client import AsyncRedisClient, TimeUnit


@pytest.mark.asyncio
async def test_redis_client_serializes_json_and_prefixes_key() -> None:
    helper = AsyncRedisClient(RedisConfig(enabled=True, key_prefix="test_app"))
    client = Mock()
    client.set = AsyncMock(return_value=True)
    helper._client = client
    result = await helper.set(
        "widget:1",
        {"widget_id": 1, "widget_name": "demo"},
        time=2,
        unit=TimeUnit.MINUTES,
    )
    assert result is True
    client.set.assert_awaited_once_with(
        "test_app:widget:1", '{"widget_id":1,"widget_name":"demo"}', ex=120
    )


@pytest.mark.asyncio
async def test_redis_client_deserializes_json() -> None:
    helper = AsyncRedisClient(RedisConfig(enabled=True, key_prefix="test_app"))
    client = Mock()
    client.get = AsyncMock(return_value='{"widget_id":1}')
    helper._client = client
    assert await helper.get("widget:1") == {"widget_id": 1}
    client.get.assert_awaited_once_with("test_app:widget:1")


@pytest.mark.asyncio
async def test_redis_client_requires_connection() -> None:
    helper = AsyncRedisClient(RedisConfig(enabled=False))
    with pytest.raises(RuntimeError, match="Redis is not connected"):
        await helper.get("missing")


def test_time_unit_conversion() -> None:
    assert TimeUnit.MINUTES.to_seconds(2) == 120
    assert TimeUnit.HOURS.to_seconds(2) == 7200
