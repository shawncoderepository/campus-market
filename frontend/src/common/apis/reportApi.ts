import http from '@/plugin/axios'
import type { PageResult } from '@/common/types/api'

export interface Report {
  id: number
  reporter_id: number
  reporter_nickname: string
  product_id: number
  product_title: string
  seller_id: number
  seller_nickname: string
  reason_type: string
  reason_type_name: string
  reason: string
  status: number
  handler_result: string
  created_at?: string
}

export interface ReportReasonType {
  code: string
  name: string
}

export const REPORT_REASON_TYPES: ReportReasonType[] = [
  { code: 'counterfeit', name: '假冒/盗版商品' },
  { code: 'false_info', name: '虚假信息/描述不符' },
  { code: 'prohibited', name: '违禁/违规物品' },
  { code: 'fraud', name: '涉嫌诈骗/诱导线下交易' },
  { code: 'price_abuse', name: '价格异常/恶意抬价' },
  { code: 'spam', name: '垃圾广告/重复刷屏' },
  { code: 'other', name: '其他违规' },
]

export function createReport(data: { product_id: number; reason_type: string; reason: string }) {
  return http.post<Report>('/report/create', data)
}

export function getMyReports(params: { page?: number; page_size?: number }) {
  return http.get<PageResult<Report>>('/report/my', params)
}
