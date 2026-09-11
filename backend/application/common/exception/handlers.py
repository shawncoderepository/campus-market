import logging
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError

from application.common.constants import HttpErrorCodeEnum
from application.common.exception.exception import HttpBusinessException
from application.common.helper.response_helper import ResponseHelper

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(HttpBusinessException)
    async def business_exception_handler(_: Request, exc: HttpBusinessException) -> Any:
        logger.warning("Business error: %s", exc.message)
        return ResponseHelper.error(code=exc.code, message=exc.message)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(_: Request, exc: RequestValidationError) -> Any:
        error = exc.errors()[0] if exc.errors() else {}
        message = str(error.get("msg", HttpErrorCodeEnum.PARAM_INVALID.message))
        return ResponseHelper.error(code=HttpErrorCodeEnum.PARAM_INVALID.code, message=message)

    @app.exception_handler(Exception)
    async def generic_exception_handler(_: Request, exc: Exception) -> Any:
        logger.exception("Unhandled error: %s", exc)
        return ResponseHelper.error()
