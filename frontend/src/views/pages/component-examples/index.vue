<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import {
  Alert as AAlert,
  Badge as ABadge,
  Button as AButton,
  Card as ACard,
  Divider as ADivider,
  Form as AForm,
  FormItem as AFormItem,
  Input as AInput,
  InputSearch as AInputSearch,
  Popover as APopover,
  Select as ASelect,
  SelectOption as ASelectOption,
  Space as ASpace,
  Switch as ASwitch,
  TabPane as ATabPane,
  Table as ATable,
  Tabs as ATabs,
  Textarea as ATextarea,
  Tooltip as ATooltip,
  message,
  type FormInstance,
  type FormProps,
  type TableColumnsType,
} from 'ant-design-vue'
import PageHeader from '@/components/common/PageHeader.vue'
import StatusBadge from '@/components/common/StatusBadge.vue'
import ConfirmAction from '@/components/common/ConfirmAction.vue'

interface FormModel { name: string; category?: string; enabled: boolean; description: string }
interface RowItem { key: number; name: string; status: 'enabled' | 'disabled'; owner: string }

const activeTab = ref('form')
const formRef = ref<FormInstance>()
const submitted = ref<FormModel | null>(null)
const form = reactive<FormModel>({ name: '', category: undefined, enabled: true, description: '' })
const rules: FormProps['rules'] = {
  name: [{ required: true, message: '请输入名称', trigger: 'blur' }],
  category: [{ required: true, message: '请选择分类', trigger: 'change' }],
}

const keyword = ref('')
const columns: TableColumnsType<RowItem> = [
  { title: '名称', dataIndex: 'name', key: 'name' },
  { title: '负责人', dataIndex: 'owner', key: 'owner' },
  { title: '状态', dataIndex: 'status', key: 'status' },
  { title: '操作', key: 'action', width: 120 },
]
const dataSource = ref<RowItem[]>([
  { key: 1, name: '通用方案 Alpha', owner: '张三', status: 'enabled' },
  { key: 2, name: '通用方案 Beta', owner: '李四', status: 'disabled' },
  { key: 3, name: '通用方案 Gamma', owner: '王五', status: 'enabled' },
])
const filteredRows = computed(() => dataSource.value.filter((row) => row.name.includes(keyword.value.trim())))

async function submitForm() {
  await formRef.value?.validate()
  submitted.value = { ...form }
  message.success('表单校验通过')
}

function removeRow(key: number) {
  dataSource.value = dataSource.value.filter((row) => row.key !== key)
  message.success('示例记录已删除')
}
</script>

<template>
  <main class="page-container">
    <PageHeader title="组件调用示例" description="包含表单、表格、反馈、弹窗及自定义组件的基础用法。" />

    <a-card :bordered="false">
      <a-tabs v-model:active-key="activeTab">
        <a-tab-pane key="form" tab="表单示例">
          <a-form ref="formRef" :model="form" :rules="rules" layout="vertical" class="example-form">
            <a-form-item label="名称" name="name"><a-input v-model:value="form.name" placeholder="请输入名称" /></a-form-item>
            <a-form-item label="分类" name="category">
              <a-select v-model:value="form.category" placeholder="请选择分类">
                <a-select-option value="frontend">前端</a-select-option>
                <a-select-option value="backend">后端</a-select-option>
                <a-select-option value="design">设计</a-select-option>
              </a-select>
            </a-form-item>
            <a-form-item label="启用状态"><a-switch v-model:checked="form.enabled" /></a-form-item>
            <a-form-item label="描述"><a-textarea v-model:value="form.description" :rows="3" show-count :maxlength="200" /></a-form-item>
            <a-space>
              <a-button type="primary" @click="submitForm">提交</a-button>
              <a-button @click="formRef?.resetFields()">重置</a-button>
            </a-space>
          </a-form>
          <a-alert v-if="submitted" class="result" type="success" show-icon :message="`提交结果：${JSON.stringify(submitted)}`" />
        </a-tab-pane>

        <a-tab-pane key="table" tab="表格示例">
          <a-input-search v-model:value="keyword" class="search" placeholder="按名称筛选" allow-clear />
          <a-table :columns="columns" :data-source="filteredRows" :pagination="{ pageSize: 5 }" :scroll="{ x: 620 }">
            <template #bodyCell="{ column, record }">
              <StatusBadge v-if="column.key === 'status'" :status="record.status" />
              <template v-else-if="column.key === 'action'">
                <ConfirmAction danger title="删除后无法恢复，确定吗？" @confirm="removeRow(record.key)" />
              </template>
            </template>
          </a-table>
        </a-tab-pane>

        <a-tab-pane key="feedback" tab="反馈示例">
          <a-space wrap>
            <a-button @click="message.info('这是一条信息')">Message</a-button>
            <a-popover title="Popover 标题" content="适合展示简短的补充信息。"><a-button>Popover</a-button></a-popover>
            <a-tooltip title="鼠标悬停提示"><a-button>Tooltip</a-button></a-tooltip>
            <a-badge :count="5"><a-button>Badge</a-button></a-badge>
          </a-space>
          <a-divider />
          <a-alert message="成功提示" description="组件示例不连接任何真实业务数据。" type="success" show-icon />
        </a-tab-pane>
      </a-tabs>
    </a-card>
  </main>
</template>

<style scoped>
.example-form { max-width: 620px; }
.result { margin-top: 16px; }
.search { width: min(320px, 100%); margin-bottom: 16px; }
</style>
