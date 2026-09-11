<script setup lang="ts">
import { computed, nextTick, onMounted, ref } from 'vue'
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
  conversations.value = await getConversations()
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

onMounted(loadConversations)
</script>

<template>
  <div class="message">
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
              :class="m.sender_id === myId ? 'message__bubble--me' : 'message__bubble--peer'"
            >
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
.message { display: grid; grid-template-columns: 300px 1fr; gap: 20px; }
.message__convs { border-radius: 12px; max-height: 70vh; overflow-y: auto; }
.message__conv { display: flex; align-items: center; gap: 10px; padding: 10px; border-radius: 8px; cursor: pointer; }
.message__conv:hover { background: #f5f7fb; }
.message__conv--active { background: #eef2ff; }
.message__conv-meta { flex: 1; min-width: 0; }
.message__conv-name { font-weight: 600; font-size: 14px; }
.message__conv-last { font-size: 12px; color: #98a2b3; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.message__unread { background: #ef4444; color: #fff; font-size: 11px; padding: 1px 6px; border-radius: 10px; }
.message__chat { border-radius: 12px; min-height: 60vh; display: flex; flex-direction: column; }
.message__list { flex: 1; overflow-y: auto; max-height: 48vh; padding: 10px 4px; }
.message__bubble { max-width: 70%; padding: 10px 14px; border-radius: 12px; margin-bottom: 10px; background: #f5f7fb; width: fit-content; }
.message__bubble--me { margin-left: auto; background: #2563eb; color: #fff; }
.message__input { display: flex; gap: 10px; border-top: 1px solid #f0f2f5; padding-top: 12px; margin-top: 12px; }
@media (max-width: 860px) { .message { grid-template-columns: 1fr; } }
</style>
