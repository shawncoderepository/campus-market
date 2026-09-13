import os
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, UploadFile

from application.apis.goods.schema import (
    GoodsDetailRes,
    GoodsItemRes,
    GoodsListQuery,
    PublishReq,
    SellerBrief,
    UpdateGoodsReq,
    UploadRes,
)
from application.common.config import config
from application.common.constants import HttpErrorCodeEnum
from application.common.dependency import get_current_user, get_current_user_optional
from application.common.exception.exception import HttpBusinessException
from application.common.helper.response_helper import ResponseHelper
from application.common.models import User
from application.common.schema.response_schema import BaseResponse, PageResult
from application.service.goods import goods_service

goods_router = APIRouter(prefix="/goods", tags=["Goods"])

_UPLOAD_ROOT = Path(__file__).resolve().parents[3] / config.upload.dir
_ALLOWED_EXT = {".jpg", ".jpeg", ".png", ".webp", ".gif"}


@goods_router.post("/publish", response_model=BaseResponse[GoodsItemRes], summary="发布商品")
async def publish(req: PublishReq, current: User = Depends(get_current_user)) -> object:
    product = await goods_service.publish(current, req.model_dump())
    product = await goods_service.get_detail(product.id, None)
    return ResponseHelper.success(GoodsItemRes(**goods_service.to_item_res(product)), message="发布成功")


@goods_router.get("/list", response_model=BaseResponse[PageResult[GoodsItemRes]], summary="商品列表")
async def list_goods(
    query: GoodsListQuery = Depends(),
    viewer: User | None = Depends(get_current_user_optional),
) -> object:
    items, total = await goods_service.list_goods(query.model_dump(), viewer)
    data = PageResult[GoodsItemRes](
        list=[GoodsItemRes(**goods_service.to_item_res(p)) for p in items],
        total=total,
        page=query.page,
        page_size=query.page_size,
    )
    return ResponseHelper.success(data)


@goods_router.get("/detail/{product_id}", response_model=BaseResponse[GoodsDetailRes], summary="商品详情")
async def detail(product_id: int, viewer: User | None = Depends(get_current_user_optional)) -> object:
    product = await goods_service.get_detail(product_id, viewer)
    base = goods_service.to_item_res(product)
    base["seller"] = SellerBrief(
        id=product.seller.id,
        nickname=product.seller.nickname,
        avatar=product.seller.avatar,
        credit_score=product.seller.credit_score,
    )
    base["is_favorited"] = await goods_service.is_favorited(viewer, product_id)
    related = await goods_service.related_goods(product)
    base["related"] = [GoodsItemRes(**goods_service.to_item_res(p)) for p in related]
    return ResponseHelper.success(GoodsDetailRes(**base))


@goods_router.put("/{product_id}", response_model=BaseResponse[GoodsItemRes], summary="编辑商品")
async def update(
    product_id: int, req: UpdateGoodsReq, current: User = Depends(get_current_user)
) -> object:
    product = await goods_service.update_goods(product_id, current, req.model_dump(exclude_none=True))
    product = await goods_service.get_detail(product.id, None)
    return ResponseHelper.success(GoodsItemRes(**goods_service.to_item_res(product)), message="修改成功")


@goods_router.delete("/{product_id}", summary="下架商品")
async def off_shelf(product_id: int, current: User = Depends(get_current_user)) -> object:
    await goods_service.update_goods(product_id, current, {"status": 3})
    return ResponseHelper.success(message="已下架")


@goods_router.get("/my/list", response_model=BaseResponse[PageResult[GoodsItemRes]], summary="我的商品")
async def my_goods(
    page: int = 1, page_size: int = 20, current: User = Depends(get_current_user)
) -> object:
    items, total = await goods_service.my_goods(current, page, page_size)
    data = PageResult[GoodsItemRes](
        list=[GoodsItemRes(**goods_service.to_item_res(p)) for p in items],
        total=total,
        page=page,
        page_size=page_size,
    )
    return ResponseHelper.success(data)


@goods_router.post("/upload", response_model=BaseResponse[UploadRes], summary="上传图片")
async def upload(file: UploadFile = File(...), current: User = Depends(get_current_user)) -> object:
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in _ALLOWED_EXT:
        raise HttpBusinessException(HttpErrorCodeEnum.PARAM_INVALID, "不支持的图片格式")
    content = await file.read()
    if len(content) > config.upload.max_size_mb * 1024 * 1024:
        raise HttpBusinessException(HttpErrorCodeEnum.PARAM_INVALID, "图片过大")
    _UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid.uuid4().hex}{ext}"
    ( _UPLOAD_ROOT / filename).write_bytes(content)
    return ResponseHelper.success(UploadRes(url=f"/uploads/{filename}"), message="上传成功")
