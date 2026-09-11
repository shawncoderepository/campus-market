from pydantic import Field

from application.common.schema import SnakeCaseModel


class CategoryRes(SnakeCaseModel):
    id: int
    name: str
    icon: str
    sort: int


class PublishReq(SnakeCaseModel):
    category_id: int
    title: str = Field(min_length=1, max_length=128)
    description: str = Field(default="", max_length=5000)
    original_price: float = Field(default=0, ge=0)
    sell_price: float = Field(gt=0)
    condition_level: int = Field(default=3, ge=1, le=5)
    images: list[str] = Field(default_factory=list)


class UpdateGoodsReq(SnakeCaseModel):
    category_id: int | None = None
    title: str | None = Field(default=None, min_length=1, max_length=128)
    description: str | None = Field(default=None, max_length=5000)
    original_price: float | None = Field(default=None, ge=0)
    sell_price: float | None = Field(default=None, gt=0)
    condition_level: int | None = Field(default=None, ge=1, le=5)
    images: list[str] | None = None
    status: int | None = Field(default=None, ge=1, le=3)


class GoodsListQuery(SnakeCaseModel):
    keyword: str = ""
    category_id: int | None = None
    min_price: float | None = None
    max_price: float | None = None
    condition_level: int | None = None
    # 排序: latest 最新 / price_asc / price_desc / hot 热度
    sort: str = "latest"
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class SellerBrief(SnakeCaseModel):
    id: int
    nickname: str
    avatar: str
    credit_score: int


class GoodsItemRes(SnakeCaseModel):
    id: int
    title: str
    description: str
    original_price: float
    sell_price: float
    condition_level: int
    images: list[str]
    status: int
    view_count: int
    category_id: int
    category_name: str
    seller_id: int
    seller_nickname: str
    seller_avatar: str
    created_at: object = None


class GoodsDetailRes(GoodsItemRes):
    seller: SellerBrief | None = None
    is_favorited: bool = False
    ai_suggest_price: float | None = None
    related: list[GoodsItemRes] = Field(default_factory=list)


class UploadRes(SnakeCaseModel):
    url: str
