from application.common.schema import SnakeCaseModel


class FavoriteToggleReq(SnakeCaseModel):
    product_id: int


class FavoriteStatusRes(SnakeCaseModel):
    is_favorited: bool
