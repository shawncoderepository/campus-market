<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import {
  Button as AButton,
  Card as ACard,
  Form as AForm,
  FormItem as AFormItem,
  Input as AInput,
  InputNumber as AInputNumber,
  message,
  Select as ASelect,
  SelectOption as ASelectOption,
  Textarea as ATextarea,
  Upload as AUpload,
} from 'ant-design-vue'
import { DeleteOutlined, LoadingOutlined, PlusOutlined, RobotOutlined } from '@ant-design/icons-vue'
import { getCategories, publishGoods, uploadImage } from '@/common/apis/goodsApi'
import { aiCopy, aiEstimate } from '@/common/apis/aiApi'
import type { Category } from '@/common/types/business'

const router = useRouter()
const categories = ref<Category[]>([])
const submitting = ref(false)
const aiCopyLoading = ref(false)
const aiEstimateLoading = ref(false)
const imageUrls = ref<string[]>([])
const uploadLoading = ref(false)
const estimateTip = ref('')

const form = reactive({
  keywords: '',
  category_id: undefined as number | undefined,
  title: '',
  description: '',
  original_price: undefined as number | undefined,
  sell_price: undefined as number | undefined,
  condition_level: 3,
  used_years: 1,
})

async function loadCategories() {
  try {
    categories.value = await getCategories()
  } catch { /* 已提示 */ }
}

function categoryName(): string {
  return categories.value.find((c) => c.id === form.category_id)?.name || '其他'
}

async function onAiCopy() {
  if (!form.keywords.trim()) return message.warning('请先填写商品关键词（用于 AI 生成文案）')
  aiCopyLoading.value = true
  try {
    const res = await aiCopy({
      keywords: form.keywords,
      category_name: categoryName(),
      condition_level: form.condition_level,
      original_price: form.original_price || 0,
    })
    form.title = res.title
    form.description = res.description
    message.success(`AI 已生成文案（${res.source === 'llm' ? '大模型' : '本地'}）`)
  } catch { /* 已提示 */ } finally {
    aiCopyLoading.value = false
  }
}

async function onAiEstimate() {
  if (!form.original_price || form.original_price <= 0) return message.warning('请先填写原价')
  const originalPrice = form.original_price
  aiEstimateLoading.value = true
  try {
    const res = await aiEstimate({
      category_name: categoryName(),
      original_price: originalPrice,
      condition_level: form.condition_level,
      used_years: form.used_years,
    })
    form.sell_price = res.suggested_price
    estimateTip.value = `建议区间 ¥${res.price_low} ~ ¥${res.price_high}（${res.reason}）`
    message.success('AI 估价完成')
  } catch { /* 已提示 */ } finally {
    aiEstimateLoading.value = false
  }
}

async function customUpload(options: { file: unknown; onSuccess?: (body: unknown) => void; onError?: (err: Error) => void }) {
  const file = options.file as File
  uploadLoading.value = true
  try {
    const url = await uploadImage(file)
    imageUrls.value.push(url)
    options.onSuccess?.(url)
    message.success('图片上传成功')
  } catch (err) {
    options.onError?.(err as Error)
  } finally {
    uploadLoading.value = false
  }
}

async function onSubmit() {
  if (!form.category_id) return message.warning('请选择分类')
  if (!form.title.trim()) return message.warning('请填写商品标题')
  if (!form.sell_price || form.sell_price <= 0) return message.warning('请填写售价')
  const sellPrice = form.sell_price
  submitting.value = true
  try {
    const goods = await publishGoods({
      category_id: form.category_id,
      title: form.title,
      description: form.description,
      original_price: form.original_price || 0,
      sell_price: sellPrice,
      condition_level: form.condition_level,
      images: imageUrls.value,
    })
    message.success('发布成功')
    void router.push(`/goods/${goods.id}`)
  } catch { /* 已提示 */ } finally {
    submitting.value = false
  }
}

onMounted(loadCategories)
</script>

<template>
  <div class="publish page-narrow">
    <a-card title="发布闲置" class="publish__card">
      <a-form layout="vertical">
        <!-- AI 文案助手 -->
        <div class="publish__ai">
          <div class="publish__ai-title"><RobotOutlined /> AI 智能助手</div>
          <a-form-item label="商品关键词（AI 可据此一键生成标题与描述）">
            <div class="publish__ai-row">
              <a-input v-model:value="form.keywords" placeholder="如：九成新机械键盘 87键 青轴" size="large" />
              <a-button type="primary" ghost size="large" :loading="aiCopyLoading" @click="onAiCopy">AI 帮写</a-button>
            </div>
          </a-form-item>
        </div>

        <a-form-item label="商品图片">
          <div class="publish__upload-list">
            <!-- 已上传图片卡片 -->
            <div v-for="(url, i) in imageUrls" :key="i" class="publish__thumb-wrap">
              <img :src="url" class="publish__thumb" alt="商品图" />
              <span class="publish__thumb-del" @click="imageUrls.splice(i, 1)"><DeleteOutlined /></span>
            </div>
            <!-- 上传按钮 -->
            <a-upload
              :custom-request="customUpload"
              :show-upload-list="false"
              accept="image/*"
              multiple
            >
              <div class="publish__upload-btn">
                <LoadingOutlined v-if="uploadLoading" />
                <template v-else>
                  <PlusOutlined />
                  <span>上传</span>
                </template>
              </div>
            </a-upload>
          </div>
        </a-form-item>

        <a-form-item label="商品标题" required>
          <a-input v-model:value="form.title" size="large" :maxlength="128" placeholder="一句话描述你的宝贝" />
        </a-form-item>

        <a-form-item label="商品描述">
          <a-textarea v-model:value="form.description" :rows="4" :maxlength="5000" placeholder="成色、使用情况、入手渠道、交易说明等" />
        </a-form-item>

        <div class="publish__row">
          <a-form-item label="分类" required class="publish__col">
            <a-select v-model:value="form.category_id" size="large" placeholder="选择分类">
              <a-select-option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.icon }} {{ cat.name }}</a-select-option>
            </a-select>
          </a-form-item>
          <a-form-item label="成色" class="publish__col">
            <a-select v-model:value="form.condition_level" size="large">
              <a-select-option :value="5">全新</a-select-option>
              <a-select-option :value="4">几乎全新</a-select-option>
              <a-select-option :value="3">明显使用痕迹</a-select-option>
              <a-select-option :value="2">成色一般</a-select-option>
              <a-select-option :value="1">成色较差</a-select-option>
            </a-select>
          </a-form-item>
        </div>

        <div class="publish__row">
          <a-form-item label="原价（元）" class="publish__col">
            <a-input-number v-model:value="form.original_price" :min="0" size="large" style="width:100%" placeholder="0" />
          </a-form-item>
          <a-form-item label="使用年限（年）" class="publish__col">
            <a-input-number v-model:value="form.used_years" :min="0" :max="50" size="large" style="width:100%" />
          </a-form-item>
        </div>

        <a-form-item label="售价（元）" required>
          <div class="publish__ai-row">
            <a-input-number v-model:value="form.sell_price" :min="1" size="large" style="flex:1" placeholder="想卖多少钱" />
            <a-button size="large" :loading="aiEstimateLoading" @click="onAiEstimate"><RobotOutlined /> AI 估价</a-button>
          </div>
          <p v-if="estimateTip" class="publish__tip">{{ estimateTip }}</p>
        </a-form-item>

        <a-button type="primary" size="large" block :loading="submitting" @click="onSubmit">立即发布</a-button>
      </a-form>
    </a-card>
  </div>
</template>

<style scoped>
.publish { width: 100%; max-width: 1000px; margin: 0 auto; }
.publish__card { border-radius: 14px; }
.publish__ai { background: linear-gradient(135deg, #eef2ff, #f5f7ff); border: 1px dashed #c7d2fe; border-radius: 12px; padding: 16px; margin-bottom: 20px; }
.publish__ai-title { font-weight: 700; color: #ff6a00; margin-bottom: 12px; }
.publish__ai-row { display: flex; gap: 10px; align-items: center; }
.publish__row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.publish__col { margin-bottom: 0; }
.publish__tip { margin: 8px 0 0; font-size: 13px; color: #e65c00; }
.publish__upload-list { display: flex; gap: 10px; flex-wrap: wrap; }
.publish__thumb-wrap { position: relative; width: 86px; height: 86px; border-radius: 8px; overflow: hidden; border: 1px solid #f0ebe3; }
.publish__thumb { width: 100%; height: 100%; object-fit: cover; display: block; }
.publish__thumb-del {
  position: absolute; top: 4px; right: 4px; width: 20px; height: 20px; border-radius: 50%;
  background: rgba(0,0,0,0.55); color: #fff; display: grid; place-items: center;
  font-size: 12px; cursor: pointer; opacity: 0; transition: opacity .15s;
}
.publish__thumb-wrap:hover .publish__thumb-del { opacity: 1; }
.publish__upload-btn {
  width: 86px; height: 86px; display: flex; flex-direction: column; align-items: center; justify-content: center;
  gap: 4px; color: #98a2b3; border: 1px dashed #d9d9d9; border-radius: 8px; cursor: pointer;
  background: #fafafa; transition: border-color .15s;
}
.publish__upload-btn:hover { border-color: #ff6a00; color: #ff6a00; }
</style>
