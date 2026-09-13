<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import {
  Button as AButton,
  Form as AForm,
  FormItem as AFormItem,
  Input as AInput,
  InputNumber as AInputNumber,
  message,
  Modal,
  Modal as AModal,
  Spin as ASpin,
} from 'ant-design-vue'
import {
  AppstoreOutlined,
  DeleteOutlined,
  EditOutlined,
  PlusOutlined,
} from '@ant-design/icons-vue'
import {
  getAdminCategories,
  createCategory,
  updateCategory,
  deleteCategory,
  type AdminCategory,
} from '@/common/apis/adminApi'

const loading = ref(false)
const list = ref<AdminCategory[]>([])

// 编辑弹窗
const editVisible = ref(false)
const saving = ref(false)
const editingId = ref<number | null>(null)
const form = reactive({ name: '', icon: '📦', sort: 0 })

// 图标库
const ICONS = [
  '💻', '📱', '📚', '👟', '🛏️', '⚽', '💄', '🎸', '📦', '🎧',
  '🖱️', '⌚', '🎮', '📷', '🚲', '🏀', '🎨', '🍔', '🌿', '💡',
]

// 预设颜色
const COLORS = [
  '#6366f1', '#8b5cf6', '#ec4899', '#f43f5e', '#f59e0b',
  '#10b981', '#06b6d4', '#3b82f6', '#84cc16', '#f97316',
]

async function load() {
  loading.value = true
  try {
    list.value = await getAdminCategories()
  } finally {
    loading.value = false
  }
}

function openCreate() {
  editingId.value = null
  form.name = ''
  form.icon = '📦'
  form.sort = list.value.length
  editVisible.value = true
}

function openEdit(c: AdminCategory) {
  editingId.value = c.id
  form.name = c.name
  form.icon = c.icon
  form.sort = c.sort
  editVisible.value = true
}

async function save() {
  if (!form.name.trim()) return message.warning('请输入分类名')
  saving.value = true
  try {
    if (editingId.value) {
      await updateCategory(editingId.value, { ...form })
      message.success('已保存')
    } else {
      await createCategory({ ...form })
      message.success('已新增')
    }
    editVisible.value = false
    load()
  } finally {
    saving.value = false
  }
}

function onDelete(c: AdminCategory) {
  Modal.confirm({
    title: '确认删除该分类？',
    content: c.goods_count > 0
      ? `该分类下有 ${c.goods_count} 件商品，删除会失败。请先移除或转移这些商品。`
      : `删除「${c.name}」后不可恢复。`,
    okType: 'danger',
    async onOk() {
      try {
        await deleteCategory(c.id)
        message.success('已删除')
        load()
      } catch (e) {
        message.error((e as Error).message || '删除失败')
      }
    },
  })
}

// 根据分类名生成颜色
function getColor(name: string, index: number) {
  return COLORS[index % COLORS.length]
}

onMounted(load)
</script>

<template>
  <div class="category-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="page-header__left">
        <h1 class="page-header__title">
          <AppstoreOutlined />
          分类管理
        </h1>
        <p class="page-header__subtitle">维护商品分类体系，优化用户浏览体验</p>
      </div>
      <a-button type="primary" class="page-header__btn" @click="openCreate">
        <template #icon><PlusOutlined /></template>
        新增分类
      </a-button>
    </div>

    <!-- 统计信息 -->
    <div class="stats-bar">
      <div class="stats-bar__item">
        <span class="stats-bar__value">{{ list.length }}</span>
        <span class="stats-bar__label">分类总数</span>
      </div>
      <div class="stats-bar__item">
        <span class="stats-bar__value">{{ list.reduce((sum, c) => sum + c.goods_count, 0) }}</span>
        <span class="stats-bar__label">商品总数</span>
      </div>
    </div>

    <!-- 分类卡片 -->
    <a-spin :spinning="loading">
      <div class="category-grid">
        <div
          v-for="(item, index) in list"
          :key="item.id"
          class="category-card"
          :style="{ '--accent-color': getColor(item.name, index) }"
        >
          <div class="category-card__header">
            <div class="category-card__icon" :style="{ background: getColor(item.name, index) + '15' }">
              {{ item.icon }}
            </div>
            <div class="category-card__actions">
              <a-button size="small" type="text" @click="openEdit(item)">
                <template #icon><EditOutlined /></template>
              </a-button>
              <a-button
                size="small"
                type="text"
                danger
                :disabled="item.goods_count > 0"
                @click="onDelete(item)"
              >
                <template #icon><DeleteOutlined /></template>
              </a-button>
            </div>
          </div>
          <div class="category-card__content">
            <div class="category-card__name">{{ item.name }}</div>
            <div class="category-card__meta">
              <span class="category-card__count">{{ item.goods_count }} 件商品</span>
              <span class="category-card__sort">排序 {{ item.sort }}</span>
            </div>
          </div>
          <div class="category-card__bar" :style="{ background: getColor(item.name, index) }"></div>
        </div>

        <!-- 新增卡片 -->
        <div class="category-card category-card--add" @click="openCreate">
          <PlusOutlined class="category-card--add__icon" />
          <span class="category-card--add__text">新增分类</span>
        </div>
      </div>
    </a-spin>

    <!-- 编辑弹窗 -->
    <a-modal
      v-model:open="editVisible"
      :title="editingId ? '编辑分类' : '新增分类'"
      :confirm-loading="saving"
      @ok="save"
    >
      <a-form layout="vertical">
        <a-form-item label="分类名" required>
          <a-input
            v-model:value="form.name"
            :maxlength="32"
            placeholder="如：数码电子"
            size="large"
          />
        </a-form-item>
        <a-form-item label="选择图标">
          <div class="icon-picker">
            <span
              v-for="ic in ICONS"
              :key="ic"
              class="icon-option"
              :class="{ active: form.icon === ic }"
              @click="form.icon = ic"
            >
              {{ ic }}
            </span>
          </div>
        </a-form-item>
        <a-form-item label="排序权重（越小越靠前）">
          <a-input-number v-model:value="form.sort" :min="0" style="width: 100%" size="large" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<style scoped>
.category-page {
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
  color: #06b6d4;
}

.page-header__subtitle {
  margin: 4px 0 0;
  color: #64748b;
  font-size: 13px;
}

.page-header__btn {
  border-radius: 8px;
}

/* ===== 统计栏 ===== */
.stats-bar {
  display: flex;
  gap: 32px;
  margin-bottom: 24px;
  padding: 20px 24px;
  background: linear-gradient(135deg, #f0f9ff, #e0f2fe);
  border-radius: 12px;
}

.stats-bar__item {
  display: flex;
  flex-direction: column;
}

.stats-bar__value {
  font-size: 28px;
  font-weight: 700;
  color: #0369a1;
  line-height: 1.2;
}

.stats-bar__label {
  font-size: 13px;
  color: #64748b;
  margin-top: 4px;
}

/* ===== 分类卡片网格 ===== */
.category-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
}

.category-card {
  position: relative;
  background: #fff;
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
  transition: transform 0.2s, box-shadow 0.2s;
  overflow: hidden;
}

.category-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.12);
}

.category-card__header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.category-card__icon {
  width: 56px;
  height: 56px;
  border-radius: 14px;
  display: grid;
  place-items: center;
  font-size: 28px;
}

.category-card__actions {
  display: flex;
  gap: 4px;
  opacity: 0;
  transition: opacity 0.2s;
}

.category-card:hover .category-card__actions {
  opacity: 1;
}

.category-card__name {
  font-size: 16px;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 8px;
}

.category-card__meta {
  display: flex;
  gap: 12px;
  font-size: 12px;
  color: #64748b;
}

.category-card__count {
  font-weight: 500;
}

.category-card__bar {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 4px;
  opacity: 0.8;
}

/* 新增卡片 */
.category-card--add {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  min-height: 160px;
  border: 2px dashed #cbd5e1;
  background: #f8fafc;
  cursor: pointer;
  transition: all 0.2s;
}

.category-card--add:hover {
  border-color: #6366f1;
  background: #eff6ff;
}

.category-card--add__icon {
  font-size: 32px;
  color: #94a3b8;
}

.category-card--add:hover .category-card--add__icon {
  color: #6366f1;
}

.category-card--add__text {
  font-size: 14px;
  color: #64748b;
  font-weight: 500;
}

.category-card--add:hover .category-card--add__text {
  color: #6366f1;
}

/* ===== 图标选择器 ===== */
.icon-picker {
  display: grid;
  grid-template-columns: repeat(10, 1fr);
  gap: 8px;
}

.icon-option {
  width: 40px;
  height: 40px;
  display: grid;
  place-items: center;
  font-size: 20px;
  border: 2px solid #e2e8f0;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.15s;
}

.icon-option:hover {
  border-color: #6366f1;
  transform: scale(1.1);
}

.icon-option.active {
  border-color: #6366f1;
  background: #eff6ff;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15);
}

/* ===== 响应式 ===== */
@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .category-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
  }

  .icon-picker {
    grid-template-columns: repeat(5, 1fr);
  }
}
</style>
