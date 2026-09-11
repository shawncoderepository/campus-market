from fastapi import APIRouter, Depends

from application.apis.review.schema import CreateReviewReq, ReviewRes
from application.common.constants import HttpErrorCodeEnum
from application.common.dependency import get_current_user
from application.common.exception.exception import HttpBusinessException
from application.common.helper.response_helper import ResponseHelper
from application.common.models import Order, Review, User
from application.common.schema.response_schema import BaseResponse, PageResult

review_router = APIRouter(prefix="/review", tags=["Review"])


def _to_res(r: Review) -> dict:
    return {
        "id": r.id,
        "order_id": r.order_id,
        "reviewer_id": r.reviewer_id,
        "reviewer_nickname": getattr(r.reviewer, "nickname", "") if hasattr(r, "reviewer") else "",
        "reviewer_avatar": getattr(r.reviewer, "avatar", "") if hasattr(r, "reviewer") else "",
        "target_id": r.target_id,
        "rating": r.rating,
        "content": r.content,
        "tags": r.tags or [],
        "created_at": r.created_at,
    }


@review_router.post("/create", response_model=BaseResponse[ReviewRes], summary="发表评价")
async def create(req: CreateReviewReq, current: User = Depends(get_current_user)) -> object:
    order = await Order.get_or_none(id=req.order_id)
    if order is None:
        raise HttpBusinessException(HttpErrorCodeEnum.NOT_FOUND, "订单不存在")
    if order.status != 4:
        raise HttpBusinessException(HttpErrorCodeEnum.PARAM_INVALID, "订单未完成，无法评价")
    if current.id not in (order.buyer_id, order.seller_id):
        raise HttpBusinessException(HttpErrorCodeEnum.FORBIDDEN, "无权评价该订单")
    existing = await Review.get_or_none(order_id=req.order_id)
    if existing:
        raise HttpBusinessException(HttpErrorCodeEnum.PARAM_INVALID, "该订单已评价")
    target_id = order.seller_id if current.id == order.buyer_id else order.buyer_id
    review = await Review.create(
        order_id=req.order_id,
        reviewer=current,
        target_id=target_id,
        rating=req.rating,
        content=req.content,
        tags=req.tags,
    )
    review.reviewer = current
    return ResponseHelper.success(ReviewRes(**_to_res(review)), message="评价成功")


@review_router.get(
    "/received/{user_id}",
    response_model=BaseResponse[PageResult[ReviewRes]],
    summary="某用户收到的评价",
)
async def received(user_id: int, page: int = 1, page_size: int = 20) -> object:
    qs = Review.filter(target_id=user_id).prefetch_related("reviewer")
    total = await qs.count()
    reviews = await qs.order_by("-id").offset((page - 1) * page_size).limit(page_size)
    return ResponseHelper.success(
        PageResult[ReviewRes](
            list=[ReviewRes(**_to_res(r)) for r in reviews], total=total, page=page, page_size=page_size
        )
    )
