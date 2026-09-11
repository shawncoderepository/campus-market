<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import {
  Avatar as AAvatar,
  Button as AButton,
  Card as ACard,
  Empty as AEmpty,
  InputNumber as AInputNumber,
  message,
  Spin as ASpin,
  Tag as ATag,
  Textarea as ATextarea,
} from 'ant-design-vue'
import { RobotOutlined } from '@ant-design/icons-vue'
import {
  buyerOffer,
  getBargainSession,
  getMyBargains,
  respondBargain,
  sellerReply,
} from '@/common/apis/bargainApi'
import { aiBargain } from '@/common/apis/aiApi'
import { createOrder } from '@/common/apis/orderApi'
import { useUserStore } from '@/stores/user'
import type { BargainRecord, BargainSession } from '@/common/types/business'

const router = useRouter()
const userStore = useUserStore()
const loading = ref(false)
const sessions = ref<BargainRecord[]>([])
const current = ref<BargainSession | null>(null)
const sessionLoading = ref(false)
const offerPrice = ref<number | undefined>(undefined)
const offerMessage = ref('')
const actionLoading = ref(false)
const aiLoading = ref(false)
const aiTip = ref('')

const myId = computed(() => userStore.user?.id)
const isSellerView = computed(() => current.value && current.value.seller_id === myId.value)
const myTurn = computed(() => {
  if (!current.value || current.value.turn === 'none') return false
  return (current.value.turn === 'seller' && isSellerView.value) || (current.value.turn === 'buyer' && !isSellerView.value)
})

async function loadSessions() {
  loading.value = true
  try {
    sessions.value = await getMyBargains()
    if (sessions.value.length) await openSession(sessions.value[0])
  } catch { /* 已提示 */ } finally {
    loading.value = false
  }
}

async function openSession(record: BargainRecord) {
  sessionLoading.value = true
  aiTip.value = ''
  try {
    current.value = await getBargainSession(record.product_id, record.buyer_id)
    offerPrice.value = undefined
    offerMessage.value = ''
  } catch { /* 已提示 */ } finally {
    sessionLoading.value = false
  }
}

async function submitOffer() {
  if (!current.value) return
  if (!offerPrice.value || offerPrice.value <= 0) return message.warning('请输入出价')
  actionLoading.value = true
  try {
    if (isSellerView.value) {
      await sellerReply({ product_id: current.value.product_id, buyer_id: current.value.buyer_id, offer_price: offerPrice.value, message: offerMessage.value })
      message.success('还价成功')
    } else {
      await buyerOffer({ product_id: current.value.product_id, offer_price: offerPrice.value, message: offerMessage.value })
      message.success('出价成功')
    }
    await refreshCurrent()
  } catch { /* 已提示 */ } finally {
    actionLoading.value = false
  }
}

async function respond(accept: boolean) {
  if (!current.value?.pending_record_id) return
  actionLoading.value = true
  try {
    await respondBargain({ record_id: current.value.pending_record_id, accept })
    message.success(accept ? '已接受，可去下单' : '已拒绝')
    await refreshCurrent()
  } catch { /* 已提示 */ } finally {
    actionLoading.value = false
  }
}

async function refreshCurrent() {
  if (!current.value) return
  current.value = await getBargainSession(current.value.product_id, current.value.buyer_id)
  await loadSessionsOnly()
}

async function loadSessionsOnly() {
  sessions.value = await getMyBargains()
}

async function askAi() {
  if (!current.value) return
  const lastBuyerOffer = [...current.value.records].reverse().find((r) => r.role === 'buyer' && r.offer_price)
  const offer = isSellerView.value ? (lastBuyerOffer?.offer_price ?? current.value.sell_price) : (offerPrice.value ?? current.value.sell_price * 0.9)
  aiLoading.value = true
  try {
    const res = await aiBargain({
      product_title: current.value.product_title,
      sell_price: current.value.sell_price,
      buyer_offer: offer,
      buyer_message: lastBuyerOffer?.message || '',
      round_no: current.value.records.length ? Math.max(...current.value.records.map((r) => r.round)) : 1,
      side: isSellerView.value ? 'seller' : 'buyer',
    })
    aiTip.value = res.reply
    if (res.counter_price) offerPrice.value = res.counter_price
  } catch { /* 已提示 */ } finally {
    aiLoading.value = false
  }
}

async function goOrder() {
  if (!current.value) return
  actionLoading.value = true
  try {
    // 找到被接受的议价记录
    const accepted = [...current.value.records].reverse().find((r) => r.status === 2)
    await createOrder({ product_id: current.value.product_id, bargain_record_id: accepted?.id })
    message.success('下单成功')
    void router.push('/order')
  } catch { /* 已提示 */ } finally {
    actionLoading.value = false
  }
}

const statusText = (s: number) => ({ 1: '待响应', 2: '已接受', 3: '已拒绝' })[s] || '未知'
const statusColor = (s: number) => ({ 1: 'gold', 2: 'green', 3: 'red' })[s] || 'default'

onMounted(loadSessions)
</script>

<template>
  <div class="bargain">
    <!-- 会话列表 -->
    <a-card class="bargain__list" title="议价会话" size="small">
      <a-spin :spinning="loading">
        <a-empty v-if="!sessions.length" description="还没有议价记录，去逛逛砍一刀吧" />
        <div
          v-for="s in sessions"
          :key="`${s.product_id}-${s.buyer_id}`"
          class="bargain__session"
          :class="{ 'bargain__session--active': current && current.product_id === s.product_id && current.buyer_id === s.buyer_id }"
          @click="openSession(s)"
        >
          <div class="bargain__session-title">{{ s.product_title }}</div>
          <div class="bargain__session-meta">
            <span>{{ s.buyer_id === myId ? '我出价' : '对方' }} ¥{{ s.offer_price ?? '-' }}</span>
            <a-tag :color="statusColor(s.status)" size="small">{{ statusText(s.status) }}</a-tag>
          </div>
        </div>
      </a-spin>
    </a-card>

    <!-- 议价对话 -->
    <a-card class="bargain__chat" :title="current ? current.product_title : '议价详情'">
      <a-spin :spinning="sessionLoading">
        <template v-if="current">
          <div class="bargain__price-bar">
            标价 <b style="color:#ef4444">¥{{ current.sell_price }}</b>
            <span class="bargain__turn" v-if="current.turn !== 'none'">
              当前轮到 {{ current.turn === 'seller' ? '卖家' : '买家' }} 出价
            </span>
          </div>

          <div class="bargain__records">
            <a-empty v-if="!current.records.length" description="还没有出价，先砍一刀" />
            <div
              v-for="r in current.records"
              :key="r.id"
              class="bargain__bubble"
              :class="(r.role === 'seller') === isSellerView ? 'bargain__bubble--me' : 'bargain__bubble--peer'"
            >
              <div class="bargain__bubble-role">{{ r.role === 'seller' ? '卖家' : r.role === 'buyer' ? '买家' : 'AI' }}</div>
              <div class="bargain__bubble-body">
                <span class="bargain__bubble-price">¥{{ r.offer_price ?? '-' }}</span>
                <span v-if="r.message" class="bargain__bubble-msg">{{ r.message }}</span>
              </div>
              <a-tag :color="statusColor(r.status)" size="small">{{ statusText(r.status) }}</a-tag>
            </div>
          </div>

          <!-- 操作区 -->
          <div class="bargain__actions">
            <template v-if="myTurn">
              <div class="bargain__input-row">
                <a-input-number v-model:value="offerPrice" :min="1" size="large" placeholder="出价" class="bargain__price-input" />
                <a-button :loading="aiLoading" size="large" @click="askAi"><RobotOutlined /> AI 助手</a-button>
                <a-button type="primary" size="large" :loading="actionLoading" @click="submitOffer">
                  {{ isSellerView ? '还价' : '出价' }}
                </a-button>
              </div>
              <a-textarea v-model:value="offerMessage" :rows="2" placeholder="捎句话（选填）" class="bargain__msg" />
              <p v-if="aiTip" class="bargain__ai-tip"><RobotOutlined /> {{ aiTip }}</p>
              <!-- 对方刚出价，我可接受/拒绝 -->
              <div class="bargain__respond" v-if="current.pending_record_id">
                <a-button type="primary" ghost :loading="actionLoading" @click="respond(true)">接受该出价</a-button>
                <a-button danger ghost :loading="actionLoading" @click="respond(false)">拒绝</a-button>
              </div>
            </template>
            <div v-else class="bargain__waiting">
              <span v-if="current.turn === 'none'">议价已结束</span>
              <span v-else>等待{{ current.turn === 'seller' ? '卖家' : '买家' }}响应…</span>
            </div>
            <!-- 买家且议价被接受，可直接下单 -->
            <a-button
              v-if="!isSellerView && current.records.some((r) => r.status === 2)"
              type="primary"
              block
              size="large"
              :loading="actionLoading"
              @click="goOrder"
            >
              按成交价下单
            </a-button>
          </div>
        </template>
        <a-empty v-else description="选择左侧会话查看议价" />
      </a-spin>
    </a-card>
  </div>
</template>

<style scoped>
.bargain { display: grid; grid-template-columns: 300px 1fr; gap: 20px; }
.bargain__list { border-radius: 12px; max-height: 70vh; overflow-y: auto; }
.bargain__session { padding: 12px; border-radius: 8px; cursor: pointer; margin-bottom: 6px; border: 1px solid transparent; }
.bargain__session:hover { background: #f5f7fb; }
.bargain__session--active { background: #eef2ff; border-color: #c7d2fe; }
.bargain__session-title { font-weight: 600; font-size: 14px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.bargain__session-meta { display: flex; justify-content: space-between; align-items: center; margin-top: 6px; font-size: 12px; color: #98a2b3; }
.bargain__chat { border-radius: 12px; min-height: 60vh; display: flex; flex-direction: column; }
.bargain__price-bar { padding: 10px 0; border-bottom: 1px solid #f0f2f5; margin-bottom: 12px; }
.bargain__turn { margin-left: 12px; font-size: 12px; color: #98a2b3; }
.bargain__records { flex: 1; overflow-y: auto; max-height: 40vh; padding: 8px 0; }
.bargain__bubble { margin-bottom: 14px; max-width: 80%; }
.bargain__bubble--me { margin-left: auto; text-align: right; }
.bargain__bubble-role { font-size: 12px; color: #98a2b3; margin-bottom: 4px; }
.bargain__bubble-body { display: inline-flex; align-items: baseline; gap: 8px; padding: 10px 14px; border-radius: 12px; background: #f5f7fb; }
.bargain__bubble--me .bargain__bubble-body { background: #dbeafe; }
.bargain__bubble-price { font-weight: 800; color: #ef4444; }
.bargain__bubble-msg { color: #4b5563; font-size: 13px; }
.bargain__actions { border-top: 1px solid #f0f2f5; padding-top: 14px; margin-top: 12px; }
.bargain__input-row { display: flex; gap: 10px; }
.bargain__price-input { flex: 1; }
.bargain__msg { margin-top: 10px; }
.bargain__ai-tip { margin-top: 10px; padding: 10px; background: #eef2ff; border-radius: 8px; color: #4f46e5; font-size: 13px; }
.bargain__respond { margin-top: 12px; display: flex; gap: 10px; }
.bargain__waiting { padding: 12px 0; color: #98a2b3; }
@media (max-width: 860px) { .bargain { grid-template-columns: 1fr; } }
</style>
