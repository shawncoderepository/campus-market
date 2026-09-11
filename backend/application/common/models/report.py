from tortoise import fields

from application.common.models.base import OrmBaseModel


class Report(OrmBaseModel):
    """举报表。status: 1待处理 2已处理 3已驳回。"""

    reporter = fields.ForeignKeyField("models.User", related_name="reports", description="举报人")
    product = fields.ForeignKeyField("models.Product", related_name="reports", description="被举报商品")
    reason = fields.CharField(max_length=512, description="举报原因")
    status = fields.SmallIntField(default=1, description="状态 1待处理 2已处理 3已驳回")
    handler_result = fields.CharField(max_length=255, default="", description="处理结果")

    class Meta:
        table = "report"
