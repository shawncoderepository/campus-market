import http from '@/plugin/axios'
import type { AiBargainResult, AiCopyResult, AiEstimateResult } from '@/common/types/business'

export function aiCopy(data: { keywords: string; category_name?: string; condition_level?: number; original_price?: number }) {
  return http.post<AiCopyResult>('/ai/copy', data)
}

export function aiEstimate(data: { category_name?: string; original_price: number; condition_level?: number; used_years?: number }) {
  return http.post<AiEstimateResult>('/ai/estimate', data)
}

export function aiBargain(data: {
  product_title: string
  sell_price: number
  buyer_offer: number
  buyer_message?: string
  round_no?: number
  side?: string
}) {
  return http.post<AiBargainResult>('/ai/bargain', data)
}
