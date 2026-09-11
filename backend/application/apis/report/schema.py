from pydantic import Field

from application.common.schema import SnakeCaseModel


class CreateReportReq(SnakeCaseModel):
    product_id: int
    reason: str = Field(min_length=1, max_length=512)


class ReportRes(SnakeCaseModel):
    id: int
    reporter_id: int
    reporter_nickname: str
    product_id: int
    product_title: str
    reason: str
    status: int
    handler_result: str
    created_at: object = None
