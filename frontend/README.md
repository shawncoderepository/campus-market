# orbai_vue_template

一个从实际管理端工程中提炼、已移除全部具体业务逻辑的 Vue 3 中后台脚手架。模板保留了路由、状态管理、请求封装、UI 主题、响应式布局和常用组件示例，适合作为新项目的起点。

## 技术栈

- Vue 3 + Composition API + `<script setup>`
- TypeScript 严格模式
- Vite 7
- Ant Design Vue 4
- Ant Design Vue 组件按页面显式导入，依赖关系清晰可控
- Vue Router 4
- Pinia 3
- Axios
- Tailwind CSS 3（可选，与普通 CSS 可同时使用）

## 快速开始

最低要求 Node.js `>= 24.18.0`，团队推荐并默认使用 `.nvmrc` 指定的 Node.js 24 LTS。使用 nvm 时可执行：

```bash
nvm install
nvm use
```

```bash
cd orbai_vue_template
npm install
cp .env.example .env.development
npm run dev
```

浏览器访问 `http://localhost:5173`。提交代码前执行：

```bash
npm run build
```

## 模板内置内容

- 中后台侧栏、顶栏和内容区布局
- 工作台及 404 页面
- 表单、表格、分页、标签、确认操作和反馈组件示例
- Pinia state/getter/action 示例
- Axios 实例、拦截器、统一响应类型与领域 API 示例
- 开发环境本地 Mock，启动时无需后端
- 路由懒加载、页面标题与切换动画
- `views/layouts` 与 `views/pages/<页面包>/index.vue` 的统一页面结构
- 完整的中文代码注释和开发文档

## 文档导航

- [开发指南](docs/DEVELOPMENT.md)：从新增一个功能到构建发布的完整流程
- [目录规范](docs/ARCHITECTURE.md)：目录职责、依赖方向和编码约定
- [组件开发](docs/COMPONENTS.md)：组件调用示例与自定义组件规范
- [接口联调](docs/API.md)：环境变量、请求封装、Mock 与错误处理
- [部署指南](docs/DEPLOYMENT.md)：构建、子路径和 Nginx 配置

## 新项目初始化清单

1. 修改 `package.json` 的 `name`、版本及项目说明。
2. 将 `.env.example` 复制为 `.env.development` 或 `.env.production`，再配置标题、接口地址、Mock 开关与路由基础路径。
3. 在 `src/plugin/router/index.ts` 中替换示例路由。
4. 按业务域新增 `views/pages/<页面包>/index.vue`、`common/apis`、`stores` 文件；在页面中显式导入所用 UI 组件。
5. 替换主题色、品牌标识和浏览器描述。
6. 接入真实鉴权后关闭 `VITE_ENABLE_MOCK`。
7. 删除不需要的示例页面，但建议保留作为团队用法参考。

## 安全说明

前端环境变量会进入浏览器产物。不得在 `.env` 或源代码中放置数据库密码、私钥、云平台密钥等服务端秘密。Token 示例仅展示接入位置，正式项目应结合自身认证方案完善过期、刷新和退出流程。
