# YAML 配置指南

项目只支持 YAML 配置，不读取 Python 配置文件。完整模板位于根目录的 `config-example.yaml`。

## 第一次运行

先复制配置模板：

```bash
cp config-example.yaml config.yaml
```

再启动应用：

```bash
uv run python main.py
```

`config.yaml` 可能包含数据库密码、Redis 密码和应用密钥，因此已加入 `.gitignore`。应该提交 `config-example.yaml`，不应提交真实运行配置。

## 配置文件读取规则

加载逻辑位于 `application/common/config.py`，规则如下。

### 默认配置

未设置任何变量时读取项目根目录：

```text
config.yaml
```

### 按环境读取

设置 `ENV=local` 时读取：

```text
config-local.yaml
```

设置 `ENV=prod` 时读取：

```text
config-prod.yaml
```

例如：

```bash
cp config-example.yaml config-local.yaml
ENV=local uv run python main.py
```

每个环境文件都是完整配置，不会与 `config.yaml` 自动合并。

### 显式指定文件

`CONFIG_FILE` 的优先级高于 `ENV`，可以指定相对路径或绝对路径：

```bash
CONFIG_FILE=config-local.yaml uv run python main.py
```

```bash
CONFIG_FILE=/etc/orbai/config.yaml uv run python main.py
```

读取优先级为：

1. `CONFIG_FILE` 指定的 YAML 文件。
2. 设置 `ENV` 时的 `config-{ENV}.yaml`。
3. 默认的 `config.yaml`。

文件不存在、不是 `.yaml`/`.yml` 文件、YAML 根节点不是对象或字段校验失败时，应用会拒绝启动并给出错误信息。

## 环境变量占位符

YAML 字符串支持以下格式：

```text
${VARIABLE_NAME:default_value}
```

例如：

```yaml
secret_key: ${APP_SECRET_KEY:change-me-in-production}

database:
  host: ${MYSQL_HOST:localhost}
  port: ${MYSQL_PORT:3306}
  password: ${MYSQL_PASSWORD:}
```

规则：

- 设置了环境变量时，使用环境变量值。
- 未设置时，使用冒号后的默认值。
- `${MYSQL_PASSWORD:}` 的默认值是空字符串。
- 替换后的端口等字符串会由 Pydantic 转换并校验为对应类型。

示例：

```bash
APP_SECRET_KEY='production-secret' \
MYSQL_HOST='mysql.internal' \
MYSQL_PASSWORD='database-password' \
uv run python main.py
```

项目不会自动读取 `.env` 文件。环境变量可以由 Shell、IDE、Docker Compose、Kubernetes 或部署平台注入；所需变量及默认值统一记录在 `config-example.yaml` 中。

## 配置如何变成 Python 对象

应用导入：

```python
from application.common.config import config
```

配置经过以下流程：

```text
选择 YAML 文件
  → yaml.safe_load
  → 递归替换 ${ENV:default}
  → Setting.model_validate
  → 全局只读式使用 config
```

使用示例：

```python
from application.common.config import config

print(config.project_name)
print(config.server.port)
print(config.database.host)
print(config.redis.key_prefix)
```

业务代码不要自行再次读取 YAML，应统一使用已经校验过的 `config` 对象。

## 服务监听配置

服务监听地址、端口和开发自动重载全部由 YAML 控制：

```yaml
server:
  host: 0.0.0.0
  port: 8000
  reload: true
```

- `host`：Uvicorn 监听地址。`0.0.0.0` 表示监听所有网络接口。
- `port`：监听端口，必须为 `1` 到 `65535` 之间的整数。
- `reload`：是否监控文件变化并自动重启；生产环境必须设为 `false`。

`main.py` 通过统一配置对象读取这些值：

```python
uvicorn.run(
    "main:app",
    host=config.server.host,
    port=config.server.port,
    reload=config.server.reload,
)
```

如确实需要由部署环境决定端口，也应在 YAML 中显式使用占位符：

```yaml
server:
  host: ${APP_HOST:0.0.0.0}
  port: ${APP_PORT:8000}
  reload: ${APP_RELOAD:false}
```

这样配置入口仍然只有 YAML，环境变量仅负责替换值。

## 新增一个简单配置项

例如新增上传文件大小限制 `upload_max_size_mb`。

第一步，在 `config-example.yaml` 增加完整示例值：

```yaml
upload_max_size_mb: ${UPLOAD_MAX_SIZE_MB:20}
```

第二步，在 `Setting` 增加对应字段：

```python
class Setting(BaseModel):
    # 已有字段省略
    upload_max_size_mb: int = 20
```

第三步，同步所有实际环境配置文件，或者确保它在 Pydantic 模型中有安全默认值。

第四步，通过统一配置对象读取：

```python
from application.common.config import config

max_bytes = config.upload_max_size_mb * 1024 * 1024
```

最后增加配置解析测试，确保环境变量字符串能正确转换为目标类型。

## 新增一组嵌套配置

例如增加对象存储配置。

第一步，在 `config-example.yaml` 增加：

```yaml
object_storage:
  enabled: false
  endpoint: ${OBJECT_STORAGE_ENDPOINT:http://127.0.0.1:9000}
  bucket_name: ${OBJECT_STORAGE_BUCKET:uploads}
  access_key: ${OBJECT_STORAGE_ACCESS_KEY:}
  secret_key: ${OBJECT_STORAGE_SECRET_KEY:}
```

第二步，在 `application/common/config.py` 定义模型：

```python
class ObjectStorageConfig(BaseModel):
    enabled: bool = False
    endpoint: str
    bucket_name: str
    access_key: str = ""
    secret_key: str = ""
```

第三步，加入顶层 `Setting`：

```python
class Setting(BaseModel):
    # 已有字段省略
    object_storage: ObjectStorageConfig
```

第四步，同步 `config.yaml`、`config-local.yaml`、`config-prod.yaml` 等实际配置。

第五步，使用：

```python
endpoint = config.object_storage.endpoint
```

配置字段和最终对外请求、响应字段一样，统一使用 snake_case。

## 数据库配置

MySQL 示例：

```yaml
database:
  enabled: true
  backend: mysql
  host: ${MYSQL_HOST:localhost}
  port: ${MYSQL_PORT:3306}
  user: ${MYSQL_USER:root}
  password: ${MYSQL_PASSWORD:}
  name: ${MYSQL_DATABASE:orbai_template}
  charset: utf8mb4
  minsize: ${MYSQL_MINSIZE:1}
  maxsize: ${MYSQL_MAXSIZE:10}
  echo: false
  auto_generate_schema: false
  sqlite_path: data/app.sqlite3
  use_tz: false
  timezone: Asia/Shanghai
```

本地 SQLite 示例：

```yaml
database:
  enabled: true
  backend: sqlite
  sqlite_path: data/app.sqlite3
  auto_generate_schema: true
```

使用 SQLite 时仍需保留 `database` 中其他配置，或者使用模型中提供的默认值。生产环境应保持 `auto_generate_schema: false` 并使用迁移工具。

## Redis 配置

```yaml
redis:
  enabled: true
  fail_fast: false
  host: ${REDIS_HOST:localhost}
  port: ${REDIS_PORT:6379}
  password: ${REDIS_PASSWORD:}
  db: ${REDIS_DB:0}
  max_connections: ${REDIS_MAX_CONNECTIONS:20}
  socket_connect_timeout: 3.0
  socket_timeout: 3.0
  key_prefix: ${REDIS_KEY_PREFIX:orbai}
```

- `fail_fast: false`：Redis 连接失败时记录警告并继续启动。
- `fail_fast: true`：Redis 连接失败时终止应用启动。
- `key_prefix`：所有 Redis 键的统一命名空间。

## 生产配置建议

生产环境建议创建 `config-prod.yaml`：

```yaml
debug_mode: false

server:
  host: 0.0.0.0
  port: 8000
  reload: false

doc:
  enable_docs: false
  enable_redoc: false

cors:
  allow_origins:
    - https://example.com
  allow_credentials: true
  allow_methods:
    - GET
    - POST
    - PUT
    - DELETE
  allow_headers:
    - authorization
    - content-type
    - x-request-id
```

以上片段需要合并到一份完整的 `config-prod.yaml` 中。密钥和密码继续使用环境变量占位符，不要写入 YAML 明文。
