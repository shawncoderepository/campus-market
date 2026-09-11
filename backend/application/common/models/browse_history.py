from tortoise import fields

from application.common.models.base import OrmBaseModel


class BrowseHistory(OrmBaseModel):
    """浏览历史表：用于商品推荐。"""

    user = fields.ForeignKeyField("models.User", related_name="browse_histories", description="用户")
    product = fields.ForeignKeyField("models.Product", related_name="browse_histories", description="商品")

    class Meta:
        table = "browse_history"
        indexes = [("user_id",)]
