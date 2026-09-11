# 构建与部署

## 构建

```bash
cp .env.example .env.production
# 编辑 .env.production，关闭 Mock 并填写生产接口地址
npm ci
npm run build
```

产物输出到 `dist/`。部署前可执行 `npm run preview` 在本地预览生产构建。

## Nginx 示例

Vue Router 使用 history 模式，未知前端路由必须回退到 `index.html`：

```nginx
server {
    listen 80;
    server_name example.com;
    root /var/www/orbai_vue_template/dist;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://backend:8080/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 部署到子路径

如果站点部署在 `https://example.com/admin/`，将两个环境保持一致：

```dotenv
VITE_ROUTE_BASE=/admin/
```

Vite 的资源 `base` 与 Vue Router 的 history base 已共用该变量。Nginx 的回退路径也应改成 `/admin/index.html`。

## 发布检查

- `npm run build` 已通过。
- 生产环境 `VITE_ENABLE_MOCK=false`。
- 接口地址、基础路径与 HTTPS 配置正确。
- 服务器对 history 路由配置了回退。
- 未上传 `.env.local`、日志、源码映射或任何密钥。
- 静态资源设置合理缓存，`index.html` 不使用长期强缓存。
