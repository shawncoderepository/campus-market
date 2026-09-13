<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  AppstoreOutlined,
  CameraOutlined,
  FireOutlined,
  RobotOutlined,
  SafetyCertificateOutlined,
  SearchOutlined,
  ShoppingOutlined,
  TagsOutlined,
  ThunderboltOutlined,
} from '@ant-design/icons-vue'
import GoodsCard from '@/components/GoodsCard.vue'
import { getCategories, getGoodsList } from '@/common/apis/goodsApi'
import type { GoodsItem, Category } from '@/common/types/business'

const router = useRouter()
const route = useRoute()
const loading = ref(false)
const list = ref<GoodsItem[]>([])
const total = ref(0)
const categories = ref<Category[]>([])
const query = ref({ page: 1, page_size: 20, keyword: String(route.query.keyword || ''), category_id: undefined as number | undefined, sort: 'latest' })

const sortTabs = [
  { key: 'latest', label: '最新' },
  { key: 'hot', label: '最热' },
  { key: 'price_asc', label: '价格 ↑' },
  { key: 'price_desc', label: '价格 ↓' },
]

// 平台亮点
const features = [
  { icon: ThunderboltOutlined, title: 'AI 智能议价', desc: 'AI 帮你生成还价话术，买卖双方砍价不再尴尬' },
  { icon: SafetyCertificateOutlined, title: '校园安全交易', desc: '实名认证 + 信用分体系，交易更安心' },
  { icon: RobotOutlined, title: 'AI 智能估价', desc: '发布时 AI 帮你定价、一键生成商品文案' },
]

// 使用流程
const steps = [
  { icon: CameraOutlined, title: '发布闲置', desc: '拍照上传，AI 帮写' },
  { icon: SearchOutlined, title: '搜索浏览', desc: '分类筛选找好物' },
  { icon: TagsOutlined, title: '在线议价', desc: '多轮还价到满意' },
  { icon: ShoppingOutlined, title: '下单成交', desc: '当面交易互评' },
]

const fetchList = async () => {
  loading.value = true
  try {
    const data = await getGoodsList(query.value)
    list.value = data.list
    total.value = data.total
  } finally {
    loading.value = false
  }
}

// Hero 搜索统一走 URL，与顶部导航栏搜索保持一致，由 watch 驱动过滤
const onSearch = (value?: string) => {
  const kw = (value || '').trim()
  router.push({ path: '/', query: kw ? { keyword: kw } : {} })
}
const onCategory = (id?: number) => {
  query.value.category_id = id
  query.value.page = 1
  fetchList()
}
const onSort = (sort: string) => {
  query.value.sort = sort
  query.value.page = 1
  fetchList()
}
const onPage = (page: number) => {
  query.value.page = page
  fetchList()
}

// 顶部导航栏搜索会修改 URL 的 keyword，这里监听它实时过滤
watch(
  () => route.query.keyword,
  (val) => {
    query.value.keyword = String(val || '')
    query.value.page = 1
    fetchList()
  },
)

onMounted(async () => {
  fetchList()
  categories.value = await getCategories()
})
</script>

<template>
  <div class="home">
    <!-- Hero 横幅 -->
    <section class="hero">
      <div class="hero__inner">
        <h1 class="hero__title">校园二手，让闲置流动起来</h1>
        <p class="hero__subtitle">教材 · 数码 · 生活好物 · AI 帮你估价议价</p>
        <a-input-search
          class="hero__search"
          size="large"
          placeholder="搜一搜，说不定就有你想要的…"
          enter-button
          @search="onSearch"
        >
          <template #enterButton>
            <a-button type="primary" size="large"><SearchOutlined /> 搜索</a-button>
          </template>
        </a-input-search>
      </div>
    </section>

    <!-- 平台亮点 -->
    <section class="features">
      <div v-for="f in features" :key="f.title" class="feature-card">
        <div class="feature-card__icon"><component :is="f.icon" /></div>
        <div class="feature-card__title">{{ f.title }}</div>
        <div class="feature-card__desc">{{ f.desc }}</div>
      </div>
    </section>

    <!-- 使用流程 -->
    <section class="flow">
      <div class="flow__head">
        <span class="flow__title">四步轻松交易</span>
        <span class="flow__sub">从闲置到变现，就这么简单</span>
      </div>
      <div class="flow__steps">
        <template v-for="(s, i) in steps" :key="s.title">
          <div class="flow-step">
            <div class="flow-step__num">{{ i + 1 }}</div>
            <div class="flow-step__icon"><component :is="s.icon" /></div>
            <div class="flow-step__title">{{ s.title }}</div>
            <div class="flow-step__desc">{{ s.desc }}</div>
          </div>
          <div v-if="i < steps.length - 1" class="flow__arrow">→</div>
        </template>
      </div>
    </section>

    <!-- 分类 -->
    <section class="cats">
      <div
        class="cat-chip"
        :class="{ active: query.category_id === undefined }"
        @click="onCategory(undefined)"
      >
        <AppstoreOutlined /> 全部
      </div>
      <div
        v-for="c in categories"
        :key="c.id"
        class="cat-chip"
        :class="{ active: query.category_id === c.id }"
        @click="onCategory(c.id)"
      >
        {{ c.name }}
      </div>
    </section>

    <!-- 商品区标题 + 排序 -->
    <section class="sortbar">
      <span class="sortbar__label"><FireOutlined /> 为你推荐 · {{ total }} 件好物</span>
      <div class="sortbar__tabs">
        <span
          v-for="t in sortTabs"
          :key="t.key"
          class="sort-tab"
          :class="{ active: query.sort === t.key }"
          @click="onSort(t.key)"
        >{{ t.label }}</span>
      </div>
    </section>

    <!-- 商品瀑布 -->
    <a-spin :spinning="loading">
      <a-empty v-if="!loading && !list.length" description="暂无相关商品" style="padding: 60px 0" />
      <div v-else class="grid">
        <GoodsCard v-for="g in list" :key="g.id" :goods="g" @click="(id) => router.push(`/goods/${id}`)" />
      </div>
      <div class="pager">
        <a-pagination
          v-model:current="query.page"
          :total="total"
          :page-size="query.page_size"
          show-less-items
          @change="onPage"
        />
      </div>
    </a-spin>
  </div>
</template>

<style scoped>
.home { display: flex; flex-direction: column; gap: 18px; }

/* Hero */
.hero {
  border-radius: 18px;
  background: linear-gradient(120deg, #ff8a3d 0%, #ff6a00 55%, #ff5e3a 100%);
  padding: 44px 40px;
  color: #fff;
  position: relative;
  overflow: hidden;
}
.hero::after {
  content: '';
  position: absolute; right: -60px; top: -60px;
  width: 260px; height: 260px; border-radius: 50%;
  background: rgba(255, 255, 255, 0.12);
}
.hero::before {
  content: '';
  position: absolute; right: 80px; bottom: -80px;
  width: 160px; height: 160px; border-radius: 50%;
  background: rgba(255, 255, 255, 0.08);
}
.hero__inner { position: relative; z-index: 1; max-width: 620px; }
.hero__title { margin: 0 0 8px; font-size: 30px; font-weight: 800; letter-spacing: 0.5px; }
.hero__subtitle { margin: 0 0 22px; font-size: 15px; opacity: 0.92; }
.hero__search { max-width: 520px; }
.hero__search :deep(.ant-input) { border-radius: 10px 0 0 10px; }

/* 平台亮点 */
.features { display: grid; grid-template-columns: repeat(3, 1fr); gap: 18px; }
.feature-card {
  background: #fff; border-radius: 14px; padding: 22px 20px;
  box-shadow: var(--shadow-card); transition: transform 0.18s ease, box-shadow 0.18s ease;
}
.feature-card:hover { transform: translateY(-3px); box-shadow: 0 8px 24px rgba(255,106,0,0.12); }
.feature-card__icon {
  width: 46px; height: 46px; border-radius: 12px; display: grid; place-items: center;
  font-size: 22px; color: #ff6a00; background: linear-gradient(135deg, #fff1e6, #ffe4cc); margin-bottom: 12px;
}
.feature-card__title { font-size: 16px; font-weight: 700; color: var(--ink); margin-bottom: 6px; }
.feature-card__desc { font-size: 13px; color: var(--ink-soft, #8a8078); line-height: 1.6; }

/* 使用流程 */
.flow { background: #fff; border-radius: 14px; padding: 24px 28px; box-shadow: var(--shadow-card); }
.flow__head { display: flex; align-items: baseline; gap: 12px; margin-bottom: 20px; }
.flow__title { font-size: 17px; font-weight: 800; color: var(--ink); }
.flow__sub { font-size: 13px; color: var(--ink-faint, #c9c2ba); }
.flow__steps { display: flex; align-items: center; justify-content: space-between; gap: 8px; }
.flow-step { flex: 1; text-align: center; position: relative; padding-top: 4px; }
.flow-step__num {
  position: absolute; top: -4px; left: 50%; transform: translateX(-50%);
  width: 20px; height: 20px; border-radius: 50%; background: linear-gradient(135deg, #ff8a3d, #ff6a00);
  color: #fff; font-size: 11px; font-weight: 700; display: grid; place-items: center; z-index: 1;
}
.flow-step__icon {
  width: 54px; height: 54px; margin: 8px auto 10px; border-radius: 50%; display: grid; place-items: center;
  font-size: 24px; color: #ff6a00; background: #fff6ef; border: 2px solid #ffe0c7;
}
.flow-step__title { font-size: 14px; font-weight: 700; color: var(--ink); margin-bottom: 4px; }
.flow-step__desc { font-size: 12px; color: var(--ink-soft, #8a8078); }
.flow__arrow { color: #ffcead; font-size: 20px; font-weight: 700; flex-shrink: 0; }

/* 分类芯片 */
.cats { display: flex; flex-wrap: wrap; gap: 10px; }
.cat-chip {
  display: inline-flex; align-items: center; gap: 5px;
  padding: 7px 16px; font-size: 14px; border-radius: 22px;
  background: #fff; color: var(--ink-soft, #8a8078);
  cursor: pointer; box-shadow: var(--shadow-card);
  transition: all 0.15s ease; user-select: none;
}
.cat-chip:hover { color: #ff6a00; transform: translateY(-1px); }
.cat-chip.active { background: linear-gradient(135deg, #ff8a3d, #ff6a00); color: #fff; font-weight: 600; box-shadow: 0 4px 12px rgba(255,106,0,0.3); }

/* 排序栏 */
.sortbar { display: flex; justify-content: space-between; align-items: center; }
.sortbar__label { font-size: 15px; font-weight: 700; color: var(--ink); display: flex; align-items: center; gap: 6px; }
.sortbar__label :deep(.anticon) { color: #ff6a00; }
.sortbar__tabs { display: flex; gap: 4px; background: #fff; padding: 4px; border-radius: 10px; box-shadow: var(--shadow-card); }
.sort-tab { padding: 5px 14px; font-size: 13px; border-radius: 8px; cursor: pointer; color: var(--ink-soft); transition: all 0.15s ease; }
.sort-tab:hover { color: #ff6a00; }
.sort-tab.active { background: var(--brand-soft, #fff1e6); color: #ff6a00; font-weight: 600; }

/* 网格与分页 */
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(218px, 1fr)); gap: 18px; }
.pager { display: flex; justify-content: center; padding: 12px 0 4px; }

@media (max-width: 900px) {
  .features { grid-template-columns: 1fr; }
  .flow__steps { flex-direction: column; gap: 16px; }
  .flow__arrow { transform: rotate(90deg); }
}
@media (max-width: 640px) {
  .hero { padding: 30px 22px; }
  .hero__title { font-size: 23px; }
}
</style>
