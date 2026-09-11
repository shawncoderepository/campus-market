from tortoise import fields

from application.common.models.base import OrmBaseModel


class BargainRecord(OrmBaseModel):
    """议价记录表。一次议价会话由同一 (product_id, buyer_id) 下的多条记录组成。
    role: buyer 买家 / seller 卖家 / ai AI助手。status: 1待响应 2已接受 3已拒绝。"""

    product = fields.ForeignKeyField("models.Product", related_name="bargains", description="商品")
    buyer = fields.ForeignKeyField("models.User", related_name="bargains_as_buyer", description="买家")
    seller = fields.ForeignKeyField("models.User", related_name="bargains_as_seller", description="卖家")
    round = fields.IntField(default=1, description="议价轮次")
    offer_price = fields.DecimalField(max_digits=10, decimal_places=2, null=True, description="出价")
    role = fields.CharField(max_length=10, description="出价方 buyer/seller/ai")
    message = fields.CharField(max_length=512, default="", description="留言")
    status = fields.SmallIntField(default=1, description="状态 1待响应 2已接受 3已拒绝")

    class Meta:
        table = "bargain_record"
        indexes = [("product_id", "buyer_id")]
