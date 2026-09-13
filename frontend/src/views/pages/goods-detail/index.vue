<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  Avatar as AAvatar,
  Button as AButton,
  Descriptions as ADescriptions,
  DescriptionsItem as ADescriptionsItem,
  InputNumber as AInputNumber,
  message,
  Modal as AModal,
  Spin as ASpin,
  Tag as ATag,
  Textarea as ATextarea,
} from 'ant-design-vue'
import {
  EyeOutlined,
  FlagOutlined,
  HeartFilled,
  HeartOutlined,
  MessageOutlined,
  TagsOutlined,
} from '@ant-design/icons-vue'
import GoodsCard from '@/components/GoodsCard.vue'
import { getGoodsDetail } from '@/common/apis/goodsApi'
import { toggleFavorite } from '@/common/apis/favoriteApi'
import { buyerOffer } from '@/common/apis/bargainApi'
import { createOrder } from '@/common/apis/orderApi'
import { sendMessage } from '@/common/apis/messageApi'
import { createReport, REPORT_REASON_TYPES } from '@/common/apis/reportApi'
import { useUserStore } from '@/stores/user'
import type { GoodsDetail } from '@/common/types/business'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const loading = ref(true)
const detail = ref<GoodsDetail | null>(null)
const favorited = ref(false)
const activeImage = ref('')

const bargainVisible = ref(false)
const bargainPrice = ref<number | undefined>(undefined)
const bargainMessage = ref('')
const bargainLoading = ref(false)

const reportVisible = ref(false)
const reportType = ref<string>('counterfeit')
const reportReason = ref('')
const reportLoading = ref(false)

const buyLoading = ref(false)

const id = Number(route.params.id)
const isOwner = computed(() => userStore.user?.id === detail.value?.seller_id)
const conditionText = computed(
  () => ({ 5: '全新', 4: '几乎全新', 3: '明显使用痕迹', 2: '成色一般', 1: '成色较差' })[detail.value?.condition_level || 3],
)

async function load() {
  loading.value = true
  try {
    detail.value = await getGoodsDetail(id)
    favorited.value = detail.value.is_favorited
    activeImage.value = detail.value.images?.[0] || ''
  } catch { /* 已提示 */ } finally {
    loading.value = false
  }
}

function needLogin(): boolean {
  if (!userStore.isLoggedIn) {
    message.warning('请先登录')
    void router.push({ path: '/login', query: { redirect: route.fullPath } })
    return true
  }
  return false
}

async function onToggleFavorite() {
  if (needLogin()) return
  try {
    const res = await toggleFavorite(id)
    favorited.value = res.is_favorited
    message.success(res.is_favorited ? '收藏成功' : '已取消收藏')
  } catch { /* 已提示 */ }
}

function openBargain() {
  if (needLogin()) return
  bargainPrice.value = detail.value ? Math.round(detail.value.sell_price * 0.9) : undefined
  bargainVisible.value = true
}

async function submitBargain() {
  if (!bargainPrice.value || bargainPrice.value <= 0) return message.warning('请输入出价')
  bargainLoading.value = true
  try {
    await buyerOffer({ product_id: id, offer_price: bargainPrice.value, message: bargainMessage.value })
    message.success('出价成功，等待卖家响应')
    bargainVisible.value = false
    void router.push('/bargain')
  } catch { /* 已提示 */ } finally {
    bargainLoading.value = false
  }
}

async function onBuyNow() {
  if (needLogin()) return
  buyLoading.value = true
  try {
    await createOrder({ product_id: id })
    message.success('下单成功，请尽快付款')
    void router.push('/order')
  } catch { /* 已提示 */ } finally {
    buyLoading.value = false
  }
}

async function onContact() {
  if (needLogin()) return
  try {
    await sendMessage({ receiver_id: detail.value!.seller_id, product_id: id, content: `你好，我对「${detail.value!.title}」感兴趣` })
    message.success('已发送私信')
    void router.push('/message')
  } catch { /* 已提示 */ }
}

// 确认键可点：已选类型且填写了原因
const canSubmitReport = computed(() => Boolean(reportType.value) && reportReason.value.trim().length > 0)

async function submitReport() {
  if (!reportType.value) return message.warning('请选择违规类型')
  if (!reportReason.value.trim()) return message.warning('请填写举报原因')
  reportLoading.value = true
  try {
    await createReport({ product_id: id, reason_type: reportType.value, reason: reportReason.value.trim() })
    message.success('举报已提交，我们会尽快核实处理')
    reportVisible.value = false
    reportType.value = 'counterfeit'
    reportReason.value = ''
  } catch { /* 已提示 */ } finally {
    reportLoading.value = false
  }
}

onMounted(load)
</script>

<template>
  <a-spin :spinning="loading">
    <div v-if="detail" class="detail page-mid">
      <div class="detail__main">
        <!-- 图片区 -->
        <div class="detail__gallery">
          <div class="detail__cover">
            <img v-if="activeImage" :src="activeImage" :alt="detail.title" />
            <div v-else class="detail__placeholder">{{ detail.title.slice(0, 1) }}</div>
            <span class="detail__condition-tag">{{ conditionText }}</span>
          </div>
          <div v-if="detail.images?.length > 1" class="detail__thumbs">
            <img
              v-for="(img, i) in detail.images"
              :key="i"
              :src="img"
              :alt="`图${i + 1}`"
              :class="{ 'is-active': activeImage === img }"
              @click="activeImage = img"
            />
          </div>
        </div>

        <!-- 信息与操作区 -->
        <div class="detail__info">
          <h1 class="detail__title">{{ detail.title }}</h1>

          <div class="detail__price-card">
            <div class="detail__price-main">
              <span class="detail__price-symbol">¥</span>
              <span class="detail__price">{{ detail.sell_price }}</span>
              <span v-if="detail.original_price > 0" class="detail__original">¥{{ detail.original_price }}</span>
            </div>
            <div class="detail__price-meta">
              <EyeOutlined /> {{ detail.view_count }} 人看过 · {{ detail.category_name }}
            </div>
          </div>

          <div class="detail__seller">
            <a-avatar :size="44" :src="detail.seller_avatar || undefined">{{ detail.seller_nickname.slice(0, 1) }}</a-avatar>
            <div class="detail__seller-meta">
              <div class="detail__seller-name">{{ detail.seller_nickname }}</div>
              <div class="detail__seller-credit">信用分 {{ detail.seller?.credit_score ?? 100 }}</div>
            </div>
            <a-button v-if="!isOwner" size="small" @click="onContact"><MessageOutlined /> 私信</a-button>
          </div>

          <div class="detail__actions">
            <template v-if="!isOwner">
              <a-button type="primary" size="large" block class="detail__buy" :loading="buyLoading" @click="onBuyNow">立即购买</a-button>
              <div class="detail__actions-row">
                <a-button size="large" @click="openBargain"><TagsOutlined /> 议价</a-button>
                <a-button size="large" @click="onToggleFavorite">
                  <HeartFilled v-if="favorited" style="color:#ff6a00" /><HeartOutlined v-else />
                  {{ favorited ? '已收藏' : '收藏' }}
                </a-button>
                <a-button type="text" size="large" @click="reportVisible = true"><FlagOutlined /> 举报</a-button>
              </div>
            </template>
            <a-button v-else size="large" block @click="router.push('/my')">这是我发布的商品，去管理</a-button>
          </div>
        </div>
      </div>

      <!-- 商品描述 -->
      <div class="detail__section">
        <h3>商品描述</h3>
        <p class="detail__text">{{ detail.description || '卖家很懒，什么都没写～' }}</p>
      </div>

      <!-- 相关推荐 -->
      <div v-if="detail.related?.length" class="detail__section">
        <h3>相似推荐</h3>
        <div class="detail__related">
          <GoodsCard v-for="item in detail.related" :key="item.id" :goods="item" @click="(rid) => router.push(`/goods/${rid}`)" />
        </div>
      </div>

      <!-- 议价弹窗 -->
      <a-modal v-model:open="bargainVisible" title="发起议价" :confirm-loading="bargainLoading" @ok="submitBargain">
        <div class="bargain-form">
          <p>当前标价：<b style="color:#ef4444">¥{{ detail.sell_price }}</b></p>
          <p>你的出价：</p>
          <a-input-number v-model:value="bargainPrice" :min="1" :max="detail.sell_price" style="width:100%" size="large" />
          <p style="margin-top:12px">留言（选填）：</p>
          <a-textarea v-model:value="bargainMessage" :rows="3" placeholder="例如：诚心要，能便宜点吗？" />
        </div>
      </a-modal>

      <!-- 举报弹窗 -->
      <a-modal
        v-model:open="reportVisible"
        title="举报商品"
        ok-text="提交举报"
        :confirm-loading="reportLoading"
        :ok-button-props="{ disabled: !canSubmitReport }"
        @ok="submitReport"
      >
        <a-form layout="vertical">
          <a-form-item label="违规类型" required>
            <a-radio-group v-model:value="reportType" class="report-type">
              <a-radio
                v-for="t in REPORT_REASON_TYPES"
                :key="t.code"
                :value="t.code"
                class="report-type__item"
                :class="{ 'report-type__item--checked': reportType === t.code }"
              >
                {{ t.name }}
              </a-radio>
            </a-radio-group>
          </a-form-item>
          <a-form-item label="举报原因" required>
            <a-textarea v-model:value="reportReason" :rows="3" placeholder="请描述具体违规情况，有助于平台核实（必填）" :maxlength="500" show-count />
          </a-form-item>
        </a-form>
      </a-modal>
    </div>
  </a-spin>
</template>

<style scoped>
.report-type {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  width: 100%;
}

.report-type__item {
  margin-right: 0;
  padding: 8px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background: #fff;
  transition: all 0.2s;
}

.report-type__item:hover {
  border-color: #ff6a00;
}

/* 选中项整卡高亮：橙边框 + 浅橙背景，一眼可见 */
.report-type__item--checked {
  border-color: #ff6a00;
  background: #fff1e6;
  box-shadow: 0 0 0 2px rgba(255, 106, 0, 0.12);
}

.report-type__item :deep(.ant-radio-checked + span) {
  color: #ff6a00;
  font-weight: 600;
}

.detail__main { display: grid; grid-template-columns: 480px 1fr; gap: 32px; background: #fff; padding: 28px; border-radius: 16px; box-shadow: var(--shadow-card); }
.detail__cover { position: relative; width: 100%; aspect-ratio: 1; border-radius: 14px; overflow: hidden; background: #f5f0ea; }
.detail__cover img { width: 100%; height: 100%; object-fit: cover; }
.detail__condition-tag { position: absolute; top: 14px; left: 14px; padding: 4px 12px; font-size: 13px; font-weight: 600; color: #fff; background: rgba(255,106,0,0.92); border-radius: 20px; backdrop-filter: blur(4px); }
.detail__placeholder { width: 100%; height: 100%; display: grid; place-items: center; font-size: 96px; font-weight: 800; color: #e8c9a8; background: linear-gradient(135deg, #fff1e6, #ffe8d6); }
.detail__thumbs { display: flex; gap: 10px; margin-top: 14px; overflow-x: auto; }
.detail__thumbs img { width: 72px; height: 72px; object-fit: cover; border-radius: 10px; cursor: pointer; border: 2px solid transparent; opacity: 0.7; transition: all 0.15s ease; }
.detail__thumbs img:hover { opacity: 1; }
.detail__thumbs img.is-active { border-color: #ff6a00; opacity: 1; }

.detail__title { margin: 0 0 16px; font-size: 22px; font-weight: 700; color: #2b2622; line-height: 1.4; }
.detail__price-card { background: linear-gradient(135deg, #fff7f0, #fff1e6); border-radius: 14px; padding: 18px 20px; margin-bottom: 18px; }
.detail__price-main { display: flex; align-items: baseline; gap: 10px; }
.detail__price-symbol { font-size: 18px; font-weight: 700; color: #ff6a00; }
.detail__price { font-size: 38px; font-weight: 800; color: #ff6a00; line-height: 1; }
.detail__original { font-size: 15px; color: #c9c2ba; text-decoration: line-through; }
.detail__price-meta { margin-top: 8px; font-size: 13px; color: #8a8078; }

.detail__seller { display: flex; align-items: center; gap: 12px; padding: 14px 16px; background: #faf7f2; border-radius: 12px; margin-bottom: 22px; }
.detail__seller-meta { flex: 1; }
.detail__seller-name { font-weight: 600; color: #2b2622; }
.detail__seller-credit { font-size: 12px; color: #8a8078; }

.detail__actions { display: flex; flex-direction: column; gap: 12px; }
.detail__buy { box-shadow: 0 6px 16px rgba(255,106,0,0.3); font-weight: 600; }
.detail__actions-row { display: flex; gap: 10px; flex-wrap: wrap; }

.detail__section { background: #fff; padding: 22px 26px; border-radius: 16px; margin-top: 20px; box-shadow: var(--shadow-card); }
.detail__section h3 { margin: 0 0 14px; font-size: 16px; font-weight: 700; color: #2b2622; }
.detail__text { color: #5c554d; line-height: 1.8; white-space: pre-wrap; margin: 0; }
.detail__related { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 16px; }
.bargain-form p { margin: 8px 0 4px; }
@media (max-width: 900px) { .detail__main { grid-template-columns: 1fr; } }
</style>
