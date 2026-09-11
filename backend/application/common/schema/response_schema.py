from __future__ import annotations

import builtins

from pydantic import Field

from application.common.schema.base_schema import SnakeCaseModel


class BaseResponse[T](SnakeCaseModel):
    code: int = Field(default=0, description="Response code; zero means success")
    message: str = Field(default="成功", description="Response message")
    data: T = Field(description="Response payload")


class PageResult[T](SnakeCaseModel):
    list: builtins.list[T] = Field(default_factory=builtins.list, description="Current page items")
    total: int = Field(ge=0, description="Total item count")
    page: int = Field(ge=1, description="Current page number")
    page_size: int = Field(ge=1, description="Items per page")
