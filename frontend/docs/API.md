# 接口、Mock 与联调

## 环境变量

```dotenv
VITE_API_BASE_URL=/api
VITE_API_TIMEOUT=10000
VITE_ENABLE_MOCK=true
```

仓库只提交 `.env.example`。开发前复制为 `.env.development`，生产构建前复制为 `.env.production`，再填写对应环境配置。复制后的文件已被 Git 忽略，不应提交。修改后需重启开发服务器或重新构建。所有 `VITE_` 变量都会暴露给浏览器，因此只能存放公开配置。

## 新增接口

```ts
import { http } from '@/plugin/axios'
import type { PageResult } from '@/common/types/api'

export interface UserItem {
  id: number
  name: string
}

export function getUserList(params: { page: number }) {
  return http.get<PageResult<UserItem>>('/users', params)
}

export function createUser(data: { name: string }) {
  return http.post<UserItem>('/users', data)
}
```

页面只调用 `getUserList`，不直接使用 Axios。这样可以统一认证、超时、错误处理和响应解包，并使页面更容易测试。

模板约定业务请求只使用 GET 和 POST：查询使用 `http.get`，提交、新增或其他写操作统一使用 `http.post`。`http` 不提供 PUT 和 DELETE。

## 请求与响应拦截器

请求和响应拦截器位于 `src/plugin/axios/interceptors.ts`，负责 Token 注入、业务错误判断和网络错误提示。`src/plugin/axios/index.ts` 只创建 Axios 实例、集成拦截器并导出 `http.get/http.post`。

## 响应约定

模板默认后端返回：

```json
{ "code": 0, "message": "success", "data": {} }
```

如果实际后端使用其他结构，只需调整 `src/common/types/api.ts` 和 `src/plugin/axios/interceptors.ts`，不要让每个页面自行判断响应码。

## Mock 策略

`src/common/apis/exampleApi.ts` 展示了最轻量的本地 Mock：环境开关打开时返回静态数据，关闭时请求真实接口。复杂项目可换成 Mock Service Worker 或独立 Mock 服务，但生产构建必须关闭 Mock。

## 代理与跨域

本地联调时可在 `vite.config.ts` 开启 `/api` 代理。生产环境应由网关或 Nginx 将 `/api` 转发到后端，或者由后端正确配置 CORS。

## 鉴权接入

模板只提供 Bearer Token 注入位置，没有实现登录、刷新 Token 或权限业务。接入时需要明确：Token 存储策略、过期刷新并发控制、401 退出流程、跨标签页同步，以及 XSS/CSRF 风险。不要直接照搬不匹配的旧项目认证逻辑。
