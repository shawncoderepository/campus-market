from tortoise import fields

from application.common.models.base import OrmBaseModel


class User(OrmBaseModel):
    """用户表。role: 1 普通用户 2 管理员；status: 1 正常 0 禁用。"""

    username = fields.CharField(max_length=32, unique=True, description="用户名")
    password_hash = fields.CharField(max_length=128, description="密码哈希")
    nickname = fields.CharField(max_length=32, default="", description="昵称")
    avatar = fields.CharField(max_length=255, default="", description="头像URL")
    phone = fields.CharField(max_length=20, default="", description="手机号")
    student_no = fields.CharField(max_length=32, default="", description="学号")
    credit_score = fields.IntField(default=100, description="信用分")
    role = fields.SmallIntField(default=1, description="角色 1用户 2管理员")
    status = fields.SmallIntField(default=1, description="状态 1正常 0禁用")

    class Meta:
        table = "user"
