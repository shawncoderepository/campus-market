<script setup lang="ts">
import { onMounted, ref } from 'vue'
import {
  Button as AButton,
  Card as ACard,
  Spin as ASpin,
} from 'ant-design-vue'
import {
  AppstoreOutlined,
  ArrowUpOutlined,
  CheckCircleOutlined,
  CommentOutlined,
  DollarOutlined,
  FlagOutlined,
  ShoppingOutlined,
  TagsOutlined,
  TeamOutlined,
} from '@ant-design/icons-vue'
import {
  getAdminStats,
  getAdminCategoryShare,
  getAdminActivities,
  type AdminStats,
  type AdminCategoryShare,
  type AdminActivity,
} from '@/common/apis/adminApi'

const stats = ref<AdminStats | null>(null)
const loading = ref(true)

// 渐变色统计卡片
const cards = ref<Array<{
  key: keyof AdminStats
  title: string
  icon: unknown
  gradient: string
  isMoney?: boolean
}>>([])

// 最新动态（真实数据）
const activities = ref<AdminActivity[]>([])

// 分类占比（真实数据）
const categoryData = ref<Array<AdminCategoryShare & { color: string }>>([])

const PIE_COLORS = ['#6366f1', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899', '#06b6d4', '#f43f5e', '#84cc16']

// 饼图 conic-gradient 动态生成
const pieGradient = ref('')

onMounted(async () => {
  try {
    const [s, share, act] = await Promise.all([
      getAdminStats(),
      getAdminCategoryShare(),
      getAdminActivities(),
    ])
    stats.value = s
    cards.value = [
      { key: 'user_total', title: '注册用户', icon: TeamOutlined, gradient: 'linear-gradient(135deg, #6366f1, #8b5cf6)' },
      { key: 'goods_on_sale', title: '在售商品', icon: TagsOutlined, gradient: 'linear-gradient(135deg, #10b981, #34d399)' },
      { key: 'order_total', title: '订单总数', icon: ShoppingOutlined, gradient: 'linear-gradient(135deg, #f59e0b, #fbbf24)' },
      { key: 'deal_amount', title: '成交总额', icon: DollarOutlined, gradient: 'linear-gradient(135deg, #ec4899, #f472b6)', isMoney: true },
      { key: 'report_pending', title: '待处理举报', icon: FlagOutlined, gradient: 'linear-gradient(135deg, #ef4444, #f87171)' },
      { key: 'review_total', title: '评价总数', icon: CommentOutlined, gradient: 'linear-gradient(135deg, #06b6d4, #22d3ee)' },
    ]
    categoryData.value = share
      .filter((c) => c.count > 0)
      .map((c, i) => ({ ...c, color: PIE_COLORS[i % PIE_COLORS.length] }))
    activities.value = act

    // 动态生成饼图渐变
    let acc = 0
    const segs = categoryData.value.map((c) => {
      const start = acc
      acc += c.percent
      return `${c.color} ${start}% ${acc}%`
    })
    pieGradient.value = segs.length ? `conic-gradient(${segs.join(', ')})` : '#f1f5f9'
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="dash">
    <!-- 页面标题 -->
    <div class="dash__header">
      <div>
        <h1 class="dash__title">数据概览</h1>
        <p class="dash__subtitle">实时监控平台核心运营数据</p>
      </div>
      <a-button type="primary" class="dash__export">
        <template #icon><ArrowUpOutlined /></template>
        导出报表
      </a-button>
    </div>

    <a-spin :spinning="loading">
      <!-- 统计卡片 -->
      <div class="dash__grid">
        <div v-for="c in cards" :key="c.key" class="stat-card" :style="{ background: c.gradient }">
          <div class="stat-card__content">
            <div class="stat-card__info">
              <div class="stat-card__title">{{ c.title }}</div>
              <div class="stat-card__value">
                <template v-if="c.isMoney">¥{{ Number(stats?.[c.key] ?? 0).toLocaleString() }}</template>
                <template v-else>{{ stats?.[c.key] ?? 0 }}</template>
              </div>
            </div>
            <div class="stat-card__icon">
              <component :is="c.icon" />
            </div>
          </div>
          <div class="stat-card__decoration"></div>
        </div>
      </div>

      <!-- 图表区域 -->
      <div class="dash__charts">
        <!-- 分类占比 -->
        <a-card title="商品分类占比" class="chart-card">
          <div class="pie-chart">
            <div class="pie-chart__center" :style="{ background: pieGradient }">
              <div class="pie-chart__total">{{ stats?.goods_total || 0 }}</div>
              <div class="pie-chart__label">总商品</div>
            </div>
            <div class="pie-chart__legend">
              <div v-for="item in categoryData" :key="item.name" class="pie-chart__item">
                <span class="pie-chart__dot" :style="{ background: item.color }"></span>
                <span class="pie-chart__name">{{ item.name }}</span>
                <span class="pie-chart__value">{{ item.count }} 件 · {{ item.percent }}%</span>
              </div>
              <div v-if="!categoryData.length" class="pie-chart__empty">暂无商品数据</div>
            </div>
          </div>
        </a-card>

        <!-- 最新动态 -->
        <a-card title="最新动态" class="chart-card activity-card">
          <div class="activity-list">
            <div v-for="item in activities" :key="item.id" class="activity-item">
              <div class="activity-item__icon" :style="{ background: item.color + '15', color: item.color }">
                <CheckCircleOutlined />
              </div>
              <div class="activity-item__content">
                <div class="activity-item__text">
                  <span class="activity-item__user">{{ item.user }}</span>
                  {{ item.action }}
                  <span v-if="item.target" class="activity-item__target">{{ item.target }}</span>
                </div>
                <div class="activity-item__time">{{ item.time }}</div>
              </div>
            </div>
            <div v-if="!activities.length" class="activity-empty">暂无动态</div>
          </div>
        </a-card>
      </div>

      <!-- 快捷入口 -->
      <div class="dash__quick">
        <router-link to="/admin/goods" class="quick-card">
          <AppstoreOutlined class="quick-card__icon" style="color: #f59e0b" />
          <div class="quick-card__title">商品管理</div>
          <div class="quick-card__desc">上下架、审核商品</div>
        </router-link>
        <router-link to="/admin/order" class="quick-card">
          <ShoppingOutlined class="quick-card__icon" style="color: #10b981" />
          <div class="quick-card__title">订单管理</div>
          <div class="quick-card__desc">查看全部订单状态</div>
        </router-link>
        <router-link to="/admin/report" class="quick-card">
          <FlagOutlined class="quick-card__icon" style="color: #ef4444" />
          <div class="quick-card__title">举报处理</div>
          <div class="quick-card__desc">处理违规内容</div>
        </router-link>
        <router-link to="/admin/user" class="quick-card">
          <TeamOutlined class="quick-card__icon" style="color: #8b5cf6" />
          <div class="quick-card__title">用户管理</div>
          <div class="quick-card__desc">管理用户与信用</div>
        </router-link>
      </div>
    </a-spin>
  </div>
</template>

<style scoped>
.dash__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.dash__title {
  margin: 0;
  font-size: 24px;
  font-weight: 700;
  color: #1e293b;
}

.dash__subtitle {
  margin: 4px 0 0;
  color: #64748b;
  font-size: 14px;
}

.dash__export {
  border-radius: 8px;
}

/* ===== 统计卡片 ===== */
.dash__grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

.stat-card {
  position: relative;
  border-radius: 16px;
  padding: 24px;
  color: #fff;
  overflow: hidden;
  transition: transform 0.2s, box-shadow 0.2s;
  cursor: pointer;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.15);
}

.stat-card__content {
  position: relative;
  z-index: 1;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.stat-card__title {
  font-size: 14px;
  opacity: 0.85;
  margin-bottom: 8px;
}

.stat-card__value {
  font-size: 32px;
  font-weight: 700;
  line-height: 1.2;
}

.stat-card__icon {
  font-size: 40px;
  opacity: 0.25;
}

.stat-card__decoration {
  position: absolute;
  right: -20px;
  bottom: -20px;
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
}

/* ===== 图表区域 ===== */
.dash__charts {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

.chart-card {
  border-radius: 16px;
  border: none;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
}

.chart-card :deep(.ant-card-head) {
  border-bottom: none;
  padding-bottom: 0;
}

.chart-card :deep(.ant-card-head-title) {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
}

/* 饼图 */
.pie-chart {
  display: flex;
  align-items: center;
  gap: 32px;
  padding: 20px 0;
}

.pie-chart__center {
  position: relative;
  width: 140px;
  height: 140px;
  border-radius: 50%;
  display: grid;
  place-items: center;
  flex-shrink: 0;
}

.pie-chart__center::before {
  content: '';
  position: absolute;
  inset: 24px;
  background: #fff;
  border-radius: 50%;
}

.pie-chart__total {
  position: relative;
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
}

.pie-chart__label {
  position: relative;
  font-size: 12px;
  color: #64748b;
  margin-top: 20px;
}

.pie-chart__legend {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.pie-chart__item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
}

.pie-chart__dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.pie-chart__name {
  flex: 1;
  color: #334155;
}

.pie-chart__value {
  font-weight: 600;
  color: #1e293b;
}

/* 动态列表 */
.activity-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
  max-height: 280px;
  overflow-y: auto;
}

.activity-item {
  display: flex;
  gap: 12px;
}

.activity-item__icon {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  display: grid;
  place-items: center;
  font-size: 16px;
  flex-shrink: 0;
}

.activity-item__content {
  flex: 1;
  min-width: 0;
}

.activity-item__text {
  font-size: 14px;
  color: #334155;
  line-height: 1.5;
}

.activity-item__user {
  font-weight: 600;
  color: #1e293b;
}

.activity-item__target {
  color: #6366f1;
}

.activity-item__time {
  font-size: 12px;
  color: #94a3b8;
  margin-top: 2px;
}

.activity-empty,
.pie-chart__empty {
  color: #94a3b8;
  font-size: 13px;
  text-align: center;
  padding: 24px 0;
}

/* ===== 快捷入口 ===== */
.dash__quick {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
}

.quick-card {
  background: #fff;
  border-radius: 14px;
  padding: 24px;
  text-align: center;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
  transition: all 0.2s;
  text-decoration: none;
  display: block;
}

.quick-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
}

.quick-card__icon {
  font-size: 32px;
  margin-bottom: 12px;
}

.quick-card__title {
  font-size: 15px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 4px;
}

.quick-card__desc {
  font-size: 13px;
  color: #64748b;
}

/* ===== 响应式 ===== */
@media (max-width: 640px) {
  .dash__grid {
    grid-template-columns: 1fr;
  }

  .dash__charts {
    grid-template-columns: 1fr;
  }

  .pie-chart {
    flex-direction: column;
  }
}
</style>
