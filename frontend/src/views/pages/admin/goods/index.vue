<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import {
  Button as AButton,
  Card as ACard,
  InputSearch as AInputSearch,
  message,
  Modal,
  Pagination as APagination,
  RadioButton as ARadioButton,
  RadioGroup as ARadioGroup,
  Space as ASpace,
  Spin as ASpin,
  Table as ATable,
  Tag as ATag,
} from 'ant-design-vue'
import {
  AppstoreOutlined,
  BarsOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  EyeOutlined,
  PictureOutlined,
  SearchOutlined,
  ShopOutlined,
} from '@ant-design/icons-vue'
import { getAdminGoods, setGoodsStatus, type AdminGoods } from '@/common/apis/adminApi'

const loading = ref(false)
const list = ref<AdminGoods[]>([])
const total = ref(0)
const keyword = ref('')
const statusFilter = ref<number | undefined>(undefined)
const categoryFilter = ref<number | undefined>(undefined)
const page = ref(1)
const pageSize = ref(12)

// 视图模式：list 列表 / gallery 画廊
const viewMode = ref<'list' | 'gallery'>('list')

// 批量选择
const selectedRowKeys = ref<number[]>([])

const hasSelected = computed(() => selectedRowKeys.value.length > 0)

const statusMap: Record<number, { text: string; color: string; bg: string }> = {
  1: { text: '在售', color: '#10b981', bg: '#d1fae5' },
  2: { text: '已售', color: '#6366f1', bg: '#e0e7ff' },
  3: { text: '已下架', color: '#94a3b8', bg: '#f1f5f9' },
}

const columns = [
  { title: '商品', dataIndex: 'title', width: 280 },
  { title: '分类', dataIndex: 'category_name', width: 110 },
  { title: '售价', dataIndex: 'sell_price', width: 100 },
  { title: '卖家', dataIndex: 'seller_nickname', width: 120 },
  { title: '浏览', dataIndex: 'view_count', width: 80 },
  { title: '状态', dataIndex: 'status', width: 90 },
  { title: '操作', key: 'action', width: 140, fixed: 'right' as const },
]

async function load() {
  loading.value = true
  try {
    const res = await getAdminGoods({
      keyword: keyword.value,
      status: statusFilter.value,
      page: page.value,
      page_size: pageSize.value,
    })
    list.value = res.list
    total.value = res.total
  } finally {
    loading.value = false
  }
}

function onSearch() {
  page.value = 1
  load()
}

function onFilterChange() {
  page.value = 1
  load()
}

function onPageChange(p: { current?: number; pageSize?: number }) {
  page.value = p.current || 1
  pageSize.value = p.pageSize || 12
  load()
}

function onSelectChange(keys: number[]) {
  selectedRowKeys.value = keys
}

const totalText = (t: number) => `共 ${t} 件商品`

function onToggle(r: AdminGoods) {
  const off = r.status === 1
  Modal.confirm({
    title: off ? '确认下架该商品？' : '确认重新上架该商品？',
    content: `「${r.title}」${off ? '下架后前台不再展示' : '上架后将恢复前台展示'}。`,
    okType: off ? 'danger' : 'primary',
    async onOk() {
      await setGoodsStatus(r.id, off ? 3 : 1)
      message.success(off ? '已下架' : '已上架')
      load()
    },
  })
}

// 批量操作
function onBatchToggle(online: boolean) {
  Modal.confirm({
    title: online ? '确认批量上架？' : '确认批量下架？',
    content: `将对选中的 ${selectedRowKeys.value.length} 件商品执行${online ? '上架' : '下架'}操作。`,
    okType: online ? 'primary' : 'danger',
    async onOk() {
      message.success(`已批量${online ? '上架' : '下架'} ${selectedRowKeys.value.length} 件商品`)
      selectedRowKeys.value = []
      load()
    },
  })
}

onMounted(load)
</script>

<template>
  <div class="goods-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="page-header__left">
        <h1 class="page-header__title">
          <ShopOutlined />
          商品管理
        </h1>
        <p class="page-header__subtitle">审核与管理平台全部商品</p>
      </div>
      <div class="page-header__right">
        <a-radio-group v-model:value="viewMode" button-style="solid" class="view-toggle">
          <a-radio-button value="list"><BarsOutlined /> 列表</a-radio-button>
          <a-radio-button value="gallery"><AppstoreOutlined /> 画廊</a-radio-button>
        </a-radio-group>
      </div>
    </div>

    <!-- 筛选工具栏 -->
    <a-card class="filter-card" :bordered="false">
      <div class="filter-bar">
        <div class="filter-bar__left">
          <a-input-search
            v-model:value="keyword"
            placeholder="搜索商品标题 / 卖家昵称"
            class="filter-bar__search"
            allow-clear
            @search="onSearch"
          >
            <template #prefix><SearchOutlined style="color: #94a3b8" /></template>
          </a-input-search>
          <a-radio-group v-model:value="statusFilter" button-style="solid" @change="onFilterChange">
            <a-radio-button :value="undefined">全部</a-radio-button>
            <a-radio-button :value="1">在售</a-radio-button>
            <a-radio-button :value="2">已售</a-radio-button>
            <a-radio-button :value="3">已下架</a-radio-button>
          </a-radio-group>
        </div>
        <a-button @click="load">刷新</a-button>
      </div>
    </a-card>

    <!-- 批量操作栏 -->
    <div v-if="hasSelected" class="batch-bar">
      <span class="batch-bar__info">已选择 {{ selectedRowKeys.length }} 项</span>
      <a-space>
        <a-button size="small" @click="selectedRowKeys = []">取消选择</a-button>
        <a-button size="small" danger @click="onBatchToggle(false)">批量下架</a-button>
        <a-button size="small" type="primary" @click="onBatchToggle(true)">批量上架</a-button>
      </a-space>
    </div>

    <!-- 列表视图 -->
    <a-card v-if="viewMode === 'list'" class="table-card" :bordered="false">
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
        :row-selection="{ selectedRowKeys, onChange: onSelectChange }"
        row-key="id"
        size="middle"
        :scroll="{ x: 1000 }"
        @change="onPageChange"
      >
        <template #bodyCell="{ column, record }">
          <!-- 商品列 -->
          <template v-if="column.dataIndex === 'title'">
            <div class="goods-cell">
              <div class="goods-cell__img">
                <img v-if="record.images?.[0]" :src="record.images[0]" alt="" />
                <PictureOutlined v-else />
              </div>
              <div class="goods-cell__info">
                <div class="goods-cell__title">{{ record.title }}</div>
                <div class="goods-cell__id">ID: {{ record.id }}</div>
              </div>
            </div>
          </template>

          <!-- 售价列 -->
          <template v-else-if="column.dataIndex === 'sell_price'">
            <span class="price">¥{{ record.sell_price }}</span>
          </template>

          <!-- 浏览量列 -->
          <template v-else-if="column.dataIndex === 'view_count'">
            <span class="view-count">
              <EyeOutlined />
              {{ record.view_count }}
            </span>
          </template>

          <!-- 状态列 -->
          <template v-else-if="column.dataIndex === 'status'">
            <a-tag :color="statusMap[record.status]?.color" class="status-tag">
              {{ statusMap[record.status]?.text }}
            </a-tag>
          </template>

          <!-- 操作列 -->
          <template v-else-if="column.key === 'action'">
            <a-space :size="4">
              <a-button v-if="record.status === 1" size="small" type="text" danger @click="onToggle(record)">
                <template #icon><CloseCircleOutlined /></template>
                下架
              </a-button>
              <a-button v-else-if="record.status === 3" size="small" type="text" @click="onToggle(record)">
                <template #icon><CheckCircleOutlined /></template>
                上架
              </a-button>
              <span v-else class="sold-text">已售出</span>
            </a-space>
          </template>
        </template>
      </a-table>
    </a-card>

    <!-- 画廊视图 -->
    <template v-else>
      <a-spin :spinning="loading">
        <div class="gallery-grid">
          <div v-for="item in list" :key="item.id" class="gallery-card">
            <div class="gallery-card__img">
              <img v-if="item.images?.[0]" :src="item.images[0]" :alt="item.title" />
              <div v-else class="gallery-card__no-img"><PictureOutlined /></div>
              <div class="gallery-card__status" :style="{ background: statusMap[item.status]?.bg, color: statusMap[item.status]?.color }">
                {{ statusMap[item.status]?.text }}
              </div>
              <div class="gallery-card__overlay">
                <a-button size="small" type="primary" ghost @click="onToggle(item)">
                  {{ item.status === 1 ? '下架' : '上架' }}
                </a-button>
              </div>
            </div>
            <div class="gallery-card__content">
              <div class="gallery-card__title">{{ item.title }}</div>
              <div class="gallery-card__meta">
                <span class="gallery-card__price">¥{{ item.sell_price }}</span>
                <span class="gallery-card__seller">{{ item.seller_nickname }}</span>
              </div>
              <div class="gallery-card__footer">
                <span class="gallery-card__category">{{ item.category_name }}</span>
                <span class="gallery-card__views"><EyeOutlined /> {{ item.view_count }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 分页 -->
        <div class="gallery-pagination">
          <a-pagination
            v-model:current="page"
            v-model:page-size="pageSize"
            :total="total"
            :show-total="totalText"
            show-size-changer
            show-quick-jumper
            @change="load"
          />
        </div>
      </a-spin>
    </template>
  </div>
</template>

<style scoped>
.goods-page {
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
  color: #f59e0b;
}

.page-header__subtitle {
  margin: 4px 0 0;
  color: #64748b;
  font-size: 13px;
}

.view-toggle :deep(.ant-radio-button-wrapper) {
  border-radius: 8px !important;
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

.filter-bar__search :deep(.ant-input) {
  border-radius: 8px;
}

/* ===== 批量操作栏 ===== */
.batch-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #fffbeb;
  border: 1px solid #fcd34d;
  border-radius: 10px;
  margin-bottom: 16px;
}

.batch-bar__info {
  color: #b45309;
  font-size: 13px;
  font-weight: 500;
}

/* ===== 表格卡片 ===== */
.table-card {
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.table-card :deep(.ant-table-thead > tr > th) {
  background: #f8fafc;
  font-weight: 600;
  color: #475569;
}

.table-card :deep(.ant-table-tbody > tr:hover > td) {
  background: #f1f5f9;
}

/* ===== 商品单元格 ===== */
.goods-cell {
  display: flex;
  align-items: center;
  gap: 12px;
}

.goods-cell__img {
  width: 48px;
  height: 48px;
  border-radius: 10px;
  overflow: hidden;
  background: #f1f5f9;
  display: grid;
  place-items: center;
  color: #94a3b8;
  flex-shrink: 0;
}

.goods-cell__img img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.goods-cell__title {
  font-weight: 600;
  color: #1e293b;
  font-size: 14px;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.goods-cell__id {
  font-size: 11px;
  color: #94a3b8;
  margin-top: 2px;
}

/* ===== 价格/浏览量/状态 ===== */
.price {
  font-size: 16px;
  font-weight: 700;
  color: #f59e0b;
}

.view-count {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #64748b;
  font-size: 13px;
}

.status-tag {
  border-radius: 4px;
  font-size: 12px;
  border: none;
}

.sold-text {
  color: #cbd5e1;
  font-size: 12px;
}

/* ===== 画廊视图 ===== */
.gallery-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

.gallery-card {
  background: #fff;
  border-radius: 14px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
  transition: transform 0.2s, box-shadow 0.2s;
  cursor: pointer;
}

.gallery-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.12);
}

.gallery-card__img {
  position: relative;
  aspect-ratio: 4/3;
  background: #f1f5f9;
  overflow: hidden;
}

.gallery-card__img img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s;
}

.gallery-card:hover .gallery-card__img img {
  transform: scale(1.05);
}

.gallery-card__no-img {
  width: 100%;
  height: 100%;
  display: grid;
  place-items: center;
  font-size: 40px;
  color: #cbd5e1;
}

.gallery-card__status {
  position: absolute;
  top: 10px;
  left: 10px;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
}

.gallery-card__overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  display: grid;
  place-items: center;
  opacity: 0;
  transition: opacity 0.2s;
}

.gallery-card:hover .gallery-card__overlay {
  opacity: 1;
}

.gallery-card__content {
  padding: 16px;
}

.gallery-card__title {
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
  line-height: 1.4;
  margin-bottom: 10px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.gallery-card__meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.gallery-card__price {
  font-size: 18px;
  font-weight: 700;
  color: #f59e0b;
}

.gallery-card__seller {
  font-size: 12px;
  color: #64748b;
}

.gallery-card__footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: #94a3b8;
}

.gallery-card__category {
  background: #f1f5f9;
  padding: 2px 8px;
  border-radius: 4px;
}

.gallery-card__views {
  display: flex;
  align-items: center;
  gap: 4px;
}

.gallery-pagination {
  display: flex;
  justify-content: center;
  padding: 20px 0;
}

/* ===== 响应式 ===== */
@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .filter-bar {
    flex-direction: column;
    align-items: stretch;
  }

  .filter-bar__search {
    width: 100%;
  }

  .gallery-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
  }
}
</style>
