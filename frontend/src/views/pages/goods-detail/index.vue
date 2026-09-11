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
import { createReport } from '@/common/apis/reportApi'
import { useUserStore } from '@/stores/user'
import type { GoodsDetail } from '@/common/types/business'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const loading = ref(true)
const detail = ref<GoodsDetail | null>(null)
const favorited = ref(false)

const bargainVisible = ref(false)
const bargainPrice = ref<number | undefined>(undefined)
const bargainMessage = ref('')
const bargainLoading = ref(false)

const reportVisible = ref(false)
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

async function submitReport() {
  if (!reportReason.value.trim()) return message.warning('请填写举报原因')
  reportLoading.value = true
  try {
    await createReport({ product_id: id, reason: reportReason.value })
    message.success('举报已提交')
    reportVisible.value = false
    reportReason.value = ''
  } catch { /* 已提示 */ } finally {
    reportLoading.value = false
  }
}

onMounted(load)
</script>

<template>
  <a-spin :spinning="loading">
    <div v-if="detail" class="detail">
      <div class="detail__main">
        <!-- 图片区 -->
        <div class="detail__gallery">
          <div class="detail__cover">
            <img v-if="detail.images?.[0]" :src="detail.images[0]" :alt="detail.title" />
            <div v-else class="detail__placeholder">{{ detail.title.slice(0, 1) }}</div>
          </div>
          <div v-if="detail.images?.length > 1" class="detail__thumbs">
            <img v-for="(img, i) in detail.images" :key="i" :src="img" :alt="`图${i + 1}`" />
          </div>
        </div>

        <!-- 信息与操作区 -->
        <div class="detail__info">
          <h1 class="detail__title">{{ detail.title }}</h1>
          <div class="detail__price-row">
            <span class="detail__price">¥{{ detail.sell_price }}</span>
            <span v-if="detail.original_price > 0" class="detail__original">原价 ¥{{ detail.original_price }}</span>
            <a-tag color="blue">{{ conditionText }}</a-tag>
          </div>

          <a-descriptions :column="1" size="small" class="detail__desc">
            <a-descriptions-item label="分类">{{ detail.category_name }}</a-descriptions-item>
            <a-descriptions-item label="浏览"><EyeOutlined /> {{ detail.view_count }}</a-descriptions-item>
          </a-descriptions>

          <div class="detail__seller">
            <a-avatar :src="detail.seller_avatar || undefined">{{ detail.seller_nickname.slice(0, 1) }}</a-avatar>
            <div class="detail__seller-meta">
              <div class="detail__seller-name">{{ detail.seller_nickname }}</div>
              <div class="detail__seller-credit">信用分 {{ detail.seller?.credit_score ?? 100 }}</div>
            </div>
          </div>

          <div class="detail__actions">
            <template v-if="!isOwner">
              <a-button type="primary" size="large" :loading="buyLoading" @click="onBuyNow">立即购买</a-button>
              <a-button size="large" @click="openBargain"><TagsOutlined /> 议价</a-button>
              <a-button size="large" @click="onContact"><MessageOutlined /> 联系卖家</a-button>
              <a-button size="large" @click="onToggleFavorite">
                <HeartFilled v-if="favorited" style="color:#ef4444" /><HeartOutlined v-else />
                {{ favorited ? '已收藏' : '收藏' }}
              </a-button>
              <a-button type="text" size="large" @click="reportVisible = true"><FlagOutlined /> 举报</a-button>
            </template>
            <a-button v-else size="large" @click="router.push('/my')">这是我发布的商品，去管理</a-button>
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
      <a-modal v-model:open="reportVisible" title="举报商品" :confirm-loading="reportLoading" @ok="submitReport">
        <a-textarea v-model:value="reportReason" :rows="4" placeholder="请描述举报原因，如虚假信息、违禁品等" />
      </a-modal>
    </div>
  </a-spin>
</template>

<style scoped>
.detail__main { display: grid; grid-template-columns: 460px 1fr; gap: 32px; background: #fff; padding: 24px; border-radius: 14px; }
.detail__cover { width: 100%; aspect-ratio: 1; border-radius: 12px; overflow: hidden; background: #f3f4f6; }
.detail__cover img { width: 100%; height: 100%; object-fit: cover; }
.detail__placeholder { width: 100%; height: 100%; display: grid; place-items: center; font-size: 96px; font-weight: 800; color: #c7d0e0; background: linear-gradient(135deg, #eef2ff, #f5f7fb); }
.detail__thumbs { display: flex; gap: 8px; margin-top: 12px; overflow-x: auto; }
.detail__thumbs img { width: 72px; height: 72px; object-fit: cover; border-radius: 8px; cursor: pointer; }
.detail__title { margin: 0 0 12px; font-size: 22px; font-weight: 700; color: #1f2937; }
.detail__price-row { display: flex; align-items: center; gap: 12px; margin-bottom: 16px; }
.detail__price { font-size: 32px; font-weight: 800; color: #ef4444; }
.detail__original { color: #9ca3af; text-decoration: line-through; }
.detail__desc { margin-bottom: 16px; }
.detail__seller { display: flex; align-items: center; gap: 12px; padding: 14px; background: #f8fafc; border-radius: 10px; margin-bottom: 20px; }
.detail__seller-name { font-weight: 600; color: #1f2937; }
.detail__seller-credit { font-size: 12px; color: #98a2b3; }
.detail__actions { display: flex; gap: 10px; flex-wrap: wrap; }
.detail__section { background: #fff; padding: 20px 24px; border-radius: 14px; margin-top: 20px; }
.detail__section h3 { margin: 0 0 12px; font-size: 16px; font-weight: 700; }
.detail__text { color: #4b5563; line-height: 1.8; white-space: pre-wrap; }
.detail__related { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 16px; }
.bargain-form p { margin: 8px 0 4px; }
@media (max-width: 900px) { .detail__main { grid-template-columns: 1fr; } }
</style>
