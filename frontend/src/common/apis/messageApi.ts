import http from '@/plugin/axios'
import type { PageResult } from '@/common/types/api'
import type { ChatMessage, Conversation } from '@/common/types/business'

export function sendMessage(data: { receiver_id: number; product_id?: number; content: string }) {
  return http.post<ChatMessage>('/message/send', data)
}

export function getConversations() {
  return http.get<Conversation[]>('/message/conversations')
}

export function getChatHistory(params: { peer_id: number; product_id?: number; page?: number; page_size?: number }) {
  return http.get<PageResult<ChatMessage>>('/message/history', params)
}

export function getUnreadCount() {
  return http.get<{ count: number }>('/message/unread')
}
