# 开发指南

## 新增一个业务模块

以 `widgets` 为例，推荐结构：

```text
application/
├── apis/widgets/
│   ├── __init__.py
│   ├── widget_api.py
│   └── schema.py
└── service/widgets/
    ├── __init__.py
    └── widget_service.py
└── common/models/
    └── widget.py
```

职责边界：

- `schema.py`：该模块全部请求与响应 Pydantic 模型，使用 `XxxReq / XxxRes` 命名。
- `widget_api.py`：解析协议、调用服务、包装响应。
- `widget_service.py`：业务规则和用例编排，接收 Req/领域命令并返回 Res/领域结果，不接收字典或 HTTP 对象。
- `widget.py`：Tortoise 持久化模型；简单项目沿用参考工程放在 `common/models`，大型项目可按领域拆分并同步修改模型发现配置。

最后在 `application/apis/__init__.py` 注册模块 router。

每个包含 `*_api.py` 的目录都必须同时包含 `schema.py`，即使当前模块只有响应对象。结构测试会自动检查该约定。

## 强类型传递规则

- 请求体、查询参数组合必须定义为继承 `SnakeCaseModel` 的 `XxxReq`。
- 对外响应数据必须定义为 `XxxRes`，分页列表使用 `PageResult[XxxRes]`。
- 路由调用 service 时传递 Pydantic 对象，不得使用 `payload.model_dump()` 转成字典。
- service 返回 Pydantic/领域对象，不得返回匿名字典。
- `ResponseHelper.success/error` 只接受 Pydantic `BaseModel` 或 `None`，传入字典会抛出 `TypeError`。
- Tortoise 的 `.values()` 会返回字典，不得直接交给接口层；应显式转换成 `XxxRes`。

## 应用工厂与测试

测试可以直接创建独立应用：

```python
from fastapi.testclient import TestClient

from application import create_app


def test_health() -> None:
    with TestClient(create_app()) as client:
        response = client.get("/api/health")
    assert response.json()["code"] == 0
```

不要增加“仅供测试”的线上路由。服务层使用依赖注入后，测试可传入 fake repository。

## 生命周期

把连接创建和释放放在 `application/core/lifespan.py`：

```python
@asynccontextmanager
async def lifespan(_: FastAPI):
    await database.connect()
    try:
        yield
    finally:
        await database.disconnect()
```

生命周期只管理资源，不执行初始化角色、写入默认业务数据等领域动作。此类数据迁移应由独立脚本或迁移工具完成。

## 代码质量

提交前运行：

```bash
uv run ruff format .
uv run ruff check .
uv run pytest
```

新增接口至少覆盖：成功响应、请求校验失败、服务异常，以及 OpenAPI 中的 snake_case 字段。
