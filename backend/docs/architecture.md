# 架构与目录

## 目录结构

```text
orbai_fastapi_template/
├── application/
│   ├── apis/                    # HTTP 路由及 DTO 编排
│   │   └── system/              # 一个完整的 API 模块
│   │       ├── __init__.py      # 导出模块 router
│   │       ├── system_api.py    # 路由定义与调用编排
│   │       └── schema.py        # XxxReq / XxxRes 请求响应模型
│   ├── common/
│   │   ├── constants/           # 全局枚举和错误码
│   │   ├── exception/           # 业务异常类型与全局处理器
│   │   ├── helper/              # 统一响应等无状态工具
│   │   ├── models/              # Tortoise 通用抽象模型
│   │   └── schema/              # DTO 基类和公共响应模型
│   ├── core/                    # 日志、生命周期、数据库和 Redis
│   ├── middleware/              # HTTP 中间件和请求上下文
│   └── service/                 # 新业务服务的放置位置
├── docs/                        # 项目文档
├── tests/                       # 自动化测试
├── config-example.yaml          # 受版本控制的完整 YAML 配置模板
├── config.yaml                  # 本地运行配置（复制生成，Git 忽略）
├── main.py                      # 本地启动入口
└── pyproject.toml               # 依赖及工具配置
```

## 调用方向

```text
HTTP 请求
  → middleware
  → apis/schema.py（Pydantic 请求校验）
  → apis/xxx_api.py（协议转换与调用编排）
  → service（接收/返回强类型对象）
  → repository / 外部基础设施（按需新增）
  → ResponseHelper
  → HTTP 响应
```

依赖方向应保持从外向内：路由可以调用服务，服务不应依赖 FastAPI 的 `Request` 或 `Response`。API 与服务之间不得传递 `dict`，应传递模块 `schema.py` 中定义的 Pydantic 模型。`common` 只能放跨领域、稳定且无业务含义的代码。

## 保留与删除的内容

基于参考工程保留了：

- `application/apis`、`service`、`common`、`core`、`middleware` 分层
- 配置文件优先级和环境变量替换方式
- 生命周期、统一响应、统一异常处理、请求上下文
- uv、pytest、Ruff 工程化入口

脚手架明确删除了账号、角色、权限、用户资料、验证码、仪表盘、系统协议、微信小程序等业务模型和逻辑。Tortoise ORM 与 Redis 已作为通用基础设施集成，但默认关闭，避免空项目启动依赖外部环境。

## 扩展基础设施

数据库和 Redis 已在 `application/core` 提供生命周期管理。消息队列等其他基础设施可按相同方式扩展。具体表模型、缓存键和消息内容仍属于业务：

1. 在 `application/core` 创建连接客户端。
2. 在 `lifespan` 中建立并关闭连接。
3. 在领域模块内创建 model/repository，隐藏具体存储实现。
4. 通过依赖注入把 repository 交给 service。
5. 测试中替换 repository，而不是连接真实外部服务。
