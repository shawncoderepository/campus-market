import logging
from pathlib import Path
from typing import Any

from tortoise import Tortoise

from application.common.config import DatabaseConfig, config
from application.core.logger_util import logger

_database_connected = False


def build_tortoise_config(database: DatabaseConfig) -> dict[str, Any]:
    if database.backend == "sqlite":
        sqlite_path = Path(database.sqlite_path)
        if not sqlite_path.is_absolute() and database.sqlite_path != ":memory:":
            root_dir = Path(__file__).resolve().parents[2]
            sqlite_path = root_dir / sqlite_path
        connection: str | dict[str, Any] = {
            "engine": "tortoise.backends.sqlite",
            "credentials": {"file_path": str(sqlite_path)},
        }
    else:
        connection = {
            "engine": "tortoise.backends.mysql",
            "credentials": {
                "host": database.host,
                "port": database.port,
                "user": database.user,
                "password": database.password,
                "database": database.name,
                "charset": database.charset,
                "minsize": database.minsize,
                "maxsize": database.maxsize,
            },
        }

    return {
        "connections": {"default": connection},
        "apps": {
            "models": {
                "models": ["application.common.models"],
                "default_connection": "default",
            }
        },
        "use_tz": database.use_tz,
        "timezone": database.timezone,
    }


TORTOISE_ORM = build_tortoise_config(config.database)


async def connect_database() -> bool:
    global _database_connected
    if not config.database.enabled:
        logger.info("Tortoise ORM is disabled")
        return False

    if config.database.backend == "sqlite" and config.database.sqlite_path != ":memory:":
        sqlite_path = Path(config.database.sqlite_path)
        if not sqlite_path.is_absolute():
            sqlite_path = Path(__file__).resolve().parents[2] / sqlite_path
        sqlite_path.parent.mkdir(parents=True, exist_ok=True)

    if config.database.echo:
        logging.getLogger("tortoise.db_client").setLevel(logging.DEBUG)
    await Tortoise.init(config=TORTOISE_ORM)
    _database_connected = True
    if config.database.auto_generate_schema:
        await Tortoise.generate_schemas(safe=True)
        logger.warning("Database schema auto-generation is enabled; use migrations in production")
    logger.info("Tortoise ORM connected using %s backend", config.database.backend)
    return True


async def disconnect_database() -> None:
    global _database_connected
    if not _database_connected:
        return
    await Tortoise.close_connections()
    _database_connected = False
    logger.info("Tortoise ORM connections closed")
