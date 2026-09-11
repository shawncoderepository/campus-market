import http from '@/plugin/axios'
import type { PageResult } from '@/common/types/api'
import type { Category, GoodsDetail, GoodsItem } from '@/common/types/business'

export interface GoodsListQuery {
  keyword?: string
  category_id?: number
  min_price?: number
  max_price?: number
  condition_level?: number
  sort?: string
  page?: number
  page_size?: number
}

export interface PublishData {
  category_id: number
  title: string
  description: string
  original_price: number
  sell_price: number
  condition_level: number
  images: string[]
}

export function getCategories() {
  return http.get<Category[]>('/category/list')
}

export function publishGoods(data: PublishData) {
  return http.post<GoodsItem>('/goods/publish', data)
}

export function getGoodsList(params: GoodsListQuery) {
  return http.get<PageResult<GoodsItem>>('/goods/list', params)
}

export function getGoodsDetail(id: number) {
  return http.get<GoodsDetail>(`/goods/detail/${id}`)
}

export function updateGoods(id: number, data: Partial<PublishData> & { status?: number }) {
  return http.put<GoodsItem>(`/goods/${id}`, data)
}

export function offShelfGoods(id: number) {
  return http.delete<null>(`/goods/${id}`)
}

export function getMyGoods(params: { page?: number; page_size?: number }) {
  return http.get<PageResult<GoodsItem>>('/goods/my/list', params)
}

export async function uploadImage(file: File): Promise<string> {
  const formData = new FormData()
  formData.append('file', file)
  const res = await http.post<{ url: string }>('/goods/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return res.url
}
