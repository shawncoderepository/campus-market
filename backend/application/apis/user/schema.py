from pydantic import Field

from application.common.schema import SnakeCaseModel


class RegisterReq(SnakeCaseModel):
    username: str = Field(min_length=3, max_length=32, description="用户名")
    password: str = Field(min_length=6, max_length=64, description="密码")
    nickname: str = Field(default="", max_length=32, description="昵称")
    student_no: str = Field(default="", max_length=32, description="学号")


class LoginReq(SnakeCaseModel):
    username: str = Field(min_length=3, max_length=32)
    password: str = Field(min_length=6, max_length=64)


class LoginRes(SnakeCaseModel):
    token: str
    user: "UserRes"


class UserRes(SnakeCaseModel):
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


class UpdateProfileReq(SnakeCaseModel):
    nickname: str | None = Field(default=None, max_length=32)
    avatar: str | None = None
    phone: str | None = Field(default=None, max_length=20)
    student_no: str | None = Field(default=None, max_length=32)


class ChangePasswordReq(SnakeCaseModel):
    old_password: str = Field(min_length=6, max_length=64)
    new_password: str = Field(min_length=6, max_length=64)


class UserStatsRes(SnakeCaseModel):
    goods_total: int = 0
    goods_on_sale: int = 0
    goods_sold: int = 0
    favorite_total: int = 0
    order_buy_total: int = 0
    order_sell_total: int = 0
    review_received_total: int = 0
    avg_rating: float | None = None
    # 管理员维度
    user_total: int | None = None
    report_pending: int | None = None


LoginRes.model_rebuild()
