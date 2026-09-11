import http from '@/plugin/axios'
import type { PageResult } from '@/common/types/api'
import type { GoodsItem } from '@/common/types/business'

export function toggleFavorite(productId: number) {
  return http.post<{ is_favorited: boolean }>('/favorite/toggle', { product_id: productId })
}

export function getMyFavorites(params: { page?: number; page_size?: number }) {
  return http.get<PageResult<GoodsItem>>('/favorite/list', params)
}
