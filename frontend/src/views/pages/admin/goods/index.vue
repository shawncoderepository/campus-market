<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { Card as ACard, Table as ATable, Tag as ATag } from 'ant-design-vue'
import { getGoodsList } from '@/common/apis/goodsApi'
import type { GoodsItem } from '@/common/types/business'

const loading = ref(false)
const list = ref<GoodsItem[]>([])
const total = ref(0)
const page = ref(1)

const columns = [
  { title: 'ID', dataIndex: 'id', width: 70 },
  { title: '标题', dataIndex: 'title', ellipsis: true },
  { title: '分类', dataIndex: 'category_name', width: 110 },
  { title: '售价', dataIndex: 'sell_price', width: 90 },
  { title: '卖家', dataIndex: 'seller_nickname', width: 120 },
  { title: '浏览', dataIndex: 'view_count', width: 80 },
  { title: '状态', dataIndex: 'status', width: 90 },
]

const statusTag = (s: number) => ({ 1: { text: '在售', color: 'green' }, 2: { text: '已售', color: 'blue' }, 3: { text: '已下架', color: 'default' } })[s]

async function load(p = 1) {
  loading.value = true
  try {
    page.value = p
    const res = await getGoodsList({ page: p, page_size: 20 })
    list.value = res.list
    total.value = res.total
  } catch { /* 已提示 */ } finally {
    loading.value = false
  }
}

onMounted(() => load())
</script>

<template>
  <a-card title="商品管理">
    <a-table
      :columns="columns"
      :data-source="list"
      :loading="loading"
      :pagination="{ current: page, pageSize: 20, total, onChange: load }"
      row-key="id"
      size="middle"
    >
      <template #bodyCell="{ column, record }">
        <template v-if="column.dataIndex === 'sell_price'">¥{{ record.sell_price }}</template>
        <template v-else-if="column.dataIndex === 'status'">
          <a-tag :color="statusTag(record.status)?.color">{{ statusTag(record.status)?.text }}</a-tag>
        </template>
      </template>
    </a-table>
  </a-card>
</template>
