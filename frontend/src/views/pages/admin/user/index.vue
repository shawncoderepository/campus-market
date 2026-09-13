<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import {
  Avatar as AAvatar,
  Badge as ABadge,
  Button as AButton,
  Card as ACard,
  InputNumber as AInputNumber,
  InputSearch as AInputSearch,
  message,
  Modal,
  Popover as APopover,
  RadioButton as ARadioButton,
  RadioGroup as ARadioGroup,
  Slider as ASlider,
  Space as ASpace,
  Table as ATable,
  Tag as ATag,
  Tooltip as ATooltip,
} from 'ant-design-vue'
import {
  CheckCircleOutlined,
  CloseCircleOutlined,
  EditOutlined,
  SearchOutlined,
  TeamOutlined,
  UserOutlined,
} from '@ant-design/icons-vue'
import { getAdminUsers, setUserStatus, setUserCredit, type AdminUser } from '@/common/apis/adminApi'

const loading = ref(false)
const list = ref<AdminUser[]>([])
const total = ref(0)
const keyword = ref('')
const roleFilter = ref<number | undefined>(undefined)
const statusFilter = ref<number | undefined>(undefined)
const page = ref(1)
const pageSize = ref(10)

// 信用分弹窗
const creditVisible = ref(false)
const creditValue = ref(100)
const currentUser = ref<AdminUser | null>(null)
const saving = ref(false)

// 批量选择
const selectedRowKeys = ref<number[]>([])

const columns = [
  { title: '用户', dataIndex: 'nickname', width: 220 },
  { title: '学号', dataIndex: 'student_no', width: 120 },
  { title: '手机号', dataIndex: 'phone', width: 130 },
  { title: '信用分', dataIndex: 'credit_score', width: 110 },
  { title: '角色', dataIndex: 'role', width: 90 },
  { title: '状态', dataIndex: 'status', width: 90 },
  { title: '注册时间', dataIndex: 'created_at', width: 160 },
  { title: '操作', key: 'action', width: 180, fixed: 'right' as const },
]

const hasSelected = computed(() => selectedRowKeys.value.length > 0)

async function load() {
  loading.value = true
  try {
    const data = await getAdminUsers({
      keyword: keyword.value,
      role: roleFilter.value,
      status: statusFilter.value,
      page: page.value,
      page_size: pageSize.value,
    })
    list.value = data.list
    total.value = data.total
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
  pageSize.value = p.pageSize || 10
  load()
}

function onSelectChange(keys: (string | number)[]) {
  selectedRowKeys.value = keys.map(Number)
}

const totalText = (t: number) => `共 ${t} 位用户`

// antd bodyCell 的 record 推断为 Record<string, any>，此处断言为 AdminUser
const asUser = (r: Record<string, unknown>) => r as unknown as AdminUser

function onToggleStatus(u: AdminUser) {
  const action = u.status === 1 ? '禁用' : '启用'
  Modal.confirm({
    title: `确认${action}该用户？`,
    content: `用户「${u.nickname || u.username}」${action}后将${u.status === 1 ? '无法登录平台' : '恢复正常使用'}。`,
    okType: u.status === 1 ? 'danger' : 'primary',
    async onOk() {
      await setUserStatus(u.id, u.status === 1 ? 0 : 1)
      message.success(`已${action}用户「${u.nickname || u.username}」`)
      load()
    },
  })
}

function openCredit(u: AdminUser) {
  currentUser.value = u
  creditValue.value = u.credit_score
  creditVisible.value = true
}

function closeCredit() {
  creditVisible.value = false
  currentUser.value = null
}

async function saveCredit() {
  if (!currentUser.value) return
  saving.value = true
  try {
    await setUserCredit(currentUser.value.id, creditValue.value)
    message.success('信用分已更新')
    closeCredit()
    load()
  } finally {
    saving.value = false
  }
}

// 信用分颜色
function creditColor(score: number) {
  if (score >= 90) return '#10b981'
  if (score >= 70) return '#6366f1'
  if (score >= 50) return '#f59e0b'
  return '#ef4444'
}

// 信用分标签
function creditLabel(score: number) {
  if (score >= 90) return '优秀'
  if (score >= 70) return '良好'
  if (score >= 50) return '一般'
  return '较差'
}

onMounted(load)
</script>

<template>
  <div class="user-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="page-header__left">
        <h1 class="page-header__title">
          <TeamOutlined />
          用户管理
        </h1>
        <p class="page-header__subtitle">管理平台注册用户，维护用户信用体系</p>
      </div>
      <div class="page-header__right">
        <a-button type="primary" class="page-header__btn">
          <template #icon><UserOutlined /></template>
          导出用户
        </a-button>
      </div>
    </div>

    <!-- 筛选工具栏 -->
    <a-card class="filter-card" :bordered="false">
      <div class="filter-bar">
        <div class="filter-bar__left">
          <a-input-search
            v-model:value="keyword"
            placeholder="搜索用户名 / 昵称 / 学号 / 手机号"
            class="filter-bar__search"
            allow-clear
            @search="onSearch"
          >
            <template #prefix><SearchOutlined style="color: #94a3b8" /></template>
          </a-input-search>
          <a-radio-group v-model:value="roleFilter" button-style="solid" class="filter-bar__group" @change="onFilterChange">
            <a-radio-button :value="undefined">全部角色</a-radio-button>
            <a-radio-button :value="1">普通用户</a-radio-button>
            <a-radio-button :value="2">管理员</a-radio-button>
          </a-radio-group>
          <a-radio-group v-model:value="statusFilter" button-style="solid" class="filter-bar__group" @change="onFilterChange">
            <a-radio-button :value="undefined">全部状态</a-radio-button>
            <a-radio-button :value="1">正常</a-radio-button>
            <a-radio-button :value="0">已禁用</a-radio-button>
          </a-radio-group>
        </div>
        <a-button @click="load">刷新</a-button>
      </div>
    </a-card>

    <!-- 用户表格 -->
    <a-card class="table-card" :bordered="false">
      <!-- 批量操作栏 -->
      <div v-if="hasSelected" class="batch-bar">
        <span class="batch-bar__info">已选择 {{ selectedRowKeys.length }} 项</span>
        <a-space>
          <a-button size="small" @click="selectedRowKeys = []">取消选择</a-button>
          <a-button size="small" danger>批量禁用</a-button>
          <a-button size="small" type="primary">批量启用</a-button>
        </a-space>
      </div>

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
        :scroll="{ x: 1200 }"
        @change="onPageChange"
      >
        <template #bodyCell="{ column, record }">
          <!-- 用户列 -->
          <template v-if="column.dataIndex === 'nickname'">
            <div class="user-cell">
              <a-avatar
                :size="40"
                :src="record.avatar || undefined"
                class="user-cell__avatar"
              >
                {{ (record.nickname || record.username).slice(0, 1) }}
              </a-avatar>
              <div class="user-cell__info">
                <div class="user-cell__name">{{ record.nickname || record.username }}</div>
                <div class="user-cell__username">@{{ record.username }}</div>
              </div>
            </div>
          </template>

          <!-- 信用分列 -->
          <template v-else-if="column.dataIndex === 'credit_score'">
            <div class="credit-cell">
              <div class="credit-cell__score" :style="{ color: creditColor(record.credit_score) }">
                {{ record.credit_score }}
              </div>
              <a-tag :color="creditColor(record.credit_score)" class="credit-cell__tag">
                {{ creditLabel(record.credit_score) }}
              </a-tag>
            </div>
          </template>

          <!-- 角色列 -->
          <template v-else-if="column.dataIndex === 'role'">
            <a-tag :color="record.role === 2 ? 'purple' : 'blue'" class="role-tag">
              {{ record.role === 2 ? '管理员' : '用户' }}
            </a-tag>
          </template>

          <!-- 状态列 -->
          <template v-else-if="column.dataIndex === 'status'">
            <a-badge
              :status="record.status === 1 ? 'success' : 'error'"
              :text="record.status === 1 ? '正常' : '禁用'"
            />
          </template>

          <!-- 操作列 -->
          <template v-else-if="column.key === 'action'">
            <a-space :size="8">
              <a-popover
                :open="creditVisible && currentUser?.id === record.id"
                trigger="click"
                placement="left"
                title="调整信用分"
                @update:open="(v: boolean) => (v ? openCredit(asUser(record)) : closeCredit())"
              >
                <template #content>
                  <div class="credit-pop">
                    <div class="credit-pop__current">
                      当前：<span :style="{ color: creditColor(record.credit_score) }">{{ record.credit_score }}</span>
                    </div>
                    <a-slider v-model:value="creditValue" :min="0" :max="100" class="credit-pop__slider" />
                    <a-input-number v-model:value="creditValue" :min="0" :max="100" size="small" style="width: 100%" />
                    <div class="credit-pop__actions">
                      <a-button size="small" @click="closeCredit">取消</a-button>
                      <a-button size="small" type="primary" :loading="saving" @click="saveCredit">确定</a-button>
                    </div>
                  </div>
                </template>
                <a-tooltip title="调整信用分">
                  <a-button size="small" type="text" @click.stop="openCredit(asUser(record))">
                    <template #icon><EditOutlined /></template>
                    调信用
                  </a-button>
                </a-tooltip>
              </a-popover>
              <a-tooltip v-if="record.role !== 2" :title="record.status === 1 ? '禁用该用户' : '启用该用户'">
                <a-button
                  size="small"
                  type="text"
                  :danger="record.status === 1"
                  @click="onToggleStatus(asUser(record))"
                >
                  <template #icon>
                    <CloseCircleOutlined v-if="record.status === 1" />
                    <CheckCircleOutlined v-else />
                  </template>
                  {{ record.status === 1 ? '禁用' : '启用' }}
                </a-button>
              </a-tooltip>
            </a-space>
          </template>
        </template>
      </a-table>
    </a-card>

  </div>
</template>

<style scoped>
.user-page {
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
  color: #6366f1;
}

.page-header__subtitle {
  margin: 4px 0 0;
  color: #64748b;
  font-size: 13px;
}

.page-header__btn {
  border-radius: 8px;
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

.filter-bar__group :deep(.ant-radio-button-wrapper) {
  border-radius: 8px !important;
}

/* ===== 表格卡片 ===== */
.table-card {
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.table-card :deep(.ant-table) {
  border-radius: 8px;
}

.table-card :deep(.ant-table-thead > tr > th) {
  background: #f8fafc;
  font-weight: 600;
  color: #475569;
}

.table-card :deep(.ant-table-tbody > tr:hover > td) {
  background: #f1f5f9;
}

/* ===== 批量操作栏 ===== */
.batch-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  border-radius: 8px;
  margin-bottom: 16px;
}

.batch-bar__info {
  color: #1d4ed8;
  font-size: 13px;
  font-weight: 500;
}

/* ===== 用户单元格 ===== */
.user-cell {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-cell__avatar {
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  flex-shrink: 0;
}

.user-cell__name {
  font-weight: 600;
  color: #1e293b;
  font-size: 14px;
}

.user-cell__username {
  font-size: 12px;
  color: #94a3b8;
}

/* ===== 信用分单元格 ===== */
.credit-cell {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.credit-cell__score {
  font-size: 20px;
  font-weight: 700;
  line-height: 1;
}

.credit-cell__tag {
  width: fit-content;
  border-radius: 4px;
  font-size: 11px;
}

/* ===== 角色标签 ===== */
.role-tag {
  border-radius: 4px;
  font-size: 12px;
}

/* ===== 信用分弹层 ===== */
.credit-pop {
  width: 240px;
}

.credit-pop__current {
  font-size: 13px;
  color: #64748b;
  margin-bottom: 8px;
}

.credit-pop__slider {
  margin-bottom: 10px;
}

.credit-pop__actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 12px;
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
}
</style>
