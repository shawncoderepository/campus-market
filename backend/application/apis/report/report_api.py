from fastapi import APIRouter, Depends

from application.apis.report.schema import CreateReportReq, ReportRes
from application.common.constants import HttpErrorCodeEnum
from application.common.dependency import get_current_user
from application.common.exception.exception import HttpBusinessException
from application.common.helper.response_helper import ResponseHelper
from application.common.models import Product, Report, User
from application.common.schema.response_schema import BaseResponse, PageResult

report_router = APIRouter(prefix="/report", tags=["Report"])


def _to_res(r: Report) -> dict:
    return {
        "id": r.id,
        "reporter_id": r.reporter_id,
        "reporter_nickname": getattr(r.reporter, "nickname", "") if hasattr(r, "reporter") else "",
        "product_id": r.product_id,
        "product_title": getattr(r.product, "title", "") if hasattr(r, "product") else "",
        "reason": r.reason,
        "status": r.status,
        "handler_result": r.handler_result,
        "created_at": r.created_at,
    }


@report_router.post("/create", response_model=BaseResponse[ReportRes], summary="提交举报")
async def create(req: CreateReportReq, current: User = Depends(get_current_user)) -> object:
    product = await Product.get_or_none(id=req.product_id)
    if product is None:
        raise HttpBusinessException(HttpErrorCodeEnum.NOT_FOUND, "商品不存在")
    report = await Report.create(reporter=current, product=product, reason=req.reason)
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
