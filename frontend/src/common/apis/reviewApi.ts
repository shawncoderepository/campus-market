import http from '@/plugin/axios'
import type { PageResult } from '@/common/types/api'
import type { Review } from '@/common/types/business'

export function createReview(data: { order_id: number; rating: number; content?: string; tags?: string[] }) {
  return http.post<Review>('/review/create', data)
}

export function getReceivedReviews(userId: number, params: { page?: number; page_size?: number }) {
  return http.get<PageResult<Review>>(`/review/received/${userId}`, params)
}
