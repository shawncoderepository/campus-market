from pydantic import Field

from application.common.schema import SnakeCaseModel


class BargainOfferReq(SnakeCaseModel):
    product_id: int
    offer_price: float = Field(gt=0)
    message: str = Field(default="", max_length=512)


class BargainReplyReq(SnakeCaseModel):
    product_id: int
    buyer_id: int
    offer_price: float = Field(gt=0)
    message: str = Field(default="", max_length=512)


class BargainRespondReq(SnakeCaseModel):
    # 对最近一条待响应出价做 接受/拒绝
    record_id: int
    accept: bool


class BargainRecordRes(SnakeCaseModel):
    id: int
    product_id: int
    product_title: str
    product_image: str
    buyer_id: int
    buyer_nickname: str
    seller_id: int
    seller_nickname: str
    round: int
    offer_price: float | None
    role: str
    message: str
    status: int
    created_at: object = None


class BargainSessionRes(SnakeCaseModel):
    product_id: int
    product_title: str
    product_image: str
    sell_price: float
    buyer_id: int
    buyer_nickname: str
    seller_id: int
    seller_nickname: str
    records: list[BargainRecordRes] = Field(default_factory=list)
    # 当前最新待响应记录 id（若有），便于做接受/拒绝
    pending_record_id: int | None = None
    # 当前轮到谁出价 buyer/seller/none
    turn: str = "none"
