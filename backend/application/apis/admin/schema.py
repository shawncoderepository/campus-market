from pydantic import Field

from application.common.schema import SnakeCaseModel


class AdminStatsRes(SnakeCaseModel):
    user_total: int
    goods_total: int
    goods_on_sale: int
    order_total: int
    order_done: int
    deal_amount: float
    report_pending: int
    category_total: int
    review_total: int
    # 较上周增长率（百分比，可能为负；None 表示上周无数据无法计算）
    user_wow: float | None = None
    goods_wow: float | None = None
    order_wow: float | None = None
    deal_amount_wow: float | None = None
    report_wow: float | None = None
    review_wow: float | None = None


class AdminCategoryShare(SnakeCaseModel):
    name: str
    count: int
    percent: float


class AdminActivity(SnakeCaseModel):
    id: str
    user: str
    action: str
    target: str = ""
    time: str
    color: str


class AdminUserRes(SnakeCaseModel):
    id: int
    username: str
    nickname: str
    avatar: str
    phone: str
    student_no: str
    credit_score: int
    role: int
    status: int
    created_at: object = None


class AdminUserStatusReq(SnakeCaseModel):
    status: int = Field(..., ge=0, le=1, description="1正常 0禁用")


class AdminUserCreditReq(SnakeCaseModel):
    credit_score: int = Field(..., ge=0, le=100, description="信用分 0-100")


class AdminCategoryReq(SnakeCaseModel):
    name: str = Field(..., min_length=1, max_length=32)
    icon: str = Field(default="📦", max_length=8)
    sort: int = Field(default=0, ge=0)


class AdminCategoryRes(SnakeCaseModel):
    id: int
    name: str
    icon: str
    sort: int
    goods_count: int = 0


class AdminReportHandleReq(SnakeCaseModel):
    status: int = Field(..., ge=2, le=3, description="2已处理 3已驳回")
    handler_result: str = Field(default="", max_length=255)


class AdminGoodsStatusReq(SnakeCaseModel):
    status: int = Field(..., ge=1, le=3, description="1在售 2已售 3下架")
