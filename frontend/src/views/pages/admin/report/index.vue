<script setup lang="ts">
import { onMounted, ref } from 'vue'
import {
  Badge as ABadge,
  Button as AButton,
  Card as ACard,
  Form as AForm,
  FormItem as AFormItem,
  InputSearch as AInputSearch,
  message,
  Modal as AModal,
  Radio as ARadio,
  RadioButton as ARadioButton,
  RadioGroup as ARadioGroup,
  Space as ASpace,
  Table as ATable,
  Tag as ATag,
  Textarea as ATextarea,
} from 'ant-design-vue'
import {
  CheckCircleOutlined,
  CloseCircleOutlined,
  ExclamationCircleOutlined,
  EyeOutlined,
  FlagOutlined,
  SearchOutlined,
  WarningOutlined,
} from '@ant-design/icons-vue'
import { getAdminReports, handleReport, type AdminReport } from '@/common/apis/adminApi'
import { REPORT_REASON_TYPES } from '@/common/apis/reportApi'

const loading = ref(false)
const list = ref<AdminReport[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)
const statusFilter = ref<number | undefined>(undefined)

// 处理弹窗
const handleVisible = ref(false)
const saving = ref(false)
const current = ref<AdminReport | null>(null)
const handleStatus = ref(2)
const handleResult = ref('')

// 详情弹窗
const detailVisible = ref(false)
const detail = ref<AdminReport | null>(null)

function openDetail(r: AdminReport) {
  detail.value = r
  detailVisible.value = true
}

// 处理理由模板：按违规类型给出“举报成立”默认理由；不成立用统一模板
const APPROVE_TEMPLATES: Record<string, string> = {
  counterfeit: '经核实，该商品为假冒/盗版物品，违反平台规定，已予以下架处理。',
  false_info: '经核实，该商品描述与实物严重不符，存在误导，已予以下架处理。',
  prohibited: '经核实，该商品属于平台禁售的违禁/违规物品，已予以下架处理。',
  fraud: '经核实，该商品涉嫌诈骗或诱导线下交易，存在安全风险，已予以下架处理。',
  price_abuse: '经核实，该商品价格异常、涉嫌恶意抬价，扰乱交易秩序，已予以下架处理。',
  spam: '经核实，该商品为垃圾广告/恶意刷屏，已予以下架处理。',
  other: '经核实，该商品存在违规行为，违反平台规定，已予以下架处理。',
}
const REJECT_TEMPLATE = '经核实，暂未发现该商品存在违规行为，举报不成立，商品保持正常在售。'

function applyTemplate() {
  if (!current.value) return
  handleResult.value = handleStatus.value === 2
    ? (APPROVE_TEMPLATES[current.value.reason_type] || APPROVE_TEMPLATES.other)
    : REJECT_TEMPLATE
}

const statusMap: Record<number, { text: string; color: string; icon: unknown }> = {
  1: { text: '待处理', color: '#f59e0b', icon: WarningOutlined },
  2: { text: '已处理', color: '#10b981', icon: CheckCircleOutlined },
  3: { text: '已驳回', color: '#94a3b8', icon: CloseCircleOutlined },
}

const columns = [
  { title: 'ID', dataIndex: 'id', width: 60 },
  { title: '举报人', dataIndex: 'reporter_nickname', width: 110 },
  { title: '被举报者', dataIndex: 'seller_nickname', width: 110 },
  { title: '被举报商品', dataIndex: 'product_title', ellipsis: true },
  { title: '违规类型', dataIndex: 'reason_type_name', width: 150 },
  { title: '补充说明', dataIndex: 'reason', ellipsis: true },
  { title: '状态', dataIndex: 'status', width: 110 },
  { title: '处理结果', dataIndex: 'handler_result', ellipsis: true },
  { title: '举报时间', dataIndex: 'created_at', width: 160 },
  { title: '操作', key: 'action', width: 110, fixed: 'right' as const },
]

async function load() {
  loading.value = true
  try {
    const res = await getAdminReports({ status: statusFilter.value, page: page.value, page_size: pageSize.value })
    list.value = res.list
    total.value = res.total
  } finally {
    loading.value = false
  }
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

const totalText = (t: number) => `共 ${t} 条举报`

function openHandle(r: AdminReport) {
  current.value = r
  handleStatus.value = 2
  handleResult.value = APPROVE_TEMPLATES[r.reason_type] || APPROVE_TEMPLATES.other
  handleVisible.value = true
}

function onStatusChange() {
  applyTemplate()
}

async function saveHandle() {
  if (!current.value) return
  saving.value = true
  try {
    await handleReport(current.value.id, { status: handleStatus.value, handler_result: handleResult.value })
    message.success('处理完成')
    handleVisible.value = false
    load()
  } finally {
    saving.value = false
  }
}

// 举报原因标签颜色
function reasonColor(reason: string) {
  if (reason.includes('诈骗') || reason.includes('虚假')) return '#ef4444'
  if (reason.includes('色情') || reason.includes('违规')) return '#dc2626'
  if (reason.includes('广告') || reason.includes('垃圾')) return '#f59e0b'
  return '#6366f1'
}

onMounted(load)
</script>

<template>
  <div class="report-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="page-header__left">
        <h1 class="page-header__title">
          <FlagOutlined />
          举报处理
        </h1>
        <p class="page-header__subtitle">处理用户举报，维护平台交易安全</p>
      </div>
      <div class="page-header__right">
        <a-badge :count="list.filter(r => r.status === 1).length" :offset="[-5, 5]">
          <a-button type="primary" danger class="page-header__btn">
            <template #icon><ExclamationCircleOutlined /></template>
            待处理举报
          </a-button>
        </a-badge>
      </div>
    </div>

    <!-- 筛选工具栏 -->
    <a-card class="filter-card" :bordered="false">
      <div class="filter-bar">
        <div class="filter-bar__left">
          <a-input-search
            placeholder="搜索举报人 / 商品 / 原因"
            class="filter-bar__search"
            allow-clear
            @search="load"
          >
            <template #prefix><SearchOutlined style="color: #94a3b8" /></template>
          </a-input-search>
          <a-radio-group v-model:value="statusFilter" button-style="solid" @change="onFilterChange">
            <a-radio-button :value="undefined">全部</a-radio-button>
            <a-radio-button :value="1">待处理</a-radio-button>
            <a-radio-button :value="2">已处理</a-radio-button>
            <a-radio-button :value="3">已驳回</a-radio-button>
          </a-radio-group>
        </div>
        <a-button @click="load">刷新</a-button>
      </div>
    </a-card>

    <!-- 举报表格 -->
    <a-card class="table-card" :bordered="false">
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
        row-key="id"
        size="middle"
        :scroll="{ x: 1200 }"
        @change="onPageChange"
      >
        <template #bodyCell="{ column, record }">
          <!-- 违规类型列 -->
          <template v-if="column.dataIndex === 'reason_type_name'">
            <a-tag :color="reasonColor(record.reason_type_name || record.reason)" class="reason-tag">
              {{ record.reason_type_name || record.reason }}
            </a-tag>
          </template>

          <!-- 补充说明列 -->
          <template v-else-if="column.dataIndex === 'reason'">
            <span class="reason-text">{{ record.reason || '-' }}</span>
          </template>

          <!-- 状态列 -->
          <template v-else-if="column.dataIndex === 'status'">
            <div class="status-cell">
              <span class="status-cell__icon" :style="{ color: statusMap[record.status]?.color }">
                <component :is="statusMap[record.status]?.icon" />
              </span>
              <span class="status-cell__text" :style="{ color: statusMap[record.status]?.color }">
                {{ statusMap[record.status]?.text }}
              </span>
            </div>
          </template>

          <!-- 处理结果列 -->
          <template v-else-if="column.dataIndex === 'handler_result'">
            <span class="result-text">{{ record.handler_result || '-' }}</span>
          </template>

          <!-- 操作列 -->
          <template v-else-if="column.key === 'action'">
            <a-space :size="4">
              <a-button v-if="record.status === 1" size="small" type="primary" @click="openHandle(record)">
                处理
              </a-button>
              <a-button v-else size="small" type="text" @click="openDetail(record)">
                <template #icon><EyeOutlined /></template>
                查看
              </a-button>
            </a-space>
          </template>
        </template>
      </a-table>
    </a-card>

    <!-- 处理弹窗 -->
    <a-modal
      v-model:open="handleVisible"
      title="处理举报"
      :confirm-loading="saving"
      @ok="saveHandle"
    >
      <div class="handle-modal">
        <!-- 举报信息 -->
        <div class="handle-modal__info">
          <div class="handle-modal__row">
            <span class="handle-modal__label">被举报商品：</span>
            <span class="handle-modal__value">{{ current?.product_title }}</span>
          </div>
          <div class="handle-modal__row">
            <span class="handle-modal__label">举报人：</span>
            <span class="handle-modal__value">{{ current?.reporter_nickname }}</span>
          </div>
          <div class="handle-modal__row">
            <span class="handle-modal__label">被举报者：</span>
            <span class="handle-modal__value">{{ current?.seller_nickname || '-' }}</span>
          </div>
          <div class="handle-modal__row">
            <span class="handle-modal__label">违规类型：</span>
            <a-tag :color="reasonColor(current?.reason_type_name || '')">{{ current?.reason_type_name }}</a-tag>
          </div>
          <div v-if="current?.reason" class="handle-modal__row">
            <span class="handle-modal__label">补充说明：</span>
            <span class="handle-modal__value">{{ current?.reason }}</span>
          </div>
        </div>

        <!-- 处理表单 -->
        <a-form layout="vertical" class="handle-modal__form">
          <a-form-item label="处理结论">
            <a-radio-group v-model:value="handleStatus" class="handle-modal__radio" @change="onStatusChange">
              <a-radio :value="2" class="handle-modal__radio-item">
                <div class="radio-content">
                  <CheckCircleOutlined style="color: #10b981" />
                  <div>
                    <div class="radio-content__title">举报成立</div>
                    <div class="radio-content__desc">下架商品 / 警告卖家</div>
                  </div>
                </div>
              </a-radio>
              <a-radio :value="3" class="handle-modal__radio-item">
                <div class="radio-content">
                  <CloseCircleOutlined style="color: #94a3b8" />
                  <div>
                    <div class="radio-content__title">举报不成立</div>
                    <div class="radio-content__desc">驳回举报，商品保持正常</div>
                  </div>
                </div>
              </a-radio>
            </a-radio-group>
          </a-form-item>
          <a-form-item label="处理说明">
            <a-textarea
              v-model:value="handleResult"
              :rows="4"
              placeholder="已按违规类型自动填入模板，可直接修改"
              :maxlength="255"
              show-count
            />
            <div class="handle-modal__hint">
              {{ handleStatus === 2
                ? '提交后将：自动下架该商品，并通过系统消息同时通知举报者与被举报者。'
                : '提交后将：仅通过系统消息通知举报者（不打扰被举报者），商品保持正常。' }}
            </div>
          </a-form-item>
        </a-form>
      </div>
    </a-modal>

    <!-- 详情弹窗（只读） -->
    <a-modal v-model:open="detailVisible" title="举报详情" :footer="null" width="560px">
      <div v-if="detail" class="handle-modal__info" style="margin-bottom:0">
        <div class="handle-modal__row">
          <span class="handle-modal__label">举报编号：</span>
          <span class="handle-modal__value">#{{ detail.id }}</span>
        </div>
        <div class="handle-modal__row">
          <span class="handle-modal__label">被举报商品：</span>
          <span class="handle-modal__value">{{ detail.product_title }}</span>
        </div>
        <div class="handle-modal__row">
          <span class="handle-modal__label">举报人：</span>
          <span class="handle-modal__value">{{ detail.reporter_nickname }}</span>
        </div>
        <div class="handle-modal__row">
          <span class="handle-modal__label">被举报者：</span>
          <span class="handle-modal__value">{{ detail.seller_nickname || '-' }}</span>
        </div>
        <div class="handle-modal__row">
          <span class="handle-modal__label">违规类型：</span>
          <a-tag :color="reasonColor(detail.reason_type_name || detail.reason)">{{ detail.reason_type_name }}</a-tag>
        </div>
        <div v-if="detail.reason" class="handle-modal__row">
          <span class="handle-modal__label">补充说明：</span>
          <span class="handle-modal__value">{{ detail.reason }}</span>
        </div>
        <div class="handle-modal__row">
          <span class="handle-modal__label">状态：</span>
          <span class="status-cell">
            <span class="status-cell__icon" :style="{ color: statusMap[detail.status]?.color }">
              <component :is="statusMap[detail.status]?.icon" />
            </span>
            <span class="status-cell__text" :style="{ color: statusMap[detail.status]?.color }">
              {{ statusMap[detail.status]?.text }}
            </span>
          </span>
        </div>
        <div v-if="detail.handler_result" class="handle-modal__row">
          <span class="handle-modal__label">处理结果：</span>
          <span class="handle-modal__value">{{ detail.handler_result }}</span>
        </div>
        <div class="handle-modal__row">
          <span class="handle-modal__label">举报时间：</span>
          <span class="handle-modal__value">{{ detail.created_at }}</span>
        </div>
      </div>
    </a-modal>
  </div>
</template>

<style scoped>
.report-page {
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
  color: #ef4444;
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

/* ===== 表格 ===== */
.table-card {
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.table-card :deep(.ant-table-thead > tr > th) {
  background: #f8fafc;
  font-weight: 600;
  color: #475569;
}

/* ===== 原因标签 ===== */
.reason-tag {
  border-radius: 4px;
  font-size: 12px;
}

/* ===== 状态单元格 ===== */
.status-cell {
  display: flex;
  align-items: center;
  gap: 6px;
}

.status-cell__icon {
  font-size: 14px;
}

.status-cell__text {
  font-size: 13px;
  font-weight: 500;
}

/* ===== 结果文本 ===== */
.result-text {
  color: #64748b;
  font-size: 13px;
}

/* ===== 处理弹窗 ===== */
.handle-modal__info {
  background: #f8fafc;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 20px;
}

.handle-modal__row {
  display: flex;
  margin-bottom: 8px;
  font-size: 14px;
}

.handle-modal__row:last-child {
  margin-bottom: 0;
}

.handle-modal__label {
  color: #64748b;
  width: 90px;
  flex-shrink: 0;
}

.handle-modal__value {
  color: #1e293b;
  font-weight: 500;
}

/* 单选样式 */
.handle-modal__radio {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.handle-modal__radio-item {
  padding: 16px;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  transition: all 0.2s;
  margin-right: 0;
}

.handle-modal__radio-item:hover {
  border-color: #6366f1;
}

.handle-modal__radio-item :deep(.ant-radio) {
  display: none;
}

.handle-modal__radio-item :deep(.ant-radio-wrapper-checked) {
  border-color: #6366f1;
  background: #eff6ff;
}

.radio-content {
  display: flex;
  align-items: center;
  gap: 12px;
}

.radio-content__title {
  font-weight: 600;
  color: #1e293b;
  font-size: 14px;
}

.radio-content__desc {
  font-size: 12px;
  color: #94a3b8;
  margin-top: 2px;
}

.handle-modal__hint {
  margin-top: 8px;
  font-size: 12px;
  color: #f59e0b;
  background: #fffbeb;
  border: 1px solid #fde68a;
  border-radius: 8px;
  padding: 8px 12px;
  line-height: 1.5;
}

.reason-text {
  color: #64748b;
  font-size: 13px;
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
