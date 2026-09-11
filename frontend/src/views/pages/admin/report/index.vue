<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { Card as ACard, Table as ATable, Tag as ATag } from 'ant-design-vue'
import { getMyReports, type Report } from '@/common/apis/reportApi'

const loading = ref(false)
const list = ref<Report[]>([])
const total = ref(0)
const page = ref(1)

const columns = [
  { title: 'ID', dataIndex: 'id', width: 70 },
  { title: '举报人', dataIndex: 'reporter_nickname', width: 120 },
  { title: '被举报商品', dataIndex: 'product_title', ellipsis: true },
  { title: '原因', dataIndex: 'reason', ellipsis: true },
  { title: '状态', dataIndex: 'status', width: 90 },
]

const statusMap: Record<number, { text: string; color: string }> = {
  1: { text: '待处理', color: 'gold' },
  2: { text: '已处理', color: 'green' },
  3: { text: '已驳回', color: 'default' },
}

async function load(p = 1) {
  loading.value = true
  try {
    page.value = p
    const res = await getMyReports({ page: p, page_size: 20 })
    list.value = res.list
    total.value = res.total
  } catch { /* 已提示 */ } finally {
    loading.value = false
  }
}

onMounted(() => load())
</script>

<template>
  <a-card title="举报处理">
    <a-table
      :columns="columns"
      :data-source="list"
      :loading="loading"
      :pagination="{ current: page, pageSize: 20, total, onChange: load }"
      row-key="id"
      size="middle"
    >
      <template #bodyCell="{ column, record }">
        <template v-if="column.dataIndex === 'status'">
          <a-tag :color="statusMap[record.status]?.color">{{ statusMap[record.status]?.text }}</a-tag>
        </template>
      </template>
    </a-table>
  </a-card>
</template>
