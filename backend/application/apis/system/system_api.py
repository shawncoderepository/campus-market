from fastapi import APIRouter

from application.apis.system.schema import HealthRes, VersionRes
from application.common.config import config
from application.common.helper.response_helper import ResponseHelper
from application.common.schema.response_schema import BaseResponse

system_router = APIRouter(tags=["System"])


@system_router.get("/health", response_model=BaseResponse[HealthRes], summary="Health check")
async def health() -> object:
    response = HealthRes(service_name=config.project_name, service_status="ok")
    return ResponseHelper.success(response)


@system_router.get("/version", response_model=BaseResponse[VersionRes], summary="Version info")
async def version() -> object:
    response = VersionRes(version=config.version)
    return ResponseHelper.success(response)
