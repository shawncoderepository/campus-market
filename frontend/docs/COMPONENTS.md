# 组件开发与调用

运行项目后访问 `/components`，可直接体验表单、表格、反馈组件和三个自定义组件；访问 `/order` 可查看 `pages/order/index.vue` 页面包的组合示例。

## PageHeader：Props 与具名插槽

```vue
<PageHeader title="用户列表" description="管理系统用户">
  <template #extra>
    <a-button type="primary">新增用户</a-button>
  </template>
</PageHeader>
```

适合每个页面统一标题和操作区。文字通过 Props 传入，调用方自定义内容通过 `extra` 插槽传入。

## StatusBadge：派生展示

```vue
<StatusBadge status="enabled" />
<StatusBadge status="pending" />
```

组件内部用 `computed` 将稳定的业务枚举映射为颜色和文案。新增状态时应同时补充 Props 联合类型与映射项。

## ConfirmAction：事件回调

```vue
<ConfirmAction danger title="确定删除吗？" @confirm="removeItem" />
```

危险操作统一增加二次确认，组件只发出 `confirm` 事件，不直接执行删除请求。

## Ant Design Vue 常用调用

```vue
<a-form :model="form" layout="vertical">
  <a-form-item label="名称" name="name">
    <a-input v-model:value="form.name" />
  </a-form-item>
</a-form>

<a-table :columns="columns" :data-source="rows">
  <template #bodyCell="{ column, record }">
    <a-tag v-if="column.key === 'status'">{{ record.status }}</a-tag>
  </template>
</a-table>
```

注意 Ant Design Vue 的双向绑定通常是 `v-model:value`、`v-model:checked` 或 `v-model:open`，具体名称以组件 API 为准。

## 公共组件的边界

只有被两个以上领域复用、API 稳定且不包含特定业务流程的组件才放入 `components/common`。仅被一个页面使用的组件应放在 `views/pages/<页面包>/components`，避免公共目录变成难以维护的组件仓库。
