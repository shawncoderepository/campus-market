from application.common.schema import SnakeCaseModel


class CategoryRes(SnakeCaseModel):
    id: int
    name: str
    icon: str
    sort: int
