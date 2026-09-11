# orbai-fastapi-template

一个不包含具体业务逻辑的 FastAPI 工程脚手架。项目沿用参考工程的分层方式：路由、服务、通用组件、基础设施和中间件彼此分离，并提供统一响应、异常处理、请求上下文、配置加载和应用生命周期。

## 特性

- Python 3.12、FastAPI、Pydantic v2、uv
- 应用工厂，便于测试和多环境启动
- 纯 YAML 多环境配置、示例模板及环境变量占位符
- 可选 Tortoise ORM（MySQL/SQLite）及通用模型基类
- 可选异步 Redis 客户端、JSON 序列化、集合、计数器和分布式锁
- 统一响应结构与集中异常处理
- 请求级 `request_id` 上下文和响应头回传
- 每个 API 模块固定包含 `xxx_api.py + schema.py`
- 请求、响应使用 `XxxReq / XxxRes` Pydantic 模型并强制 snake_case
- 统一响应禁止传递 `dict`，接口与服务之间使用强类型对象
- 数据库和 Redis 默认关闭，按配置独立启用
- 示例与正式应用隔离，不携带业务代码
- pytest 与 Ruff 基础工程配置

## 快速开始

```bash
cd orbai_fastapi_template
cp config-example.yaml config.yaml
uv sync
uv run python main.py
```

打开：

- Swagger UI：<http://127.0.0.1:8000/api/docs>
- ReDoc：<http://127.0.0.1:8000/api/redoc>
- 健康检查：<http://127.0.0.1:8000/api/health>

监听地址、端口和自动重载由 `config.yaml` 的 `server` 节点控制。

## 常用命令

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run ruff format .
```

## 文档导航

- [快速上手](docs/getting-started.md)
- [架构与目录](docs/architecture.md)
- [开发指南](docs/development-guide.md)
- [API 与 snake_case 约定](docs/api-conventions.md)
- [配置说明](docs/configuration.md)
- [Tortoise ORM 与 Redis](docs/infrastructure.md)
- [使用示例](docs/examples.md)
- [部署指南](docs/deployment.md)

## 设计边界

`application/` 只包含可复用的通用能力、基础设施和系统运维接口。账号、权限、订单、支付等领域内容均未包含。新增业务时，以独立模块加入 `application/apis` 和 `application/service`，不要将领域规则写入 `common`、`core` 或中间件。
