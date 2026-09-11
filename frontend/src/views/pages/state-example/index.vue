<script setup lang="ts">
import { storeToRefs } from 'pinia'
import {
  Button as AButton,
  Card as ACard,
  Col as ACol,
  Empty as AEmpty,
  Row as ARow,
  Space as ASpace,
  Statistic as AStatistic,
  Timeline as ATimeline,
  TimelineItem as ATimelineItem,
} from 'ant-design-vue'
import { useCounterStore } from '@/stores/counter'
import PageHeader from '@/components/common/PageHeader.vue'

const counterStore = useCounterStore()
// storeToRefs 保持 state/getter 的响应性；action 直接从 store 调用即可。
const { count, doubled, history } = storeToRefs(counterStore)
</script>

<template>
  <main class="page-container">
    <PageHeader title="Pinia 状态示例" description="展示跨组件共享状态、派生值与操作方法。" />
    <a-row :gutter="[16, 16]">
      <a-col :xs="24" :md="12">
        <a-card title="计数器" :bordered="false">
          <a-space direction="vertical" size="large">
            <a-statistic title="当前计数" :value="count" />
            <a-statistic title="派生值（两倍）" :value="doubled" />
            <a-space>
              <a-button type="primary" @click="counterStore.increment">增加</a-button>
              <a-button :disabled="count === 0" @click="counterStore.reset">重置</a-button>
            </a-space>
          </a-space>
        </a-card>
      </a-col>
      <a-col :xs="24" :md="12">
        <a-card title="操作历史" :bordered="false">
          <a-empty v-if="history.length === 0" description="暂无操作" />
          <a-timeline v-else>
            <a-timeline-item v-for="(value, index) in history" :key="index">第 {{ index + 1 }} 次：{{ value }}</a-timeline-item>
          </a-timeline>
        </a-card>
      </a-col>
    </a-row>
  </main>
</template>
