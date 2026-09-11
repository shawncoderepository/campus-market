import http from '@/plugin/axios'
import type { PageResult } from '@/common/types/api'
import type { Order } from '@/common/types/business'

export function createOrder(data: {
  product_id: number
  bargain_record_id?: number
  address?: string
  remark?: string
}) {
  return http.post<Order>('/order/create', data)
}

export function payOrder(orderId: number) {
  return http.post<Order>('/order/pay', { order_id: orderId })
}

export function shipOrder(orderId: number) {
  return http.post<Order>('/order/ship', { order_id: orderId })
}

export function confirmOrder(orderId: number) {
  return http.post<Order>('/order/confirm', { order_id: orderId })
}

export function cancelOrder(orderId: number) {
  return http.post<Order>('/order/cancel', { order_id: orderId })
}

export function getMyOrders(params: { role?: string; page?: number; page_size?: number }) {
  return http.get<PageResult<Order>>('/order/my', params)
}
