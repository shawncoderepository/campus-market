# 使用示例

以下代码用于展示扩展方式，不属于脚手架的正式业务模块。

## 示例一：读取请求上下文

```python
# application/apis/system/schema.py
from application.common.schema import SnakeCaseModel


class RequestInfoRes(SnakeCaseModel):
    request_id: str
    client_ip: str
    preferred_language: str
```

```python
# application/apis/system/system_api.py
from fastapi import APIRouter

from application.apis.system.schema import RequestInfoRes
from application.common.helper import ResponseHelper
from application.middleware import get_request_context

router = APIRouter()


@router.get("/request-info")
async def request_info() -> object:
    context = get_request_context()
    response = RequestInfoRes(
        request_id=context.request_id,
        client_ip=context.client_ip,
        preferred_language=context.language,
    )
    return ResponseHelper.success(response)
```

客户端可以传递 `X-Request-Id`；未传时中间件生成 UUID。响应头会返回同一个 `x-request-id`。

## 示例二：创建接口 DTO

```python
# application/apis/widgets/schema.py
from datetime import datetime

from application.common.schema import SnakeCaseModel


class CreateWidgetReq(SnakeCaseModel):
    widget_name: str
    display_order: int = 0


class CreateWidgetRes(SnakeCaseModel):
    widget_id: int
    widget_name: str
    display_order: int
    created_at: datetime
```

```python
# application/apis/widgets/widget_api.py
from datetime import datetime

from fastapi import APIRouter

from application.apis.widgets.schema import CreateWidgetReq, CreateWidgetRes
from application.common.helper import ResponseHelper
from application.common.schema import BaseResponse

router = APIRouter(prefix="/widgets", tags=["Widgets"])


@router.post("", response_model=BaseResponse[CreateWidgetRes])
async def create_widget(payload: CreateWidgetReq) -> object:
    # 实际项目中由 service 接收 payload 并返回 CreateWidgetRes。
    response = CreateWidgetRes(
        widget_id=1,
        widget_name=payload.widget_name,
        display_order=payload.display_order,
        created_at=datetime.now(),
    )
    return ResponseHelper.success(response)
```

请求：

```bash
curl -X POST http://127.0.0.1:8000/api/widgets \
  -H 'content-type: application/json' \
  -d '{"widget_name":"demo_widget","display_order":10}'
```

`{"widgetName":"demo"}` 会被拒绝，因为请求字段必须为 snake_case。

## 示例三：服务层与依赖注入

```python
from datetime import datetime
from typing import Protocol

from application.apis.widgets.schema import CreateWidgetReq, CreateWidgetRes


class WidgetRepository(Protocol):
    async def name_exists(self, widget_name: str) -> bool: ...


class WidgetService:
    def __init__(self, repository: WidgetRepository) -> None:
        self.repository = repository

    async def create_widget(self, request: CreateWidgetReq) -> CreateWidgetRes:
        if await self.repository.name_exists(request.widget_name):
            raise ValueError("widget_name already exists")
        return CreateWidgetRes(
            widget_id=1,
            widget_name=request.widget_name,
            display_order=request.display_order,
            created_at=datetime.now(),
        )
```

服务层接收 Pydantic Req/领域命令并返回 Pydantic Res/领域结果，不接收字典或 FastAPI `Request`。测试时传入内存 repository，即可快速验证业务规则。

## 示例四：添加自定义错误码

```python
class WidgetErrorCodeEnum(Enum):
    WIDGET_NOT_FOUND = (40410, "组件不存在")

    def __init__(self, code: int, message: str) -> None:
        self.code = code
        self.message = message
```

建议每个领域维护自己的错误码段，再抛出兼容 `code`、`message` 的领域异常；全局枚举只保留跨领域错误。

## 示例五：定义 Tortoise 模型

```python
from tortoise import fields

from application.common.models import OrmBaseModel


class Widget(OrmBaseModel):
    widget_name = fields.CharField(max_length=100, unique=True)
    display_order = fields.IntField(default=0)

    class Meta:
        table = "widget"
```

然后在 `application/common/models/__init__.py` 导入 `Widget`，使 Tortoise 在启动时发现模型。查询示例：

```python
widget = await Widget.create(widget_name="demo_widget", display_order=10)
widget_list = await Widget.filter(display_order__gte=0).order_by("display_order")
```

## 示例六：Redis 缓存与计数器

```python
from application.core.redis_client import TimeUnit, redis_client

await redis_client.set(
    "widget:1",
    {"widget_id": 1, "widget_name": "demo_widget"},
    time=10,
    unit=TimeUnit.MINUTES,
)
widget = await redis_client.get("widget:1")

view_count = await redis_client.incr("widget:1:view_count")
await redis_client.expire("widget:1:view_count", 1, TimeUnit.DAYS)
```

实际 Redis 键会自动变成 `{key_prefix}:widget:1`，业务代码不需要重复拼接应用前缀。

## 示例七：Redis 集合和分布式锁

```python
await redis_client.sadd("online_user_ids", "1001", "1002")
is_online = await redis_client.sismember("online_user_ids", "1001")
online_user_ids = await redis_client.smembers("online_user_ids")

async with redis_client.lock("widget:1:update", expire=10, blocking_timeout=3):
    # 同一时刻只允许一个实例执行的短任务
    await update_widget()
```

锁的 `expire` 必须大于受保护任务的正常执行时间。长任务需要续期策略，且不能把 Redis 锁当作数据库事务替代品。
