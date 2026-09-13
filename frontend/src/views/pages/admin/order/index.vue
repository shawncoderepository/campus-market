<script setup lang="ts">
import { onMounted, ref } from 'vue'
import {
  Button as AButton,
  Card as ACard,
  Descriptions as ADescriptions,
  DescriptionsItem as ADescriptionsItem,
  Drawer as ADrawer,
  InputSearch as AInputSearch,
  RadioButton as ARadioButton,
  RadioGroup as ARadioGroup,
  Table as ATable,
  Tag as ATag,
} from 'ant-design-vue'
import {
  CheckCircleOutlined,
  ClockCircleOutlined,
  CloseCircleOutlined,
  EyeOutlined,
  SearchOutlined,
  ShoppingCartOutlined,
  SyncOutlined,
} from '@ant-design/icons-vue'
import { getAdminOrders, type AdminOrder } from '@/common/apis/adminApi'

const loading = ref(false)
const list = ref<AdminOrder[]>([])
const total = ref(0)
const statusFilter = ref<number | undefined>(undefined)
const page = ref(1)
const pageSize = ref(10)

// 订单详情抽屉
const drawerVisible = ref(false)
const current = ref<AdminOrder | null>(null)

const statusMap: Record<number, { text: string; color: string; icon: unknown; step: number }> = {
  1: { text: '待付款', color: '#f59e0b', icon: ClockCircleOutlined, step: 0 },
  2: { text: '待面议', color: '#6366f1', icon: SyncOutlined, step: 1 },
  3: { text: '待面议', color: '#06b6d4', icon: SyncOutlined, step: 2 },
  4: { text: '已完成', color: '#10b981', icon: CheckCircleOutlined, step: 3 },
  5: { text: '已取消', color: '#94a3b8', icon: CloseCircleOutlined, step: -1 },
}

const columns = [
  { title: '订单号', dataIndex: 'order_no', width: 180 },
  { title: '商品', dataIndex: 'product_title', ellipsis: true },
  { title: '买家', dataIndex: 'buyer_nickname', width: 110 },
  { title: '卖家', dataIndex: 'seller_nickname', width: 110 },
  { title: '成交价', dataIndex: 'deal_price', width: 100 },
  { title: '状态', dataIndex: 'status', width: 110 },
  { title: '下单时间', dataIndex: 'created_at', width: 160 },
  { title: '操作', key: 'action', width: 100, fixed: 'right' as const },
]

async function load() {
  loading.value = true
  try {
    const res = await getAdminOrders({ status: statusFilter.value, page: page.value, page_size: pageSize.value })
    list.value = res.list
    total.value = res.total
  } finally {
    loading.value = false
  }
}

function onFilterChange() {
  page.value = 1
  load()
}

function onPageChange(p: { current?: number; pageSize?: number }) {
  page.value = p.current || 1
  pageSize.value = p.pageSize || 10
  load()
}

const totalText = (t: number) => `共 ${t} 笔订单`

function openDetail(r: AdminOrder) {
  current.value = r
  drawerVisible.value = true
}

onMounted(load)
</script>

<template>
  <div class="order-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="page-header__left">
        <h1 class="page-header__title">
          <ShoppingCartOutlined />
          订单管理
        </h1>
        <p class="page-header__subtitle">查看和跟踪平台全部交易订单</p>
      </div>
    </div>

    <!-- 筛选工具栏 -->
    <a-card class="filter-card" :bordered="false">
      <div class="filter-bar">
        <div class="filter-bar__left">
          <a-input-search
            placeholder="搜索订单号 / 商品 / 买家 / 卖家"
            class="filter-bar__search"
            allow-clear
            @search="load"
          >
            <template #prefix><SearchOutlined style="color: #94a3b8" /></template>
          </a-input-search>
          <a-radio-group v-model:value="statusFilter" button-style="solid" @change="onFilterChange">
            <a-radio-button :value="undefined">全部</a-radio-button>
            <a-radio-button :value="1">待付款</a-radio-button>
            <a-radio-button :value="2">待面议</a-radio-button>
            <a-radio-button :value="3">待面议</a-radio-button>
            <a-radio-button :value="4">已完成</a-radio-button>
            <a-radio-button :value="5">已取消</a-radio-button>
          </a-radio-group>
        </div>
        <a-button @click="load">刷新</a-button>
      </div>
    </a-card>

    <!-- 订单表格 -->
    <a-card class="table-card" :bordered="false">
      <a-table
        :columns="columns"
        :data-source="list"
        :loading="loading"
        :pagination="{
          current: page,
          pageSize,
          total,
          showTotal: totalText,
          showSizeChanger: true,
          showQuickJumper: true,
        }"
        row-key="id"
        size="middle"
        :scroll="{ x: 1100 }"
        @change="onPageChange"
      >
        <template #bodyCell="{ column, record }">
          <!-- 订单号列 -->
          <template v-if="column.dataIndex === 'order_no'">
            <span class="order-no">{{ record.order_no }}</span>
          </template>

          <!-- 成交价列 -->
          <template v-else-if="column.dataIndex === 'deal_price'">
            <span class="deal-price">¥{{ record.deal_price }}</span>
          </template>

          <!-- 状态列 -->
          <template v-else-if="column.dataIndex === 'status'">
            <div class="status-cell">
              <span class="status-cell__icon" :style="{ color: statusMap[record.status]?.color }">
                <component :is="statusMap[record.status]?.icon" />
              </span>
              <span class="status-cell__text" :style="{ color: statusMap[record.status]?.color }">
                {{ statusMap[record.status]?.text }}
              </span>
            </div>
          </template>

          <!-- 操作列 -->
          <template v-else-if="column.key === 'action'">
            <a-button size="small" type="text" @click="openDetail(record)">
              <template #icon><EyeOutlined /></template>
              详情
            </a-button>
          </template>
        </template>
      </a-table>
    </a-card>

    <!-- 订单详情抽屉 -->
    <a-drawer
      v-model:open="drawerVisible"
      title="订单详情"
      :width="480"
      class="order-drawer"
    >
      <div v-if="current" class="order-detail">
        <!-- 状态进度 -->
        <div class="order-detail__status">
          <div class="status-timeline">
            <div
              v-for="(s, key) in [1, 2, 3, 4]"
              :key="key"
              class="status-timeline__step"
              :class="{
                active: statusMap[current.status]?.step >= statusMap[s as unknown as number]?.step - 1 && current.status !== 5,
                done: statusMap[current.status]?.step > statusMap[s as unknown as number]?.step - 1 && current.status !== 5,
              }"
            >
              <div class="status-timeline__dot">
                <CheckCircleOutlined v-if="statusMap[current.status]?.step > statusMap[s as unknown as number]?.step - 1 && current.status !== 5" />
              </div>
              <div class="status-timeline__label">{{ statusMap[s as unknown as number]?.text }}</div>
            </div>
            <div v-if="current.status === 5" class="status-timeline__cancel">
              <CloseCircleOutlined />
              订单已取消
            </div>
          </div>
        </div>

        <!-- 订单信息 -->
        <a-descriptions :column="1" bordered size="small" class="order-detail__info">
          <a-descriptions-item label="订单号">
            <span class="order-no">{{ current.order_no }}</span>
          </a-descriptions-item>
          <a-descriptions-item label="商品">{{ current.product_title }}</a-descriptions-item>
          <a-descriptions-item label="买家">{{ current.buyer_nickname }}</a-descriptions-item>
          <a-descriptions-item label="卖家">{{ current.seller_nickname }}</a-descriptions-item>
          <a-descriptions-item label="成交价">
            <span class="deal-price">¥{{ current.deal_price }}</span>
          </a-descriptions-item>
          <a-descriptions-item label="状态">
            <a-tag :color="statusMap[current.status]?.color">
              {{ statusMap[current.status]?.text }}
            </a-tag>
          </a-descriptions-item>
          <a-descriptions-item label="交易地址">{{ current.address || '-' }}</a-descriptions-item>
          <a-descriptions-item label="备注">{{ current.remark || '-' }}</a-descriptions-item>
          <a-descriptions-item label="下单时间">{{ current.created_at }}</a-descriptions-item>
        </a-descriptions>
      </div>
    </a-drawer>
  </div>
</template>

<style scoped>
.order-page {
  padding-bottom: 24px;
}

/* ===== 页面头部 ===== */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header__title {
  margin: 0;
  font-size: 22px;
  font-weight: 700;
  color: #1e293b;
  display: flex;
  align-items: center;
  gap: 10px;
}

.page-header__title :deep(.anticon) {
  color: #10b981;
}

.page-header__subtitle {
  margin: 4px 0 0;
  color: #64748b;
  font-size: 13px;
}

/* ===== 筛选卡片 ===== */
.filter-card {
  margin-bottom: 16px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.filter-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}

.filter-bar__left {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.filter-bar__search {
  width: 320px;
}

/* ===== 表格 ===== */
.table-card {
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.table-card :deep(.ant-table-thead > tr > th) {
  background: #f8fafc;
  font-weight: 600;
  color: #475569;
}

.order-no {
  font-family: 'Courier New', monospace;
  font-size: 13px;
  color: #6366f1;
}

.deal-price {
  font-size: 16px;
  font-weight: 700;
  color: #f59e0b;
}

/* ===== 状态单元格 ===== */
.status-cell {
  display: flex;
  align-items: center;
  gap: 6px;
}

.status-cell__icon {
  font-size: 14px;
}

.status-cell__text {
  font-size: 13px;
  font-weight: 500;
}

/* ===== 订单详情抽屉 ===== */
.order-detail__status {
  margin-bottom: 24px;
}

.status-timeline {
  display: flex;
  justify-content: space-between;
  position: relative;
  padding: 0 10px;
}

.status-timeline::before {
  content: '';
  position: absolute;
  top: 14px;
  left: 10%;
  right: 10%;
  height: 2px;
  background: #e2e8f0;
}

.status-timeline__step {
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
  z-index: 1;
}

.status-timeline__dot {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: #fff;
  border: 2px solid #e2e8f0;
  display: grid;
  place-items: center;
  color: #10b981;
  font-size: 14px;
  transition: all 0.2s;
}

.status-timeline__step.active .status-timeline__dot {
  border-color: #6366f1;
  background: #6366f1;
  color: #fff;
}

.status-timeline__step.done .status-timeline__dot {
  border-color: #10b981;
  background: #10b981;
  color: #fff;
}

.status-timeline__label {
  margin-top: 8px;
  font-size: 12px;
  color: #94a3b8;
}

.status-timeline__step.active .status-timeline__label,
.status-timeline__step.done .status-timeline__label {
  color: #1e293b;
  font-weight: 500;
}

.status-timeline__cancel {
  position: absolute;
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  background: #fef2f2;
  color: #ef4444;
  padding: 8px 16px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  font-weight: 500;
}

/* ===== 响应式 ===== */
@media (max-width: 768px) {
  .filter-bar {
    flex-direction: column;
    align-items: stretch;
  }

  .filter-bar__search {
    width: 100%;
  }
}
</style>
