from tortoise import fields

from application.common.models.base import OrmBaseModel


class Category(OrmBaseModel):
    """商品分类表。"""

    name = fields.CharField(max_length=32, unique=True, description="分类名")
    icon = fields.CharField(max_length=255, default="", description="图标")
    sort = fields.IntField(default=0, description="排序")

    class Meta:
        table = "category"
