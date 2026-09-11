<script setup lang="ts">
import { onMounted, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  Empty as AEmpty,
  Pagination as APagination,
  RadioButton as ARadioButton,
  RadioGroup as ARadioGroup,
  Select as ASelect,
  Spin as ASpin,
} from 'ant-design-vue'
import GoodsCard from '@/components/GoodsCard.vue'
import { getCategories, getGoodsList, type GoodsListQuery } from '@/common/apis/goodsApi'
import type { Category, GoodsItem } from '@/common/types/business'

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const goods = ref<GoodsItem[]>([])
const categories = ref<Category[]>([])
const total = ref(0)

const query = reactive<GoodsListQuery>({
  keyword: String(route.query.keyword || ''),
  category_id: undefined,
  condition_level: undefined,
  sort: 'latest',
  page: 1,
  page_size: 24,
})

const sortOptions = [
  { label: '最新', value: 'latest' },
  { label: '价格从低到高', value: 'price_asc' },
  { label: '价格从高到低', value: 'price_desc' },
  { label: '最热', value: 'hot' },
]

async function loadCategories() {
  try {
    categories.value = await getCategories()
  } catch { /* 已提示 */ }
}

async function loadGoods() {
  loading.value = true
  try {
    const res = await getGoodsList(query)
    goods.value = res.list
    total.value = res.total
  } catch { /* 已提示 */ } finally {
    loading.value = false
  }
}

function onFilterChange() {
  query.page = 1
  void loadGoods()
}

function onPageChange(page: number) {
  query.page = page
  void loadGoods()
}

function goDetail(id: number) {
  void router.push(`/goods/${id}`)
}

// 顶部导航搜索时同步 keyword
watch(
  () => route.query.keyword,
  (val) => {
    query.keyword = String(val || '')
    query.page = 1
    void loadGoods()
  },
)

onMounted(() => {
  void loadCategories()
  void loadGoods()
})
</script>

<template>
  <div class="home">
    <!-- 分类快捷入口 -->
    <div class="home__cats">
      <button
        class="home__cat"
        :class="{ 'home__cat--active': !query.category_id }"
        @click="query.category_id = undefined; onFilterChange()"
      >
        全部
      </button>
      <button
        v-for="cat in categories"
        :key="cat.id"
        class="home__cat"
        :class="{ 'home__cat--active': query.category_id === cat.id }"
        @click="query.category_id = cat.id; onFilterChange()"
      >
        <span class="home__cat-icon">{{ cat.icon }}</span>{{ cat.name }}
      </button>
    </div>

    <!-- 筛选与排序工具条 -->
    <div class="home__toolbar">
      <a-radio-group v-model:value="query.sort" @change="onFilterChange">
        <a-radio-button v-for="opt in sortOptions" :key="opt.value" :value="opt.value">{{ opt.label }}</a-radio-button>
      </a-radio-group>
      <a-select
        v-model:value="query.condition_level"
        placeholder="成色"
        allow-clear
        class="home__condition"
        @change="onFilterChange"
      >
        <a-select-option :value="5">全新</a-select-option>
        <a-select-option :value="4">几乎全新</a-select-option>
        <a-select-option :value="3">明显使用</a-select-option>
        <a-select-option :value="2">成色一般</a-select-option>
        <a-select-option :value="1">成色较差</a-select-option>
      </a-select>
    </div>

    <!-- 商品瀑布流 -->
    <a-spin :spinning="loading">
      <div v-if="goods.length" class="home__grid">
        <GoodsCard v-for="item in goods" :key="item.id" :goods="item" @click="goDetail" />
      </div>
      <a-empty v-else-if="!loading" description="没有找到相关商品，换个关键词试试" />
    </a-spin>

    <div v-if="total > (query.page_size ?? 24)" class="home__pagination">
      <a-pagination
        :current="query.page"
        :page-size="query.page_size"
        :total="total"
        show-quick-jumper
        @change="onPageChange"
      />
    </div>
  </div>
</template>

<style scoped>
.home__cats { display: flex; gap: 10px; overflow-x: auto; padding-bottom: 8px; margin-bottom: 16px; }
.home__cat { flex-shrink: 0; padding: 8px 16px; border: 1px solid #e5e7eb; border-radius: 20px; background: #fff; cursor: pointer; font-size: 14px; color: #4b5563; transition: all 0.15s; white-space: nowrap; }
.home__cat:hover { border-color: #2563eb; color: #2563eb; }
.home__cat--active { background: #2563eb; border-color: #2563eb; color: #fff; }
.home__cat-icon { margin-right: 4px; }
.home__toolbar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; flex-wrap: wrap; gap: 12px; }
.home__condition { width: 140px; }
.home__grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(210px, 1fr)); gap: 18px; }
.home__pagination { display: flex; justify-content: center; margin-top: 28px; }
@media (max-width: 640px) {
  .home__grid { grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 12px; }
}
</style>
