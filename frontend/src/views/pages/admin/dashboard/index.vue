<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { Card as ACard, Col as ACol, Row as ARow, Statistic as AStatistic } from 'ant-design-vue'
import { getGoodsList } from '@/common/apis/goodsApi'
import { getMyOrders } from '@/common/apis/orderApi'

const goodsTotal = ref(0)
const orderTotal = ref(0)

onMounted(async () => {
  try {
    const [g, o] = await Promise.all([
      getGoodsList({ page: 1, page_size: 1 }),
      getMyOrders({ role: 'buyer', page: 1, page_size: 1 }),
    ])
    goodsTotal.value = g.total
    orderTotal.value = o.total
  } catch { /* 已提示 */ }
})
</script>

<template>
  <div class="admin-dashboard">
    <h2 class="admin-dashboard__title">数据概览</h2>
    <a-row :gutter="16">
      <a-col :span="8">
        <a-card><a-statistic title="在售商品总数" :value="goodsTotal" /></a-card>
      </a-col>
      <a-col :span="8">
        <a-card><a-statistic title="订单总数" :value="orderTotal" /></a-card>
      </a-col>
      <a-col :span="8">
        <a-card><a-statistic title="平台" value="校园淘" /></a-card>
      </a-col>
    </a-row>
    <a-card style="margin-top:16px" title="说明">
      <p>这里是校园二手交易平台的管理后台，可对商品、订单、举报、用户、分类进行管理。</p>
      <p>更多统计维度（交易额、活跃用户、AI 调用量）可在后续迭代中接入。</p>
    </a-card>
  </div>
</template>

<style scoped>
.admin-dashboard__title { font-size: 20px; font-weight: 700; margin-bottom: 16px; }
</style>
