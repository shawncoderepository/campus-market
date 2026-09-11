from pydantic import Field

from application.common.schema import SnakeCaseModel


class CreateReviewReq(SnakeCaseModel):
    order_id: int
    rating: int = Field(ge=1, le=5)
    content: str = Field(default="", max_length=512)
    tags: list[str] = Field(default_factory=list)


class ReviewRes(SnakeCaseModel):
    id: int
    order_id: int
    reviewer_id: int
    reviewer_nickname: str
    reviewer_avatar: str
    target_id: int
    rating: int
    content: str
    tags: list[str]
    created_at: object = None
