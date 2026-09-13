from fastapi import APIRouter, Depends

from application.apis.report.schema import CreateReportReq, ReportRes
from application.common.constants import HttpErrorCodeEnum
from application.common.constants.report_constant import reason_type_name
from application.common.dependency import get_current_user
from application.common.exception.exception import HttpBusinessException
from application.common.helper.response_helper import ResponseHelper
from application.common.models import Product, Report, User
from application.common.schema.response_schema import BaseResponse, PageResult

report_router = APIRouter(prefix="/report", tags=["Report"])


def _to_res(r: Report) -> dict:
    product = r.product if hasattr(r, "product") else None
    seller = getattr(product, "seller", None) if product is not None else None
    # 未预取时 seller 是 QuerySet（无 id/nickname），安全回退
    seller_id = getattr(seller, "id", 0) or 0
    seller_nickname = getattr(seller, "nickname", "") or ""
    return {
        "id": r.id,
        "reporter_id": r.reporter_id,
        "reporter_nickname": getattr(r.reporter, "nickname", "") if hasattr(r, "reporter") else "",
        "product_id": r.product_id,
        "product_title": getattr(product, "title", "") if product is not None else "",
        "seller_id": seller_id,
        "seller_nickname": seller_nickname,
        "reason_type": r.reason_type,
        "reason_type_name": reason_type_name(r.reason_type),
        "reason": r.reason,
        "status": r.status,
        "handler_result": r.handler_result,
        "created_at": r.created_at,
    }


@report_router.post("/create", response_model=BaseResponse[ReportRes], summary="提交举报")
async def create(req: CreateReportReq, current: User = Depends(get_current_user)) -> object:
    product = await Product.get_or_none(id=req.product_id).prefetch_related("seller")
    if product is None:
        raise HttpBusinessException(HttpErrorCodeEnum.NOT_FOUND, "商品不存在")
    if product.seller_id == current.id:
        raise HttpBusinessException(HttpErrorCodeEnum.PARAM_INVALID, "不能举报自己的商品")
    report = await Report.create(
        reporter=current, product=product, reason_type=req.reason_type, reason=req.reason
    )
    report.reporter = current
    report.product = product
    return ResponseHelper.success(ReportRes(**_to_res(report)), message="举报成功，我们会尽快处理")


@report_router.get("/my", response_model=BaseResponse[PageResult[ReportRes]], summary="我的举报")
async def my_reports(
    page: int = 1, page_size: int = 20, current: User = Depends(get_current_user)
) -> object:
    qs = Report.filter(reporter=current).prefetch_related("reporter", "product")
    total = await qs.count()
    reports = await qs.order_by("-id").offset((page - 1) * page_size).limit(page_size)
    return ResponseHelper.success(
        PageResult[ReportRes](
            list=[ReportRes(**_to_res(r)) for r in reports], total=total, page=page, page_size=page_size
        )
    )
