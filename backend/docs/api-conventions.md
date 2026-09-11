# API 与 snake_case 约定

## 统一响应

所有接口返回以下顶层结构：

```json
{
  "code": 0,
  "message": "成功",
  "data": {}
}
```

- `code`：稳定的数字业务码，`0` 表示成功。
- `message`：用户可读消息。
- `data`：固定存在的载荷；无数据或错误时为 `null`。

当前脚手架沿用参考项目约定：业务错误 HTTP 状态仍为 `200`，通过 `code === 0` 判断成功。如果项目需要 REST 状态码，可统一修改 `ResponseHelper.error`，不要在单个路由中混用两套规则。

对应前端类型：

```typescript
export interface ApiResponse<T> {
  code: number
  message: string
  data: T
}

export interface PageResult<T> {
  list: T[]
  total: number
  page: number
  page_size: number
}
```

后端统一要求 snake_case，因此分页字段为 `page_size`，前端不使用 `pageSize`。

后端分页模型可以直接复用：

```python
from typing import Annotated

from fastapi import Query

from application.apis.widgets.schema import ListWidgetReq, WidgetRes
from application.common.schema import BaseResponse, PageResult


@router.get("", response_model=BaseResponse[PageResult[WidgetRes]])
async def list_widgets(params: Annotated[ListWidgetReq, Query()]) -> object:
    response = await widget_service.list_widgets(params)
    return ResponseHelper.success(response)
```

其中 service 返回类型应明确声明为 `PageResult[WidgetRes]`，不得返回包含分页字段的字典。

## snake_case 强制规则

所有请求和响应 JSON 字段必须使用小写蛇形命名：

| 正确 | 错误 |
| --- | --- |
| `user_id` | `userId` |
| `created_at` | `createdAt` |
| `page_size` | `pageSize` |
| `page_size` | `PageSize` |

请求和响应模型必须放在对应 API 模块的 `schema.py` 中，继承 `SnakeCaseModel`，并使用 `Req / Res` 后缀：

```python
from application.common.schema import SnakeCaseModel


class CreateWidgetReq(SnakeCaseModel):
    widget_name: str
    display_order: int = 0


class CreateWidgetRes(SnakeCaseModel):
    widget_id: int
    widget_name: str
    created_at: str


class ListWidgetReq(SnakeCaseModel):
    page: int = 1
    page_size: int = 20


class WidgetRes(SnakeCaseModel):
    widget_id: int
    widget_name: str
```

该基类会拒绝非 snake_case 的字段声明，并使用 `extra="forbid"` 拒绝请求中未声明的键。因此发送 `widgetName` 不会被静默接受。

接口响应禁止传递字典：

```python
response = CreateWidgetRes(widget_id=1, widget_name="demo", created_at="2026-01-01")
ResponseHelper.success(response)  # 正确

ResponseHelper.success({"widget_id": 1})  # TypeError，禁止字典
```

`ResponseHelper.success/error` 只接受 Pydantic `BaseModel` 或 `None`。数组需要放进一个 `XxxRes`，分页数组统一使用 `PageResult[XxxRes]`。

## API 模块结构与命名

```text
application/apis/orders/
├── __init__.py
├── order_api.py
└── schema.py
```

例如 `create_order` 接口至少包含：

```python
# application/apis/orders/schema.py
from application.common.schema import SnakeCaseModel


class CreateOrderReq(SnakeCaseModel):
    product_id: int
    quantity: int


class CreateOrderRes(SnakeCaseModel):
    order_id: int
    order_status: str
```

路由必须直接接收和传递模型：

```python
@router.post("", response_model=BaseResponse[CreateOrderRes])
async def create_order(payload: CreateOrderReq) -> object:
    response = await order_service.create_order(payload)
    return ResponseHelper.success(response)
```

禁止以下写法：

```python
await order_service.create_order(payload.model_dump())  # 禁止传字典
return ResponseHelper.success({"order_id": 1})  # 禁止返回字典
```

## 路径和参数

- 路径使用小写短横线：`/audit-records`。
- 路径参数、查询参数、请求体和响应体字段使用 snake_case。
- 路由函数名使用 snake_case。
- 复数资源名优先，例如 `/widgets/{widget_id}`。
- 多个查询参数应组合为 `XxxReq`，通过 FastAPI 的 Pydantic Query Model 校验，不应手动拼接字典。

## 错误处理

可预期错误抛出 `HttpBusinessException`：

```python
from application.common.constants import HttpErrorCodeEnum
from application.common.exception import HttpBusinessException

raise HttpBusinessException(HttpErrorCodeEnum.NOT_FOUND, "组件不存在")
```

参数校验异常和未处理异常由全局处理器统一转换，路由中无需 `try/except Exception`。
