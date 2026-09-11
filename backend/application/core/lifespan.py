from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from application.core.database import connect_database, disconnect_database
from application.core.logger_util import logger
from application.core.redis_client import redis_client


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Register infrastructure startup/shutdown here, never domain logic."""
    logger.info("Application startup")
    try:
        await connect_database()
        await redis_client.connect()
        yield
    finally:
        await redis_client.close()
        await disconnect_database()
        logger.info("Application shutdown")
