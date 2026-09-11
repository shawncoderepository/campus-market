# 目录与架构规范

```text
orbai_vue_template/
├── docs/                  # 团队开发文档
├── src/
│   ├── common/
│   │   ├── apis/           # 按领域拆分的 API 函数
│   │   └── types/         # 跨模块通用类型
│   ├── components/common/ # 跨领域通用组件
│   ├── plugin/
│   │   ├── axios/          # Axios 实例及独立请求/响应拦截器
│   │   ├── pinia/          # Pinia 实例与注册函数
│   │   ├── router/         # 路由表、守卫与注册函数
│   │   └── index.ts        # 插件统一注册入口
│   ├── stores/            # Pinia 全局/领域状态
│   ├── styles/            # 全局样式与设计令牌
│   ├── views/
│   │   ├── layouts/       # 布局包：导航壳、空白布局等
│   │   │   └── default/
│   │   │       └── index.vue
│   │   └── pages/         # 页面包：每个目录代表一个页面领域
│   │       ├── home/
│   │       │   └── index.vue
│   │       └── order/
│   │           └── index.vue
│   ├── App.vue            # 根组件、全局主题
│   └── main.ts            # 应用启动与插件注册
├── .env.example           # 环境变量示例；复制后再按环境配置
└── vite.config.ts         # 构建和开发服务器配置
```

## 依赖方向

推荐依赖方向为：`views/pages → components/stores/common/apis → plugin/axios/common/types`。布局只负责页面骨架和导航；API 层不引用页面，通用组件不引用具体业务页面，Store 不操作 DOM。保持单向依赖能减少循环引用，也便于单独测试和替换实现。

## 插件注册规则

- Pinia、Axios、Vue Router 等基础设施统一放在 `src/plugin`。
- `plugin/pinia` 与 `plugin/router` 分别导出 `setup(app)`，由 `plugin/index.ts` 统一注册。
- Axios 不是 Vue UI 插件，不挂载到全局属性；领域 API 从 `plugin/axios` 显式导入 `http`，且只使用 `http.get/http.post`。
- `main.ts` 只创建应用、调用统一插件入口并挂载，不分散注册逻辑。

## 页面包与布局包

- 页面统一放在 `src/views/pages/<package>/index.vue`，例如 `home/index.vue`、`order/index.vue`。
- `<package>` 使用小写 kebab-case，表达页面领域，不使用 `Page1` 等无语义名称。
- 页面专属组件放在该页面包的 `components/`，不要提前提升为全局组件。
- 布局统一放在 `src/views/layouts/<layout>/index.vue`，由父路由引用，再通过 `<RouterView />` 渲染子页面。
- 路由必须使用动态 `import()` 指向页面包入口，保持按页面拆包。

## 状态应该放在哪里

- 输入框展开状态、弹窗开关：当前组件的 `ref`。
- 父子组件共享：Props、Emits 或 `v-model`。
- 同一路由下深层组件共享：必要时使用 `provide/inject`。
- 跨页面用户信息、权限、偏好设置：Pinia。
- 后端列表数据：默认由页面请求并持有；只有确实需要跨页面缓存时才进入 Pinia。

## 命名规则

- Vue 组件：PascalCase，例如 `UserTable.vue`；页面和布局入口统一为 `index.vue`。
- 组合式函数：`use` 开头，例如 `usePagination.ts`。
- Store：`useXxxStore`，文件用领域名，例如 `user.ts`。
- API 函数：动词开头，例如 `getUserList`、`createUser`。
- 类型：PascalCase，例如 `UserQuery`、`PageResult<T>`。

## 新增鉴权的建议位置

Token 注入和响应处理放在 `plugin/axios/interceptors.ts`；用户状态放在单独的用户 Store；访问控制放在 `plugin/router` 的 `beforeEach` 守卫；按钮级权限封装为组合式函数或指令。四者职责应分离，不把认证逻辑散落到每个页面。
