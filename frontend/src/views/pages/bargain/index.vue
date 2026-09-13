<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
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
import { getChatHistory, sendMessage } from '@/common/apis/messageApi'
import { useUserStore } from '@/stores/user'
import type { BargainRecord, BargainSession, ChatMessage } from '@/common/types/business'

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

// 议价后的继续交流
const chatList = ref<ChatMessage[]>([])
const chatInput = ref('')
const chatLoading = ref(false)
const chatSending = ref(false)

const myId = computed(() => userStore.user?.id)
const isSellerView = computed(() => current.value && current.value.seller_id === myId.value)
const myTurn = computed(() => {
  if (!current.value || current.value.turn === 'none') return false
  return (current.value.turn === 'seller' && isSellerView.value) || (current.value.turn === 'buyer' && !isSellerView.value)
})

// 已成交（有议价被接受）
const acceptedRecord = computed(() => {
  if (!current.value) return null
  return [...current.value.records].reverse().find((r) => r.status === 2) || null
})
const dealPrice = computed(() => acceptedRecord.value?.offer_price ?? null)
// 议价是否已结束（无待响应记录）
const isEnded = computed(() => current.value && current.value.turn === 'none')
// 聊天对象 id
const peerId = computed(() => (isSellerView.value ? current.value?.buyer_id : current.value?.seller_id))

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
  try {
    current.value = await getBargainSession(record.product_id, record.buyer_id)
    offerPrice.value = undefined
    offerMessage.value = ''
    await loadChat()
  } catch { /* 已提示 */ } finally {
    sessionLoading.value = false
  }
}

async function loadChat() {
  if (!peerId.value || !current.value) return
  chatLoading.value = true
  try {
    const res = await getChatHistory({ peer_id: peerId.value, product_id: current.value.product_id, page_size: 100 })
    chatList.value = res.list
  } catch { /* 忽略 */ } finally {
    chatLoading.value = false
  }
}

async function sendChat() {
  const content = chatInput.value.trim()
  if (!content || !peerId.value || !current.value) return
  chatSending.value = true
  try {
    const msg = await sendMessage({ receiver_id: peerId.value, product_id: current.value.product_id, content })
    chatList.value.push(msg)
    chatInput.value = ''
  } catch { /* 已提示 */ } finally {
    chatSending.value = false
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
  try {
    sessions.value = await getMyBargains()
  } catch { /* 忽略轮询失败 */ }
}

// 静默刷新当前议价会话：对方新出价/响应自动出现，无需手动刷新
async function refreshCurrentSilent() {
  if (!current.value) return
  try {
    const data = await getBargainSession(current.value.product_id, current.value.buyer_id)
    // 记录数或待响应状态变化时更新
    if (data.records.length !== current.value.records.length || data.pending_record_id !== current.value.pending_record_id) {
      current.value = data
    }
  } catch { /* 忽略轮询失败 */ }
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
    // AI 话术直接填入消息输入框，点击“还价/出价”即可连同价格一起发送
    offerMessage.value = res.reply
    if (res.counter_price) offerPrice.value = res.counter_price
  } catch { /* 已提示 */ } finally {
    aiLoading.value = false
  }
}

async function goOrder() {
  if (!current.value) return
  actionLoading.value = true
  try {
    await createOrder({ product_id: current.value.product_id, bargain_record_id: acceptedRecord.value?.id })
    message.success('下单成功')
    void router.push('/order')
  } catch { /* 已提示 */ } finally {
    actionLoading.value = false
  }
}

const statusText = (s: number) => ({ 1: '待响应', 2: '已接受', 3: '已拒绝' })[s] || '未知'
const statusColor = (s: number) => ({ 1: 'gold', 2: 'green', 3: 'red' })[s] || 'default'

let timer: ReturnType<typeof setInterval> | null = null

onMounted(async () => {
  await loadSessions()
  // 轮询：议价会话与当前对话自动更新，对方出价/响应即时可见
  timer = setInterval(async () => {
    await loadSessionsOnly()
    await refreshCurrentSilent()
  }, 4000)
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
})
</script>

<template>
  <div class="bargain page-mid">
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

          <!-- 成交卡片（议价被接受后展示） -->
          <div v-if="acceptedRecord" class="deal-card">
            <img v-if="current.product_image" :src="current.product_image" class="deal-card__img" alt="" />
            <div class="deal-card__info">
              <div class="deal-card__title">{{ current.product_title }}</div>
              <div class="deal-card__price">
                成交价 <b>¥{{ dealPrice }}</b>
                <span class="deal-card__orig">¥{{ current.sell_price }}</span>
              </div>
            </div>
            <!-- 买家可立即购买 -->
            <a-button
              v-if="!isSellerView"
              type="primary"
              size="large"
              class="deal-card__btn"
              :loading="actionLoading"
              @click="goOrder"
            >
              立即购买
            </a-button>
            <a-tag v-else color="green" class="deal-card__tag">已成交</a-tag>
          </div>

          <!-- 操作区 -->
          <div class="bargain__actions" v-if="!isEnded">
            <template v-if="myTurn">
              <div class="bargain__input-row">
                <a-input-number v-model:value="offerPrice" :min="1" size="large" placeholder="出价" class="bargain__price-input" />
                <a-button :loading="aiLoading" size="large" @click="askAi"><RobotOutlined /> AI 助手</a-button>
                <a-button type="primary" size="large" :loading="actionLoading" @click="submitOffer">
                  {{ isSellerView ? '还价' : '出价' }}
                </a-button>
              </div>
              <a-textarea v-model:value="offerMessage" :rows="2" placeholder="捎句话（选填）" class="bargain__msg" />
              <!-- 对方刚出价，我可接受/拒绝 -->
              <div class="bargain__respond" v-if="current.pending_record_id">
                <a-button type="primary" ghost :loading="actionLoading" @click="respond(true)">接受该出价</a-button>
                <a-button danger ghost :loading="actionLoading" @click="respond(false)">拒绝</a-button>
              </div>
            </template>
            <div v-else class="bargain__waiting">
              <span>等待{{ current.turn === 'seller' ? '卖家' : '买家' }}响应…</span>
            </div>
          </div>

          <!-- 议价结束后的继续交流 -->
          <div class="chat">
            <div class="chat__divider">{{ isEnded ? '议价已结束 · 可继续交流' : '交流' }}</div>
            <a-spin :spinning="chatLoading">
              <div class="chat__list">
                <a-empty v-if="!chatList.length" description="还没有聊天记录" :image-style="{ height: '40px' }" />
                <div
                  v-for="m in chatList"
                  :key="m.id"
                  class="chat__item"
                  :class="{ 'chat__item--me': m.sender_id === myId }"
                >
                  <a-avatar :size="28" :src="m.sender_avatar || undefined" class="chat__avatar">
                    {{ (m.sender_nickname || 'U').slice(0, 1) }}
                  </a-avatar>
                  <div class="chat__bubble">{{ m.content }}</div>
                </div>
              </div>
            </a-spin>
            <div class="chat__input-row">
              <a-textarea
                v-model:value="chatInput"
                :rows="1"
                placeholder="发消息…"
                class="chat__input"
                @press-enter.prevent="sendChat"
              />
              <a-button type="primary" :loading="chatSending" :disabled="!chatInput.trim()" @click="sendChat">发送</a-button>
            </div>
          </div>
        </template>
        <a-empty v-else description="选择左侧会话查看议价" />
      </a-spin>
    </a-card>
  </div>
</template>

<style scoped>
.bargain { display: grid; grid-template-columns: 340px 1fr; gap: 20px; flex: 1; min-height: 0; }
.bargain__list { border-radius: 12px; height: 100%; overflow-y: auto; }
.bargain__session { padding: 12px; border-radius: 8px; cursor: pointer; margin-bottom: 6px; border: 1px solid transparent; }
.bargain__session:hover { background: #faf7f2; }
.bargain__session--active { background: #fff1e6; border-color: #ffd9b3; }
.bargain__session-title { font-weight: 600; font-size: 14px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.bargain__session-meta { display: flex; justify-content: space-between; align-items: center; margin-top: 6px; font-size: 12px; color: #98a2b3; }
.bargain__chat { border-radius: 12px; height: 100%; display: flex; flex-direction: column; }
.bargain__chat :deep(.ant-card-body) { flex: 1; display: flex; flex-direction: column; overflow: hidden; }
.bargain__chat :deep(.ant-spin-nested-loading),
.bargain__chat :deep(.ant-spin-container) { height: 100%; display: flex; flex-direction: column; }
.bargain__price-bar { padding: 10px 0; border-bottom: 1px solid #f0f2f5; margin-bottom: 12px; }
.bargain__turn { margin-left: 12px; font-size: 12px; color: #98a2b3; }
.bargain__records { flex: 1; overflow-y: auto; padding: 8px 0; }
.bargain__bubble { margin-bottom: 14px; max-width: 80%; }
.bargain__bubble--me { margin-left: auto; text-align: right; }
.bargain__bubble-role { font-size: 12px; color: #98a2b3; margin-bottom: 4px; }
.bargain__bubble-body { display: inline-flex; align-items: baseline; gap: 8px; padding: 10px 14px; border-radius: 12px; background: #faf7f2; }
.bargain__bubble--me .bargain__bubble-body { background: #fff1e6; }
.bargain__bubble-price { font-weight: 800; color: #ef4444; }
.bargain__bubble-msg { color: #4b5563; font-size: 13px; }
.bargain__actions { border-top: 1px solid #f0f2f5; padding-top: 14px; margin-top: 12px; }
.bargain__input-row { display: flex; gap: 10px; }
.bargain__price-input { flex: 1; }
.bargain__msg { margin-top: 10px; }
.bargain__respond { margin-top: 12px; display: flex; gap: 10px; }
.bargain__waiting { padding: 12px 0; color: #98a2b3; }

/* ===== 成交卡片 ===== */
.deal-card {
  display: flex; align-items: center; gap: 14px;
  background: linear-gradient(135deg, #f0fdf4, #ecfdf5);
  border: 1px solid #bbf7d0; border-radius: 14px; padding: 14px 16px; margin-bottom: 14px;
}
.deal-card__img { width: 64px; height: 64px; border-radius: 10px; object-fit: cover; flex-shrink: 0; }
.deal-card__info { flex: 1; min-width: 0; }
.deal-card__title { font-weight: 700; color: #1e293b; font-size: 14px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.deal-card__price { margin-top: 6px; color: #64748b; font-size: 13px; }
.deal-card__price b { color: #16a34a; font-size: 20px; margin: 0 2px; }
.deal-card__orig { color: #cbd5e1; text-decoration: line-through; font-size: 12px; }
.deal-card__btn { flex-shrink: 0; border-radius: 10px; }
.deal-card__tag { flex-shrink: 0; }

/* ===== 聊天区 ===== */
.chat { margin-top: 14px; }
.chat__divider { text-align: center; font-size: 12px; color: #b0a79d; margin-bottom: 12px; position: relative; }
.chat__divider::before, .chat__divider::after {
  content: ''; position: absolute; top: 50%; width: 28%; height: 1px; background: #f0ebe3;
}
.chat__divider::before { left: 0; }
.chat__divider::after { right: 0; }
.chat__list { max-height: 260px; overflow-y: auto; padding: 4px 2px; display: flex; flex-direction: column; gap: 10px; }
.chat__item { display: flex; align-items: flex-end; gap: 8px; }
.chat__item--me { flex-direction: row-reverse; }
.chat__avatar { flex-shrink: 0; background: linear-gradient(135deg, #ff8a3d, #ff6a00); }
.chat__bubble {
  max-width: 70%; padding: 8px 12px; border-radius: 12px; font-size: 13px; line-height: 1.5;
  background: #faf7f2; color: #2b2622; border-bottom-left-radius: 4px;
}
.chat__item--me .chat__bubble { background: #fff1e6; border-bottom-left-radius: 12px; border-bottom-right-radius: 4px; }
.chat__input-row { display: flex; gap: 10px; margin-top: 12px; align-items: flex-end; }
.chat__input { flex: 1; }

@media (max-width: 860px) { .bargain { grid-template-columns: 1fr; } }
</style>
