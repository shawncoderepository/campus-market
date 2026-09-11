import pytest
from tortoise import Tortoise

from application.common.config import DatabaseConfig
from application.core.database import build_tortoise_config


def test_build_mysql_tortoise_config() -> None:
    database = DatabaseConfig(
        backend="mysql",
        host="db.internal",
        port=3307,
        user="app_user",
        password="secret",
        name="app_database",
        minsize=2,
        maxsize=8,
    )
    connection = build_tortoise_config(database)["connections"]["default"]
    assert connection["engine"] == "tortoise.backends.mysql"
    assert connection["credentials"]["host"] == "db.internal"
    assert connection["credentials"]["port"] == 3307
    assert connection["credentials"]["database"] == "app_database"
    assert connection["credentials"]["minsize"] == 2
    assert connection["credentials"]["maxsize"] == 8
    assert "echo" not in connection["credentials"]


def test_build_sqlite_tortoise_config_keeps_memory_database() -> None:
    database = DatabaseConfig(backend="sqlite", sqlite_path=":memory:")
    connection = build_tortoise_config(database)["connections"]["default"]
    assert connection == {
        "engine": "tortoise.backends.sqlite",
        "credentials": {"file_path": ":memory:"},
    }


@pytest.mark.asyncio
async def test_tortoise_can_initialize_with_sqlite_config() -> None:
    database = DatabaseConfig(backend="sqlite", sqlite_path=":memory:")
    with pytest.warns(RuntimeWarning, match="has no models"):
        await Tortoise.init(config=build_tortoise_config(database))
    try:
        assert Tortoise.apps
    finally:
        await Tortoise.close_connections()
