from pydantic import Field

from application.common.schema import SnakeCaseModel


class CopyReq(SnakeCaseModel):
    keywords: str = Field(min_length=1, max_length=128, description="商品关键词")
    category_name: str = Field(default="其他", max_length=32)
    condition_level: int = Field(default=3, ge=1, le=5)
    original_price: float = Field(default=0, ge=0)


class CopyRes(SnakeCaseModel):
    title: str
    description: str
    source: str


class EstimateReq(SnakeCaseModel):
    category_name: str = Field(default="其他", max_length=32)
    original_price: float = Field(gt=0)
    condition_level: int = Field(default=3, ge=1, le=5)
    used_years: float = Field(default=1.0, ge=0, le=50)


class EstimateRes(SnakeCaseModel):
    suggested_price: float
    price_low: float
    price_high: float
    source: str
    reason: str


class BargainAssistReq(SnakeCaseModel):
    product_title: str = Field(min_length=1, max_length=128)
    sell_price: float = Field(gt=0)
    buyer_offer: float = Field(gt=0)
    buyer_message: str = Field(default="", max_length=512)
    round_no: int = Field(default=1, ge=1)
    # side: seller 给卖家建议 / buyer 给买家建议
    side: str = Field(default="seller", pattern="^(seller|buyer)$")


class BargainAssistRes(SnakeCaseModel):
    reply: str
    counter_price: float | None
    source: str
