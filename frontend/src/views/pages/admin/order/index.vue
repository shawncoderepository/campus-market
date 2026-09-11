<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { Card as ACard, Table as ATable, Tag as ATag } from 'ant-design-vue'
import { getMyOrders } from '@/common/apis/orderApi'
import type { Order } from '@/common/types/business'

const loading = ref(false)
const list = ref<Order[]>([])
const total = ref(0)
const page = ref(1)

const columns = [
  { title: '订单号', dataIndex: 'order_no', ellipsis: true },
  { title: '商品', dataIndex: 'product_title', ellipsis: true },
  { title: '买家', dataIndex: 'buyer_nickname', width: 110 },
  { title: '卖家', dataIndex: 'seller_nickname', width: 110 },
  { title: '成交价', dataIndex: 'deal_price', width: 90 },
  { title: '状态', dataIndex: 'status', width: 90 },
]

const statusMap: Record<number, { text: string; color: string }> = {
  1: { text: '待付款', color: 'gold' },
  2: { text: '待发货', color: 'blue' },
  3: { text: '待收货', color: 'cyan' },
  4: { text: '已完成', color: 'green' },
  5: { text: '已取消', color: 'default' },
}

async function load(p = 1) {
  loading.value = true
  try {
    page.value = p
    const res = await getMyOrders({ role: 'buyer', page: p, page_size: 20 })
    list.value = res.list
    total.value = res.total
  } catch { /* 已提示 */ } finally {
    loading.value = false
  }
}

onMounted(() => load())
</script>

<template>
  <a-card title="订单管理">
    <a-table
      :columns="columns"
      :data-source="list"
      :loading="loading"
      :pagination="{ current: page, pageSize: 20, total, onChange: load }"
      row-key="id"
      size="middle"
    >
      <template #bodyCell="{ column, record }">
        <template v-if="column.dataIndex === 'deal_price'">¥{{ record.deal_price }}</template>
        <template v-else-if="column.dataIndex === 'status'">
          <a-tag :color="statusMap[record.status]?.color">{{ statusMap[record.status]?.text }}</a-tag>
        </template>
      </template>
    </a-table>
  </a-card>
</template>
