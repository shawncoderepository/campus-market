from fastapi import APIRouter, Depends

from application.apis.bargain.schema import (
    BargainOfferReq,
    BargainRecordRes,
    BargainReplyReq,
    BargainRespondReq,
    BargainSessionRes,
)
from application.common.dependency import get_current_user
from application.common.helper.response_helper import ResponseHelper
from application.common.models import User
from application.common.schema.response_schema import BaseResponse
from application.service.bargain import bargain_service

bargain_router = APIRouter(prefix="/bargain", tags=["Bargain"])


@bargain_router.post("/offer", response_model=BaseResponse[BargainRecordRes], summary="买家出价")
async def buyer_offer(req: BargainOfferReq, current: User = Depends(get_current_user)) -> object:
    record = await bargain_service.buyer_offer(
        current, req.product_id, req.offer_price, req.message
    )
    return ResponseHelper.success(
        BargainRecordRes(**bargain_service.to_record_res(record)), message="出价成功"
    )


@bargain_router.post("/reply", response_model=BaseResponse[BargainRecordRes], summary="卖家还价")
async def seller_reply(req: BargainReplyReq, current: User = Depends(get_current_user)) -> object:
    record = await bargain_service.seller_reply(
        current, req.product_id, req.buyer_id, req.offer_price, req.message
    )
    return ResponseHelper.success(
        BargainRecordRes(**bargain_service.to_record_res(record)), message="还价成功"
    )


@bargain_router.post("/respond", response_model=BaseResponse[BargainRecordRes], summary="接受/拒绝出价")
async def respond(req: BargainRespondReq, current: User = Depends(get_current_user)) -> object:
    record = await bargain_service.respond(current, req.record_id, req.accept)
    msg = "已接受" if req.accept else "已拒绝"
    return ResponseHelper.success(
        BargainRecordRes(**bargain_service.to_record_res(record)), message=msg
    )


@bargain_router.get("/session", response_model=BaseResponse[BargainSessionRes], summary="议价会话")
async def session(
    product_id: int, buyer_id: int | None = None, current: User = Depends(get_current_user)
) -> object:
    data = await bargain_service.session(current, product_id, buyer_id)
    return ResponseHelper.success(BargainSessionRes(**data))


@bargain_router.get("/my", response_model=BaseResponse[list[BargainRecordRes]], summary="我的议价会话列表")
async def my_sessions(current: User = Depends(get_current_user)) -> object:
    data = await bargain_service.my_sessions(current)
    return ResponseHelper.success([BargainRecordRes(**d) for d in data])
