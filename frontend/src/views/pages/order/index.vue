<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import {
  Button as AButton,
  Card as ACard,
  Empty as AEmpty,
  message,
  Modal as AModal,
  Rate as ARate,
  Spin as ASpin,
  TabPane as ATabPane,
  Tabs as ATabs,
  Tag as ATag,
  Textarea as ATextarea,
} from 'ant-design-vue'
import { cancelOrder, confirmOrder, getMyOrders, payOrder } from '@/common/apis/orderApi'
import { createReview } from '@/common/apis/reviewApi'
import type { Order } from '@/common/types/business'

const router = useRouter()
const loading = ref(false)
const role = ref('buyer')
const orders = ref<Order[]>([])
const reviewVisible = ref(false)
const reviewOrder = ref<Order | null>(null)
const rating = ref(5)
const reviewContent = ref('')
const actionLoading = ref(false)

const statusMap: Record<number, { text: string; color: string }> = {
  1: { text: '待付款', color: 'gold' },
  2: { text: '待面议', color: 'blue' },
  3: { text: '待面议', color: 'cyan' },
  4: { text: '已完成', color: 'green' },
  5: { text: '已取消', color: 'default' },
}

async function load() {
  loading.value = true
  try {
    const res = await getMyOrders({ role: role.value, page_size: 100 })
    orders.value = res.list
  } catch { /* 已提示 */ } finally {
    loading.value = false
  }
}

function onRoleChange() {
  void load()
}

async function doAction(order: Order, action: 'pay' | 'confirm' | 'cancel') {
  actionLoading.value = true
  try {
    if (action === 'pay') await payOrder(order.id)
    else if (action === 'confirm') await confirmOrder(order.id)
    else await cancelOrder(order.id)
    message.success('操作成功')
    await load()
  } catch { /* 已提示 */ } finally {
    actionLoading.value = false
  }
}

function openReview(order: Order) {
  reviewOrder.value = order
  rating.value = 5
  reviewContent.value = ''
  reviewVisible.value = true
}

async function submitReview() {
  if (!reviewOrder.value) return
  actionLoading.value = true
  try {
    await createReview({ order_id: reviewOrder.value.id, rating: rating.value, content: reviewContent.value })
    message.success('评价成功')
    reviewVisible.value = false
    await load()
  } catch { /* 已提示 */ } finally {
    actionLoading.value = false
  }
}

onMounted(load)
</script>

<template>
  <a-card class="order page-mid" title="我的订单">
    <a-tabs v-model:active-key="role" @change="onRoleChange">
      <a-tab-pane key="buyer" tab="我买入的" />
      <a-tab-pane key="seller" tab="我卖出的" />
    </a-tabs>

    <a-spin :spinning="loading">
      <a-empty v-if="!orders.length" description="暂无订单" />
      <div v-for="o in orders" :key="o.id" class="order__item">
        <div class="order__head">
          <span class="order__no">订单号 {{ o.order_no }}</span>
          <a-tag :color="statusMap[o.status]?.color">{{ statusMap[o.status]?.text }}</a-tag>
        </div>
        <div class="order__body" @click="router.push(`/goods/${o.product_id}`)">
          <div class="order__title">{{ o.product_title }}</div>
          <div class="order__meta">
            <span>{{ role === 'buyer' ? '卖家' : '买家' }}：{{ role === 'buyer' ? o.seller_nickname : o.buyer_nickname }}</span>
            <span class="order__price">¥{{ o.deal_price }}</span>
          </div>
          <div v-if="o.address" class="order__address">地址：{{ o.address }}</div>
        </div>
        <div class="order__actions">
          <template v-if="role === 'buyer'">
            <a-button v-if="o.status === 1" type="primary" size="small" :loading="actionLoading" @click="doAction(o, 'pay')">付款</a-button>
            <a-button v-if="o.status === 3" type="primary" size="small" :loading="actionLoading" @click="doAction(o, 'confirm')">确认收货</a-button>
            <a-button v-if="o.status === 4 && !o.has_review" size="small" @click="openReview(o)">评价</a-button>
            <a-tag v-if="o.status === 4 && o.has_review" color="green">已评价</a-tag>
            <a-button v-if="o.status === 1 || o.status === 2" danger size="small" :loading="actionLoading" @click="doAction(o, 'cancel')">取消</a-button>
          </template>
          <template v-else>
            <a-tag v-if="o.status === 3" color="cyan">等待买家确认收货</a-tag>
            <a-button v-if="o.status === 1 || o.status === 2" danger size="small" :loading="actionLoading" @click="doAction(o, 'cancel')">取消</a-button>
          </template>
        </div>
      </div>
    </a-spin>

    <a-modal v-model:open="reviewVisible" title="评价订单" :confirm-loading="actionLoading" @ok="submitReview">
      <div style="margin-bottom:12px">
        <span style="margin-right:8px">评分：</span>
        <a-rate v-model:value="rating" />
      </div>
      <a-textarea v-model:value="reviewContent" :rows="4" placeholder="说说这次交易体验（选填）" />
    </a-modal>
  </a-card>
</template>

<style scoped>
.order { border-radius: 12px; }
.order__item { border: 1px solid #f0f2f5; border-radius: 10px; padding: 14px; margin-bottom: 12px; }
.order__head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
.order__no { font-size: 12px; color: #98a2b3; }
.order__body { cursor: pointer; }
.order__title { font-weight: 600; color: #1f2937; }
.order__meta { display: flex; justify-content: space-between; align-items: center; margin-top: 6px; color: #98a2b3; font-size: 13px; }
.order__price { color: #ef4444; font-weight: 700; font-size: 16px; }
.order__address { margin-top: 4px; font-size: 12px; color: #98a2b3; }
.order__actions { display: flex; gap: 8px; margin-top: 12px; justify-content: flex-end; }
</style>
