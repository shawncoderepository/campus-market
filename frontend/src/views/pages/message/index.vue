<script setup lang="ts">
import { computed, nextTick, onMounted, onUnmounted, ref } from 'vue'
import {
  Avatar as AAvatar,
  Button as AButton,
  Card as ACard,
  Empty as AEmpty,
  Input as AInput,
  Spin as ASpin,
} from 'ant-design-vue'
import { SendOutlined } from '@ant-design/icons-vue'
import { getChatHistory, getConversations, sendMessage } from '@/common/apis/messageApi'
import { useUserStore } from '@/stores/user'
import type { ChatMessage, Conversation } from '@/common/types/business'

const userStore = useUserStore()
const loading = ref(false)
const conversations = ref<Conversation[]>([])
const active = ref<Conversation | null>(null)
const messages = ref<ChatMessage[]>([])
const chatLoading = ref(false)
const input = ref('')
const sending = ref(false)
const listRef = ref<HTMLElement | null>(null)

const myId = computed(() => userStore.user?.id)

async function loadConversations() {
  loading.value = true
  try {
    conversations.value = await getConversations()
    if (conversations.value.length && !active.value) await open(conversations.value[0])
  } catch { /* 已提示 */ } finally {
    loading.value = false
  }
}

async function open(conv: Conversation) {
  active.value = conv
  chatLoading.value = true
  try {
    const res = await getChatHistory({ peer_id: conv.peer_id, product_id: conv.product_id ?? undefined, page_size: 100 })
    messages.value = res.list
    await nextTick()
    scrollToBottom()
    await loadConversationsOnly()
  } catch { /* 已提示 */ } finally {
    chatLoading.value = false
  }
}

async function loadConversationsOnly() {
  try {
    conversations.value = await getConversations()
  } catch { /* 忽略轮询失败 */ }
}

async function send() {
  if (!input.value.trim() || !active.value) return
  sending.value = true
  try {
    const msg = await sendMessage({ receiver_id: active.value.peer_id, product_id: active.value.product_id ?? undefined, content: input.value.trim() })
    messages.value.push(msg)
    input.value = ''
    await nextTick()
    scrollToBottom()
  } catch { /* 已提示 */ } finally {
    sending.value = false
  }
}

function scrollToBottom() {
  if (listRef.value) listRef.value.scrollTop = listRef.value.scrollHeight
}

// 判断用户是否已滚动到底部附近（避免拉新消息时打断其翻看历史）
function isNearBottom() {
  if (!listRef.value) return true
  const el = listRef.value
  return el.scrollHeight - el.scrollTop - el.clientHeight < 80
}

// 静默刷新当前聊天：新消息自动出现，仅在贴近底部时才自动下滚
async function refreshActiveChat() {
  if (!active.value) return
  try {
    const res = await getChatHistory({ peer_id: active.value.peer_id, product_id: active.value.product_id ?? undefined, page_size: 100 })
    if (res.list.length !== messages.value.length) {
      const nearBottom = isNearBottom()
      messages.value = res.list
      if (nearBottom) {
        await nextTick()
        scrollToBottom()
      }
    }
  } catch { /* 忽略轮询失败 */ }
}

let timer: ReturnType<typeof setInterval> | null = null

onMounted(async () => {
  await loadConversations()
  // 轮询：会话列表与当前聊天自动更新，无需手动刷新页面
  timer = setInterval(async () => {
    await loadConversationsOnly().catch(() => {})
    await refreshActiveChat()
  }, 4000)
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
})
</script>

<template>
  <div class="message page-mid">
    <a-card class="message__convs" title="会话" size="small">
      <a-spin :spinning="loading">
        <a-empty v-if="!conversations.length" description="暂无会话" />
        <div
          v-for="c in conversations"
          :key="`${c.peer_id}-${c.product_id}`"
          class="message__conv"
          :class="{ 'message__conv--active': active && active.peer_id === c.peer_id && active.product_id === c.product_id }"
          @click="open(c)"
        >
          <a-avatar :src="c.peer_avatar || undefined">{{ c.peer_nickname.slice(0, 1) }}</a-avatar>
          <div class="message__conv-meta">
            <div class="message__conv-name">{{ c.peer_nickname }}</div>
            <div class="message__conv-last">{{ c.last_content }}</div>
          </div>
          <span v-if="c.unread_count" class="message__unread">{{ c.unread_count }}</span>
        </div>
      </a-spin>
    </a-card>

    <a-card class="message__chat" :title="active ? `与 ${active.peer_nickname} 的对话` : '聊天'">
      <a-spin :spinning="chatLoading">
        <template v-if="active">
          <div ref="listRef" class="message__list">
            <a-empty v-if="!messages.length" description="开始聊天吧" />
            <div
              v-for="m in messages"
              :key="m.id"
              class="message__bubble"
              :class="m.sender_id === myId ? 'message__bubble--me' : (m.msg_type === 2 ? 'message__bubble--system' : 'message__bubble--peer')"
            >
              <span v-if="m.msg_type === 2 && m.sender_id !== myId" class="message__sys-badge">系统通知</span>
              {{ m.content }}
            </div>
          </div>
          <div class="message__input">
            <a-input
              v-model:value="input"
              size="large"
              placeholder="输入消息，回车发送"
              @press-enter="send"
            />
            <a-button type="primary" size="large" :loading="sending" @click="send"><SendOutlined /></a-button>
          </div>
        </template>
        <a-empty v-else description="选择会话开始聊天" />
      </a-spin>
    </a-card>
  </div>
</template>

<style scoped>
.message { display: grid; grid-template-columns: 340px 1fr; gap: 20px; flex: 1; min-height: 0; }
.message__convs { border-radius: 12px; height: 100%; overflow-y: auto; }
.message__conv { display: flex; align-items: center; gap: 10px; padding: 10px; border-radius: 8px; cursor: pointer; }
.message__conv:hover { background: #faf7f2; }
.message__conv--active { background: #fff1e6; }
.message__conv-meta { flex: 1; min-width: 0; }
.message__conv-name { font-weight: 600; font-size: 14px; }
.message__conv-last { font-size: 12px; color: #98a2b3; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.message__unread { background: #ef4444; color: #fff; font-size: 11px; padding: 1px 6px; border-radius: 10px; }
.message__chat { border-radius: 12px; height: 100%; display: flex; flex-direction: column; }
.message__chat :deep(.ant-card-body) { flex: 1; display: flex; flex-direction: column; overflow: hidden; }
.message__chat :deep(.ant-spin-nested-loading),
.message__chat :deep(.ant-spin-container) { height: 100%; display: flex; flex-direction: column; }
.message__list { flex: 1; overflow-y: auto; padding: 10px 4px; }
.message__bubble { max-width: 70%; padding: 10px 14px; border-radius: 12px; margin-bottom: 10px; background: #f5f0ea; width: fit-content; }
.message__bubble--me { margin-left: auto; background: linear-gradient(135deg, #ff8a3d, #ff6a00); color: #fff; }
.message__bubble--system { background: #fff7ed; border: 1px solid #fed7aa; color: #9a3412; max-width: 88%; }
.message__sys-badge { display: inline-block; font-size: 11px; font-weight: 700; color: #ff6a00; background: #ffedd5; border-radius: 4px; padding: 0 6px; margin-right: 6px; }
.message__input { display: flex; gap: 10px; border-top: 1px solid #f0f2f5; padding-top: 12px; margin-top: 12px; }
@media (max-width: 860px) { .message { grid-template-columns: 1fr; } }
</style>
