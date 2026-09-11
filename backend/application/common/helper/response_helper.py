import re
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Any

from pydantic import BaseModel
from starlette.responses import JSONResponse

from application.common.constants import HttpErrorCodeEnum
from application.common.schema import BaseResponse

_SNAKE_CASE_PATTERN = re.compile(r"^[a-z][a-z0-9]*(?:_[a-z0-9]+)*$")


class ResponseDateTimeFormat(Enum):
    ISO = "iso"
    YMDHMS = "%Y-%m-%d %H:%M:%S"


def to_serializable(value: Any, datetime_format: ResponseDateTimeFormat) -> Any:
    if isinstance(value, BaseModel):
        return to_serializable(value.model_dump(), datetime_format)
    if isinstance(value, datetime):
        return (
            value.isoformat()
            if datetime_format is ResponseDateTimeFormat.ISO
            else value.strftime(datetime_format.value)
        )
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, dict):
        output: dict[str, Any] = {}
        for key, item in value.items():
            if not isinstance(key, str) or not _SNAKE_CASE_PATTERN.fullmatch(key):
                raise ValueError(f"Response key must use snake_case: {key!r}")
            output[key] = to_serializable(item, datetime_format)
        return output
    if isinstance(value, (list, tuple, set)):
        return [to_serializable(item, datetime_format) for item in value]
    return value


class ResponseHelper:
    @staticmethod
    def _response(
        code: int,
        message: str,
        data: BaseModel | list | None,
        datetime_format: ResponseDateTimeFormat,
    ) -> JSONResponse:
        if data is not None and not isinstance(data, (BaseModel, list)):
            raise TypeError("Response data must be a Pydantic BaseModel, a list, or None")
        if isinstance(data, list) and any(not isinstance(item, BaseModel) for item in data):
            raise TypeError("All items in a list response must be Pydantic BaseModel")

        payload: Any = data if data is not None else None
        response_model = BaseResponse[Any](code=code, message=message, data=payload)
        content = to_serializable(response_model, datetime_format)
        return JSONResponse(content=content, status_code=200)

    @staticmethod
    def success(
        data: BaseModel | list | None = None,
        message: str = "成功",
        code: int = HttpErrorCodeEnum.SUCCESS.code,
        datetime_format: ResponseDateTimeFormat = ResponseDateTimeFormat.YMDHMS,
    ) -> JSONResponse:
        return ResponseHelper._response(code, message, data, datetime_format)

    @staticmethod
    def error(
        code: int = HttpErrorCodeEnum.ERROR.code,
        message: str = HttpErrorCodeEnum.ERROR.message,
        data: BaseModel | None = None,
    ) -> JSONResponse:
        return ResponseHelper._response(
            code,
            message,
            data,
            ResponseDateTimeFormat.YMDHMS,
        )
