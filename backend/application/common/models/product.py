from tortoise import fields

from application.common.models.base import OrmBaseModel


class Product(OrmBaseModel):
    """商品表。condition_level 成色 5全新 4几乎全新 3明显使用 2一般 1较差。
    status: 1在售 2已售 3下架。images 为 JSON 数组字符串列表。"""

    seller = fields.ForeignKeyField("models.User", related_name="products", description="卖家")
    category = fields.ForeignKeyField("models.Category", related_name="products", description="分类")
    title = fields.CharField(max_length=128, description="标题")
    description = fields.TextField(default="", description="描述")
    original_price = fields.DecimalField(max_digits=10, decimal_places=2, default=0, description="原价")
    sell_price = fields.DecimalField(max_digits=10, decimal_places=2, description="售价")
    condition_level = fields.SmallIntField(default=3, description="成色 1-5")
    images = fields.JSONField(default=list, description="图片URL列表")
    status = fields.SmallIntField(default=1, description="状态 1在售 2已售 3下架")
    view_count = fields.IntField(default=0, description="浏览量")

    class Meta:
        table = "product"
        indexes = [("status", "category_id"), ("seller_id",)]
