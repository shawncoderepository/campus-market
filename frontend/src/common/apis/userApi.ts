import http from '@/plugin/axios'
import type { User } from '@/common/types/business'

export interface LoginResult {
  token: string
  user: User
}

export function register(data: { username: string; password: string; nickname?: string; student_no?: string }) {
  return http.post<User>('/user/register', data)
}

export function login(data: { username: string; password: string }) {
  return http.post<LoginResult>('/user/login', data)
}

export function getMe() {
  return http.get<User>('/user/me')
}

export function updateProfile(data: Partial<Pick<User, 'nickname' | 'avatar' | 'phone' | 'student_no'>>) {
  return http.put<User>('/user/profile', data)
}

export function changePassword(data: { old_password: string; new_password: string }) {
  return http.put<null>('/user/password', data)
}

export interface UserStats {
  goods_total: number
  goods_on_sale: number
  goods_sold: number
  favorite_total: number
  order_buy_total: number
  order_sell_total: number
  review_received_total: number
  avg_rating: number | null
  user_total: number | null
  report_pending: number | null
}

export function getMyStats() {
  return http.get<UserStats>('/user/stats')
}
