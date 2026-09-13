from pydantic import Field

from application.common.schema import SnakeCaseModel


class CreateReportReq(SnakeCaseModel):
    product_id: int
    reason_type: str = Field(default="other", max_length=32, description="违规类型编码")
    reason: str = Field(default="", max_length=512, description="补充说明")


class ReportRes(SnakeCaseModel):
    id: int
    reporter_id: int
    reporter_nickname: str
    product_id: int
    product_title: str
    seller_id: int = 0
    seller_nickname: str = ""
    reason_type: str = "other"
    reason_type_name: str = ""
    reason: str
    status: int
    handler_result: str
    created_at: object = None
