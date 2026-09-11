<script setup lang="ts">
import { onMounted, ref } from 'vue'
import {
  Alert as AAlert,
  Avatar as AAvatar,
  Button as AButton,
  Card as ACard,
  List as AList,
  ListItem as AListItem,
  ListItemMeta as AListItemMeta,
  Skeleton as ASkeleton,
  TypographyParagraph as ATypographyParagraph,
  TypographyText as ATypographyText,
  message,
} from 'ant-design-vue'
import { ReloadOutlined } from '@ant-design/icons-vue'
import PageHeader from '@/components/common/PageHeader.vue'
import StatusBadge from '@/components/common/StatusBadge.vue'
import { createExampleItem, getExampleList, type ExampleItem } from '@/common/apis/exampleApi'

const loading = ref(false)
const posting = ref(false)
const errorText = ref('')
const rows = ref<ExampleItem[]>([])
const isMockEnabled = import.meta.env.VITE_ENABLE_MOCK === 'true'

async function loadData() {
  loading.value = true
  errorText.value = ''
  try {
    const result = await getExampleList()
    rows.value = result.list
  } catch (error) {
    errorText.value = error instanceof Error ? error.message : '加载失败'
  } finally {
    loading.value = false
  }
}

async function createData() {
  posting.value = true
  errorText.value = ''
  try {
    const item = await createExampleItem({ name: `POST 示例 ${rows.value.length + 1}` })
    rows.value.unshift(item)
    message.success('POST 示例调用成功')
  } catch (error) {
    errorText.value = error instanceof Error ? error.message : '新增失败'
  } finally {
    posting.value = false
  }
}

onMounted(loadData)
</script>

<template>
  <main class="page-container">
    <PageHeader title="请求层示例" description="演示页面如何通过领域 API 模块获取数据，并处理加载与异常状态。">
      <template #extra>
        <a-button :loading="loading" @click="loadData"><ReloadOutlined />GET 列表</a-button>
        <a-button type="primary" :loading="posting" @click="createData">POST 新增</a-button>
      </template>
    </PageHeader>

    <a-alert
      v-if="isMockEnabled"
      type="info"
      show-icon
      message="开发环境默认启用本地 Mock"
      description="关闭 Mock 后，两个按钮会分别请求 GET /api/examples 与 POST /api/examples。"
    />
    <a-alert v-if="errorText" type="error" show-icon :message="errorText" />

    <a-card :bordered="false">
      <a-skeleton :loading="loading" active>
        <a-list :data-source="rows" item-layout="horizontal">
          <template #renderItem="{ item }">
            <a-list-item>
              <a-list-item-meta :description="`创建时间：${item.createdAt}`">
                <template #title>{{ item.name }}</template>
                <template #avatar><a-avatar>{{ item.id }}</a-avatar></template>
              </a-list-item-meta>
              <StatusBadge :status="item.status" />
            </a-list-item>
          </template>
        </a-list>
      </a-skeleton>
    </a-card>

    <a-card title="推荐调用链" :bordered="false">
      <a-typography-paragraph>
        页面组件 → <a-typography-text code>common/apis/exampleApi.ts</a-typography-text>
        → <a-typography-text code>plugin/axios/index.ts</a-typography-text> → 后端接口
      </a-typography-paragraph>
    </a-card>
  </main>
</template>
