# 部署指南

## 生产启动

生产环境首先在 `config-prod.yaml` 中关闭自动重载并设置监听端口：

```yaml
server:
  host: 0.0.0.0
  port: 8000
  reload: false
```

单进程或由容器平台管理副本时直接启动：

```bash
ENV=prod uv run python main.py
```

如果需要在单个容器中使用多个 worker，可以直接运行 Uvicorn；此时命令行监听参数会覆盖 YAML 的 `server` 参数：

```bash
uv run uvicorn application:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 2 \
  --proxy-headers \
  --forwarded-allow-ips='127.0.0.1'
```

不要在多个 worker 之间共享进程内可变状态。数据库连接池、缓存客户端等应由每个 worker 在生命周期中独立创建。

## 反向代理

反向代理至少应转发：

- `Host`
- `X-Forwarded-For`
- `X-Forwarded-Proto`
- `X-Request-Id`（如果网关生成）

只有在可信代理后方才启用代理头，并明确配置可信代理 IP，避免伪造客户端地址。

## 健康检查

容器或负载均衡器使用：

```text
GET /api/health
```

当前健康检查仅表示进程可响应。接入数据库或缓存后，可按系统需求增加 readiness 检查，但不要在每次 liveness 检查中执行昂贵查询。

## 发布前清单

- `debug_mode` 已关闭。
- Swagger/ReDoc 按安全策略关闭或受控访问。
- `APP_SECRET_KEY` 已从密钥管理服务注入。
- CORS 不再使用通配来源。
- 日志不包含密钥、令牌和个人敏感信息。
- 已运行 Ruff、pytest 和依赖安全扫描。
- 连接池大小与 worker 数量一并评估。
