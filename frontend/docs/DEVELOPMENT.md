# 开发指南

## 1. 环境准备

安装 Node.js 24.18 或更高的 24.x LTS 版本。项目提供 `.nvmrc`，使用 nvm 时执行 `nvm install && nvm use` 即可切换。进入项目后执行 `npm install`。本地开发使用 `npm run dev`，类型检查使用 `npm run type-check`，生产构建使用 `npm run build`。

建议提交锁文件 `package-lock.json`，确保团队与 CI 安装完全相同的依赖版本。

## 2. 开发一个新功能

以“通知管理”为例，推荐按以下顺序工作：

1. 在 `src/common/types` 定义跨模块使用的数据类型；只在单一模块使用的类型可就近定义。
2. 新建 `src/common/apis/notificationApi.ts`，封装查询、新增、修改、删除方法。
3. 如有跨页面状态，新建 `src/stores/notification.ts`；页面局部状态留在页面组件中。
4. 新建 `src/views/pages/notification/index.vue`，页面包统一使用语义化目录名，入口统一命名为 `index.vue`。
5. 仅该页面使用的组件放在 `src/views/pages/notification/components`，跨页面复用的组件放在 `src/components/common`。
6. 在 `src/plugin/router/index.ts` 注册懒加载路由，并在布局菜单中增加入口。
7. 覆盖加载中、空数据、请求失败、无权限和移动端窄屏场景。
8. 执行 `npm run build`，确认类型检查和生产构建通过。

页面包示例：

```text
src/views/pages/
├── home/
│   └── index.vue
├── order/
│   ├── components/       # 可选，仅订单页面使用的组件
│   └── index.vue
└── user/
    └── index.vue
```

布局统一放在 `src/views/layouts/<布局名称>/index.vue`。默认后台布局为 `views/layouts/default/index.vue`，登录、空白页等不同结构可新增独立布局包。

## 3. Vue 代码约定

- 统一使用 Composition API 与 `<script setup lang="ts">`。
- Ant Design Vue 组件必须在使用它的 Vue 文件中显式导入，不使用自动注册。
- Props 和 Emits 必须声明 TypeScript 类型，不使用无类型的 `any`。
- 派生数据使用 `computed`，有副作用的操作使用函数或 `watch`。
- 页面负责流程编排，通用组件负责展示和交互，不在组件内偷偷发起不相关请求。
- 事件名表达已经发生的动作，例如 `saved`、`confirm`；布尔值以 `is`、`has`、`can` 开头。
- 异步请求必须包含 loading，并在适当位置呈现错误与空状态。

## 4. 样式约定

全局变量和页面通用样式位于 `src/styles/index.css`。组件私有样式使用 `scoped`。简单布局可使用 Tailwind 工具类，复杂组件建议使用语义化类名，避免超长工具类降低可读性。

Ant Design Vue 主题在 `src/App.vue` 中集中设置。不要在多个页面重复覆盖同一主题变量。

## 5. 分支与提交建议

- 功能分支：`feat/notification-list`
- 修复分支：`fix/request-timeout`
- 提交示例：`feat: 新增通知列表筛选`
- 每次提交只包含一个清晰目的，不提交 `node_modules`、`dist`、本地密钥或编辑器缓存。

## 6. 完成定义

功能只有在以下条件全部满足时才算完成：需求路径可操作；异常路径有反馈；类型检查和构建通过；没有真实密钥与调试日志；新增公共能力已有中文注释或文档；在常用桌面与移动宽度下没有明显布局问题。
