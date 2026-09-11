from tortoise import fields

from application.common.models.base import OrmBaseModel


class Message(OrmBaseModel):
    """站内消息/聊天表。"""

    sender = fields.ForeignKeyField("models.User", related_name="messages_sent", description="发送者")
    receiver = fields.ForeignKeyField("models.User", related_name="messages_received", description="接收者")
    product = fields.ForeignKeyField("models.Product", related_name="messages", null=True, description="关联商品")
    content = fields.CharField(max_length=1024, description="消息内容")
    msg_type = fields.SmallIntField(default=1, description="类型 1文本 2系统")
    is_read = fields.BooleanField(default=False, description="是否已读")

    class Meta:
        table = "message"
        indexes = [("sender_id", "receiver_id"), ("receiver_id", "is_read")]
