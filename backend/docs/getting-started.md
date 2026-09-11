# 快速上手

## 环境要求

- Python 3.12 或 3.13
- uv（推荐）

安装 uv 可参考其官方文档；已有 uv 时直接执行：

```bash
uv sync
```

`uv sync` 会创建 `.venv` 并安装运行与开发依赖。

## 启动开发服务器

```bash
cp config-example.yaml config.yaml
uv run python main.py
```

`config.yaml` 是必需的运行配置，且已加入 `.gitignore`。所有可用配置项都可以从 `config-example.yaml` 复制，不要把包含真实密码的 `config.yaml` 提交到仓库。

默认监听 `0.0.0.0:8000`，自动重载开启。监听参数统一在 `config.yaml` 中设置：

```yaml
server:
  host: 0.0.0.0
  port: 8000
  reload: true
```

修改端口后重新启动应用，例如：

```yaml
server:
  host: 0.0.0.0
  port: 9000
  reload: false
```

`port` 必须是 `1` 到 `65535` 之间的整数。项目不会自动读取 `.env`；其他 YAML 环境变量占位符由容器、IDE、Shell 或部署平台注入。

## 验证服务

```bash
curl http://127.0.0.1:8000/api/health
```

响应：

```json
{
  "code": 0,
  "message": "成功",
  "data": {
    "service_name": "orbai-fastapi-template",
    "service_status": "ok"
  }
}
```

## 测试与检查

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
```
