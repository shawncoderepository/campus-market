import http from '@/plugin/axios'
import type { BargainRecord, BargainSession } from '@/common/types/business'

export function buyerOffer(data: { product_id: number; offer_price: number; message?: string }) {
  return http.post<BargainRecord>('/bargain/offer', data)
}

export function sellerReply(data: { product_id: number; buyer_id: number; offer_price: number; message?: string }) {
  return http.post<BargainRecord>('/bargain/reply', data)
}

export function respondBargain(data: { record_id: number; accept: boolean }) {
  return http.post<BargainRecord>('/bargain/respond', data)
}

export function getBargainSession(productId: number, buyerId?: number) {
  return http.get<BargainSession>('/bargain/session', { product_id: productId, buyer_id: buyerId })
}

export function getMyBargains() {
  return http.get<BargainRecord[]>('/bargain/my')
}
