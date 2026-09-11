# Tortoise ORM 与 Redis

## 生命周期

`application/core/lifespan.py` 在 FastAPI 启动阶段依次初始化 Tortoise ORM 和 Redis，在关闭阶段逆向释放资源。连接是否启用完全由配置控制：

```text
FastAPI startup
  → connect_database()
  → redis_client.connect()
  → serve requests
  → redis_client.close()
  → disconnect_database()
```

数据库启用后连接失败会终止启动。Redis 是否终止启动由 `redis.fail_fast` 控制。

## Tortoise ORM

数据库模块位于 `application/core/database.py`，支持：

- MySQL：`tortoise.backends.mysql` + `aiomysql`
- SQLite：`tortoise.backends.sqlite` + `aiosqlite`
- 连接池参数
- 时区参数
- 开发环境安全建表
- 应用关闭时释放全部连接

通用抽象模型：

- `TimestampMixin`：`created_at`、`updated_at`
- `OrmBaseModel`：自增 bigint `id` 和时间字段

正式业务模型需要在 `application/common/models/__init__.py` 中导入。`auto_generate_schema` 只适合本地开发和测试；生产环境应使用 Aerich 或团队选定的迁移流程。

### 本地 SQLite 配置

复制示例配置：

```bash
cp config-example.yaml config-local.yaml
```

编辑 `config-local.yaml`：

```yaml
database:
  enabled: true
  backend: sqlite
  sqlite_path: data/app.sqlite3
  auto_generate_schema: true
```

文件中的其他顶层配置仍需保留，然后按环境名称启动：

```bash
ENV=local uv run python main.py
```

## Redis 工具类

`application/core/redis_client.py` 提供一个生命周期托管的全局 `redis_client`：

| 方法 | 用途 |
| --- | --- |
| `set` / `get` | 字符串或 JSON 值读写 |
| `delete` | 批量删除键 |
| `incr` | 原子计数 |
| `expire` | 设置有效期 |
| `exists` | 判断键是否存在 |
| `sadd` / `srem` | 集合成员增删 |
| `smembers` / `sismember` | 集合查询 |
| `keys` | 小型键空间的模式查询 |
| `scan_iter` | 生产环境渐进扫描 |
| `lock` | redis-py 异步分布式锁 |

`dict`、`list`、`set`、布尔值和空值会序列化为 JSON；读取时自动还原。所有键统一添加配置的 `key_prefix`，避免多个应用共享 Redis 时冲突。

Redis 未连接时调用工具方法会抛出清晰的 `RuntimeError`。不要绕过生命周期在模块导入阶段执行 Redis 命令。

## 测试建议

- 单元测试：为 repository 或缓存接口提供 fake，不依赖真实 MySQL/Redis。
- ORM 集成测试：使用临时 SQLite 数据库并在测试结束后关闭连接。
- Redis 集成测试：使用独立测试 DB 或临时容器，并为 `key_prefix` 加测试运行标识。
- 不要让测试连接开发或生产数据库。
