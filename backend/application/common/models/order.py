from tortoise import fields

from application.common.models.base import OrmBaseModel


class Order(OrmBaseModel):
    """订单表。status: 1待付款 2待发货 3待收货 4已完成 5已取消。"""

    order_no = fields.CharField(max_length=32, unique=True, description="订单号")
    product = fields.ForeignKeyField("models.Product", related_name="orders", description="商品")
    buyer = fields.ForeignKeyField("models.User", related_name="orders_as_buyer", description="买家")
    seller = fields.ForeignKeyField("models.User", related_name="orders_as_seller", description="卖家")
    deal_price = fields.DecimalField(max_digits=10, decimal_places=2, description="成交价")
    status = fields.SmallIntField(default=1, description="状态 1待付款 2待发货 3待收货 4已完成 5已取消")
    address = fields.CharField(max_length=255, default="", description="收货地址")
    remark = fields.CharField(max_length=255, default="", description="备注")

    class Meta:
        table = "orders"
        indexes = [("buyer_id", "status"), ("seller_id", "status")]
