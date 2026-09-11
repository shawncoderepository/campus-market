from tortoise import fields

from application.common.models.base import OrmBaseModel


class Favorite(OrmBaseModel):
    """收藏表：user 与 product 的多对多关系。"""

    user = fields.ForeignKeyField("models.User", related_name="favorites", description="用户")
    product = fields.ForeignKeyField("models.Product", related_name="favorited_by", description="商品")

    class Meta:
        table = "favorite"
        unique_together = (("user", "product"),)
