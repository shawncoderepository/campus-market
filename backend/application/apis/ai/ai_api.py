from fastapi import APIRouter, Depends

from application.apis.ai.schema import (
    BargainAssistReq,
    BargainAssistRes,
    CopyReq,
    CopyRes,
    EstimateReq,
    EstimateRes,
)
from application.common.dependency import get_current_user
from application.common.helper.response_helper import ResponseHelper
from application.common.models import User
from application.common.schema.response_schema import BaseResponse
from application.service.ai import ai_service

ai_router = APIRouter(prefix="/ai", tags=["AI"])


@ai_router.post("/copy", response_model=BaseResponse[CopyRes], summary="AI 帮写文案")
async def copy(req: CopyReq, current: User = Depends(get_current_user)) -> object:
    data = await ai_service.generate_copy(
        req.keywords, req.category_name, req.condition_level, req.original_price
    )
    return ResponseHelper.success(CopyRes(**data), message="生成成功")


@ai_router.post("/estimate", response_model=BaseResponse[EstimateRes], summary="AI 智能估价")
async def estimate(req: EstimateReq, current: User = Depends(get_current_user)) -> object:
    data = await ai_service.estimate_price(
        req.category_name, req.original_price, req.condition_level, req.used_years
    )
    return ResponseHelper.success(EstimateRes(**data), message="估价成功")


@ai_router.post("/bargain", response_model=BaseResponse[BargainAssistRes], summary="AI 议价助手")
async def bargain(req: BargainAssistReq, current: User = Depends(get_current_user)) -> object:
    data = await ai_service.bargain_assist(
        req.product_title, req.sell_price, req.buyer_offer, req.buyer_message,
        req.round_no, req.side,
    )
    return ResponseHelper.success(BargainAssistRes(**data), message="已生成议价建议")
