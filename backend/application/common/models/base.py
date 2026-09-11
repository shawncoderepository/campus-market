from tortoise import fields, models


class TimestampMixin(models.Model):
    """Reusable created/updated timestamps for domain models."""

    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")
    updated_at = fields.DatetimeField(auto_now=True, description="更新时间")

    class Meta:
        abstract = True


class OrmBaseModel(TimestampMixin):
    """Generic bigint primary key plus timestamps; contains no domain fields."""

    id = fields.BigIntField(primary_key=True, description="主键")

    class Meta:
        abstract = True
