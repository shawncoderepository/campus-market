from pydantic import Field

from application.common.schema import SnakeCaseModel


class CreateOrderReq(SnakeCaseModel):
    product_id: int
    # 若是议价成交，传入被接受的议价记录 id，用其 offer_price 作为成交价
    bargain_record_id: int | None = None
    address: str = Field(default="", max_length=255)
    remark: str = Field(default="", max_length=255)


class OrderRes(SnakeCaseModel):
    id: int
    order_no: str
    product_id: int
    product_title: str
    product_image: str
    buyer_id: int
    buyer_nickname: str
    seller_id: int
    seller_nickname: str
    deal_price: float
    status: int
    address: str
    remark: str
    has_review: bool = False
    created_at: object = None


class OrderActionReq(SnakeCaseModel):
    order_id: int
