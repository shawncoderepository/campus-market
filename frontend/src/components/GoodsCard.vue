<script setup lang="ts">
import { computed } from 'vue'
import { EyeOutlined } from '@ant-design/icons-vue'
import type { GoodsItem } from '@/common/types/business'

const props = defineProps<{ goods: GoodsItem }>()
const emit = defineEmits<{ (e: 'click', id: number): void }>()

const cover = computed(() => props.goods.images?.[0] || '')
const conditionText = computed(
  () => ({ 5: '全新', 4: '几乎全新', 3: '明显使用', 2: '成色一般', 1: '成色较差' })[props.goods.condition_level] || '成色一般',
)
</script>

<template>
  <div class="goods-card" @click="emit('click', goods.id)">
    <div class="goods-card__cover">
      <img v-if="cover" :src="cover" :alt="goods.title" loading="lazy" />
      <div v-else class="goods-card__placeholder">{{ goods.title.slice(0, 1) }}</div>
      <span class="goods-card__condition">{{ conditionText }}</span>
    </div>
    <div class="goods-card__body">
      <h3 class="goods-card__title">{{ goods.title }}</h3>
      <div class="goods-card__price">
        <span class="goods-card__sell">¥{{ goods.sell_price }}</span>
        <span v-if="goods.original_price > 0" class="goods-card__original">¥{{ goods.original_price }}</span>
      </div>
      <div class="goods-card__meta">
        <span class="goods-card__seller">{{ goods.seller_nickname }}</span>
        <span class="goods-card__views"><EyeOutlined /> {{ goods.view_count }}</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.goods-card { background: #fff; border-radius: 12px; overflow: hidden; cursor: pointer; transition: transform 0.18s ease, box-shadow 0.18s ease; border: 1px solid #f0f2f5; }
.goods-card:hover { transform: translateY(-4px); box-shadow: 0 10px 24px rgba(0, 0, 0, 0.08); }
.goods-card__cover { position: relative; width: 100%; aspect-ratio: 1; background: #f3f4f6; }
.goods-card__cover img { width: 100%; height: 100%; object-fit: cover; display: block; }
.goods-card__placeholder { width: 100%; height: 100%; display: grid; place-items: center; font-size: 48px; font-weight: 800; color: #c7d0e0; background: linear-gradient(135deg, #eef2ff, #f5f7fb); }
.goods-card__condition { position: absolute; top: 8px; left: 8px; padding: 2px 8px; font-size: 12px; color: #fff; background: rgba(37, 99, 235, 0.85); border-radius: 6px; }
.goods-card__body { padding: 12px; }
.goods-card__title { margin: 0 0 8px; font-size: 14px; font-weight: 600; color: #1f2937; line-height: 1.4; height: 2.8em; overflow: hidden; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; }
.goods-card__price { display: flex; align-items: baseline; gap: 8px; margin-bottom: 8px; }
.goods-card__sell { font-size: 18px; font-weight: 800; color: #ef4444; }
.goods-card__original { font-size: 12px; color: #9ca3af; text-decoration: line-through; }
.goods-card__meta { display: flex; justify-content: space-between; align-items: center; font-size: 12px; color: #9ca3af; }
.goods-card__seller { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.goods-card__views { flex-shrink: 0; }
</style>
