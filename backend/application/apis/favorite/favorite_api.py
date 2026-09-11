from fastapi import APIRouter, Depends

from application.apis.favorite.schema import FavoriteStatusRes, FavoriteToggleReq
from application.apis.goods.schema import GoodsItemRes
from application.common.dependency import get_current_user
from application.common.helper.response_helper import ResponseHelper
from application.common.models import Favorite, User
from application.common.schema.response_schema import BaseResponse, PageResult
from application.service.goods import goods_service

favorite_router = APIRouter(prefix="/favorite", tags=["Favorite"])


@favorite_router.post("/toggle", response_model=BaseResponse[FavoriteStatusRes], summary="收藏/取消收藏")
async def toggle(req: FavoriteToggleReq, current: User = Depends(get_current_user)) -> object:
    existing = await Favorite.get_or_none(user=current, product_id=req.product_id)
    if existing:
        await existing.delete()
        return ResponseHelper.success(FavoriteStatusRes(is_favorited=False), message="已取消收藏")
    await Favorite.create(user=current, product_id=req.product_id)
    return ResponseHelper.success(FavoriteStatusRes(is_favorited=True), message="收藏成功")


@favorite_router.get("/list", response_model=BaseResponse[PageResult[GoodsItemRes]], summary="我的收藏")
async def my_favorites(
    page: int = 1, page_size: int = 20, current: User = Depends(get_current_user)
) -> object:
    qs = Favorite.filter(user=current).prefetch_related("product__category", "product__seller")
    total = await qs.count()
    favorites = await qs.order_by("-created_at").offset((page - 1) * page_size).limit(page_size)
    items = [GoodsItemRes(**goods_service.to_item_res(f.product)) for f in favorites]
    return ResponseHelper.success(
        PageResult[GoodsItemRes](list=items, total=total, page=page, page_size=page_size)
    )
