import http from '@/plugin/axios'
import type { PageResult } from '@/common/types/api'

export interface AdminStats {
  user_total: number
  goods_total: number
  goods_on_sale: number
  order_total: number
  order_done: number
  deal_amount: number
  report_pending: number
  category_total: number
  review_total: number
  user_wow: number | null
  goods_wow: number | null
  order_wow: number | null
  deal_amount_wow: number | null
  report_wow: number | null
  review_wow: number | null
}

export interface AdminCategoryShare {
  name: string
  count: number
  percent: number
}

export interface AdminActivity {
  id: string
  user: string
  action: string
  target: string
  time: string
  color: string
}

export interface AdminUser {
  id: number
  username: string
  nickname: string
  avatar: string
  phone: string
  student_no: string
  credit_score: number
  role: number
  status: number
  created_at: string
}

export interface AdminCategory {
  id: number
  name: string
  icon: string
  sort: number
  goods_count: number
}

export interface AdminReport {
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
  created_at: string
}

export const getAdminStats = () => http.get<AdminStats>('/admin/stats')

export const getAdminCategoryShare = () => http.get<AdminCategoryShare[]>('/admin/stats/category-share')

export const getAdminActivities = () => http.get<AdminActivity[]>('/admin/stats/activities')

export const getAdminUsers = (params: {
  keyword?: string
  role?: number
  status?: number
  page?: number
  page_size?: number
}) => http.get<PageResult<AdminUser>>('/admin/users', params)

export const setUserStatus = (userId: number, status: number) =>
  http.put<AdminUser>(`/admin/users/${userId}/status`, { status })

export const setUserCredit = (userId: number, credit_score: number) =>
  http.put<AdminUser>(`/admin/users/${userId}/credit`, { credit_score })

export const getAdminCategories = () => http.get<AdminCategory[]>('/admin/categories')

export const createCategory = (data: { name: string; icon: string; sort: number }) =>
  http.post<AdminCategory>('/admin/categories', data)

export const updateCategory = (id: number, data: { name: string; icon: string; sort: number }) =>
  http.put<AdminCategory>(`/admin/categories/${id}`, data)

export const deleteCategory = (id: number) => http.delete<null>(`/admin/categories/${id}`)

export const getAdminReports = (params: { status?: number; page?: number; page_size?: number }) =>
  http.get<PageResult<AdminReport>>('/admin/reports', params)

export const handleReport = (id: number, data: { status: number; handler_result: string }) =>
  http.put<AdminReport>(`/admin/reports/${id}`, data)

export interface AdminGoods {
  id: number
  title: string
  category_name: string
  sell_price: number
  seller_nickname: string
  view_count: number
  status: number
  images: string[]
}

export interface AdminOrder {
  id: number
  order_no: string
  product_title: string
  buyer_nickname: string
  seller_nickname: string
  deal_price: number
  status: number
  address: string
  remark: string
  created_at: string
}

export const getAdminGoods = (params: { keyword?: string; status?: number; page?: number; page_size?: number }) =>
  http.get<PageResult<AdminGoods>>('/admin/goods', params)

export const setGoodsStatus = (id: number, status: number) =>
  http.put<AdminGoods>(`/admin/goods/${id}/status`, { status })

export const getAdminOrders = (params: { status?: number; page?: number; page_size?: number }) =>
  http.get<PageResult<AdminOrder>>('/admin/orders', params)
