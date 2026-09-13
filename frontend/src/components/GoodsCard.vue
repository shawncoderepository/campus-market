<script setup lang="ts">
import { computed } from 'vue'
import { EyeOutlined, EnvironmentOutlined } from '@ant-design/icons-vue'
import type { GoodsItem } from '@/common/types/business'

const props = defineProps<{ goods: GoodsItem }>()
const emit = defineEmits<{ (e: 'click', id: number): void }>()

const cover = computed(() => props.goods.images?.[0] || '')
const conditionMap: Record<number, { text: string; cls: string }> = {
  5: { text: '全新', cls: 'is-new' },
  4: { text: '几乎全新', cls: 'is-like-new' },
  3: { text: '明显使用', cls: 'is-used' },
  2: { text: '成色一般', cls: 'is-fair' },
  1: { text: '成色较差', cls: 'is-poor' },
}
const condition = computed(() => conditionMap[props.goods.condition_level] || conditionMap[3])
const discount = computed(() => {
  if (!props.goods.original_price || props.goods.original_price <= 0) return null
  return Math.round((props.goods.sell_price / props.goods.original_price) * 10)
})
</script>

<template>
  <div class="goods-card" @click="emit('click', goods.id)">
    <div class="goods-card__cover">
      <img v-if="cover" :src="cover" :alt="goods.title" loading="lazy" />
      <div v-else class="goods-card__placeholder">
        <span class="goods-card__placeholder-icon">📦</span>
        <span class="goods-card__placeholder-text">{{ goods.title.slice(0, 4) }}</span>
      </div>
      <span class="goods-card__condition" :class="condition.cls">{{ condition.text }}</span>
      <span v-if="discount && discount < 10" class="goods-card__discount">{{ discount }}折</span>
    </div>
    <div class="goods-card__body">
      <h3 class="goods-card__title">{{ goods.title }}</h3>
      <div class="goods-card__price">
        <span class="goods-card__sell"><i>¥</i>{{ goods.sell_price }}</span>
        <span v-if="goods.original_price > 0" class="goods-card__original">¥{{ goods.original_price }}</span>
      </div>
      <div class="goods-card__meta">
        <span class="goods-card__seller">
          <img v-if="goods.seller_avatar" :src="goods.seller_avatar" class="goods-card__avatar" alt="" />
          <i v-else class="goods-card__avatar goods-card__avatar--text">{{ goods.seller_nickname.slice(0, 1) }}</i>
          {{ goods.seller_nickname }}
        </span>
        <span class="goods-card__views"><EyeOutlined /> {{ goods.view_count }}</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.goods-card { background: #fff; border-radius: 14px; overflow: hidden; cursor: pointer; transition: transform 0.18s ease, box-shadow 0.18s ease; box-shadow: var(--shadow-card, 0 2px 12px rgba(43,38,34,0.06)); }
.goods-card:hover { transform: translateY(-5px); box-shadow: var(--shadow-card-hover, 0 12px 32px rgba(255,106,0,0.14)); }

.goods-card__cover { position: relative; width: 100%; aspect-ratio: 1; background: #f5f0ea; overflow: hidden; }
.goods-card__cover img { width: 100%; height: 100%; object-fit: cover; display: block; transition: transform 0.3s ease; }
.goods-card:hover .goods-card__cover img { transform: scale(1.05); }
.goods-card__placeholder { width: 100%; height: 100%; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 8px; background: linear-gradient(135deg, #fff1e6, #ffe8d6); }
.goods-card__placeholder-icon { font-size: 44px; }
.goods-card__placeholder-text { font-size: 13px; color: #c98a5a; font-weight: 600; }

.goods-card__condition { position: absolute; top: 10px; left: 10px; padding: 3px 10px; font-size: 12px; font-weight: 600; color: #fff; border-radius: 20px; backdrop-filter: blur(4px); }
.goods-card__condition.is-new { background: rgba(34, 197, 94, 0.9); }
.goods-card__condition.is-like-new { background: rgba(59, 130, 246, 0.9); }
.goods-card__condition.is-used { background: rgba(255, 106, 0, 0.9); }
.goods-card__condition.is-fair { background: rgba(245, 158, 11, 0.9); }
.goods-card__condition.is-poor { background: rgba(120, 113, 108, 0.9); }

.goods-card__discount { position: absolute; top: 10px; right: 10px; padding: 3px 8px; font-size: 12px; font-weight: 700; color: #fff; background: linear-gradient(135deg, #ff8a3d, #ff6a00); border-radius: 8px; box-shadow: 0 2px 8px rgba(255,106,0,0.3); }

.goods-card__body { padding: 12px 14px 14px; }
.goods-card__title { margin: 0 0 8px; font-size: 14px; font-weight: 600; color: var(--ink, #2b2622); line-height: 1.4; height: 2.8em; overflow: hidden; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; }

.goods-card__price { display: flex; align-items: baseline; gap: 8px; margin-bottom: 10px; }
.goods-card__sell { font-size: 20px; font-weight: 800; color: #ff6a00; }
.goods-card__sell i { font-style: normal; font-size: 13px; margin-right: 1px; }
.goods-card__original { font-size: 12px; color: var(--ink-faint, #c9c2ba); text-decoration: line-through; }

.goods-card__meta { display: flex; justify-content: space-between; align-items: center; font-size: 12px; color: var(--ink-soft, #8a8078); }
.goods-card__seller { display: flex; align-items: center; gap: 6px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.goods-card__avatar { width: 20px; height: 20px; border-radius: 50%; object-fit: cover; flex-shrink: 0; }
.goods-card__avatar--text { display: inline-grid; place-items: center; background: linear-gradient(135deg, #ff8a3d, #ff6a00); color: #fff; font-size: 11px; font-weight: 700; font-style: normal; }
.goods-card__views { flex-shrink: 0; display: flex; align-items: center; gap: 3px; }
</style>
