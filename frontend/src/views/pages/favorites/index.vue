<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { Empty as AEmpty, message, Spin as ASpin } from 'ant-design-vue'
import GoodsCard from '@/components/GoodsCard.vue'
import { getMyFavorites, toggleFavorite } from '@/common/apis/favoriteApi'
import type { GoodsItem } from '@/common/types/business'

const router = useRouter()
const loading = ref(false)
const favorites = ref<GoodsItem[]>([])

async function load() {
  loading.value = true
  try {
    const res = await getMyFavorites({ page_size: 100 })
    favorites.value = res.list
  } catch { /* 已提示 */ } finally {
    loading.value = false
  }
}

async function remove(id: number) {
  try {
    await toggleFavorite(id)
    message.success('已取消收藏')
    favorites.value = favorites.value.filter((f) => f.id !== id)
  } catch { /* 已提示 */ }
}

onMounted(load)
</script>

<template>
  <div class="favorites">
    <h2 class="favorites__title">我的收藏</h2>
    <a-spin :spinning="loading">
      <a-empty v-if="!favorites.length" description="还没有收藏，去首页逛逛吧" />
      <div v-else class="favorites__grid">
        <div v-for="item in favorites" :key="item.id" class="favorites__cell">
          <GoodsCard :goods="item" @click="(id) => router.push(`/goods/${id}`)" />
          <button class="favorites__remove" @click="remove(item.id)">取消收藏</button>
        </div>
      </div>
    </a-spin>
  </div>
</template>

<style scoped>
.favorites__title { font-size: 20px; font-weight: 700; margin-bottom: 20px; }
.favorites__grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(210px, 1fr)); gap: 18px; }
.favorites__cell { position: relative; }
.favorites__remove { margin-top: 6px; width: 100%; padding: 6px; border: 1px solid #e5e7eb; background: #fff; border-radius: 8px; cursor: pointer; font-size: 13px; color: #98a2b3; }
.favorites__remove:hover { color: #ef4444; border-color: #ef4444; }
</style>
