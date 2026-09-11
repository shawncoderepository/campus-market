from fastapi import APIRouter

from application.apis.category.schema import CategoryRes
from application.common.helper.response_helper import ResponseHelper
from application.common.models import Category
from application.common.schema.response_schema import BaseResponse

category_router = APIRouter(prefix="/category", tags=["Category"])


@category_router.get("/list", response_model=BaseResponse[list[CategoryRes]], summary="分类列表")
async def list_categories() -> object:
    categories = await Category.all().order_by("sort")
    data = [CategoryRes(id=c.id, name=c.name, icon=c.icon, sort=c.sort) for c in categories]
    return ResponseHelper.success(data)
