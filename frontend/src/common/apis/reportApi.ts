import http from '@/plugin/axios'
import type { PageResult } from '@/common/types/api'

export interface Report {
  id: number
  reporter_id: number
  reporter_nickname: string
  product_id: number
  product_title: string
  reason: string
  status: number
  handler_result: string
  created_at?: string
}

export function createReport(data: { product_id: number; reason: string }) {
  return http.post<Report>('/report/create', data)
}

export function getMyReports(params: { page?: number; page_size?: number }) {
  return http.get<PageResult<Report>>('/report/my', params)
}
