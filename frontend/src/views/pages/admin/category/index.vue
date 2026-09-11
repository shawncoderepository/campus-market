<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { Card as ACard, Table as ATable } from 'ant-design-vue'
import { getCategories } from '@/common/apis/goodsApi'
import type { Category } from '@/common/types/business'

const loading = ref(false)
const list = ref<Category[]>([])

const columns = [
  { title: 'ID', dataIndex: 'id', width: 80 },
  { title: '图标', dataIndex: 'icon', width: 80 },
  { title: '分类名', dataIndex: 'name' },
  { title: '排序', dataIndex: 'sort', width: 80 },
]

onMounted(async () => {
  loading.value = true
  try {
    list.value = await getCategories()
  } catch { /* 已提示 */ } finally {
    loading.value = false
  }
})
</script>

<template>
  <a-card title="分类管理">
    <a-table :columns="columns" :data-source="list" :loading="loading" row-key="id" :pagination="false" size="middle" />
  </a-card>
</template>
