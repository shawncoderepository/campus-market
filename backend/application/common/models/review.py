from tortoise import fields

from application.common.models.base import OrmBaseModel


class Review(OrmBaseModel):
    """评价表：一个订单一条评价。"""

    order = fields.OneToOneField("models.Order", related_name="review", description="订单")
    reviewer = fields.ForeignKeyField("models.User", related_name="reviews_made", description="评价人")
    target = fields.ForeignKeyField("models.User", related_name="reviews_received", description="被评价人")
    rating = fields.SmallIntField(default=5, description="评分 1-5")
    content = fields.CharField(max_length=512, default="", description="评价内容")
    tags = fields.JSONField(default=list, description="评价标签")

    class Meta:
        table = "review"
