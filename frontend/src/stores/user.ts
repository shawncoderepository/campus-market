import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import type { User } from '@/common/types/business'
import * as userApi from '@/common/apis/userApi'

/** 登录态 Store：token 持久化在 localStorage，用户信息缓存于内存。 */
export const useUserStore = defineStore('user', () => {
  const token = ref<string>(localStorage.getItem('access_token') || '')
  const user = ref<User | null>(null)

  const isLoggedIn = computed(() => !!token.value)
  const isAdmin = computed(() => user.value?.role === 2)

  async function login(username: string, password: string) {
    const res = await userApi.login({ username, password })
    token.value = res.token
    user.value = res.user
    localStorage.setItem('access_token', res.token)
    return res.user
  }

  async function fetchMe() {
    if (!token.value) return null
    try {
      user.value = await userApi.getMe()
      return user.value
    } catch {
      logout()
      return null
    }
  }

  function logout() {
    token.value = ''
    user.value = null
    localStorage.removeItem('access_token')
  }

  return { token, user, isLoggedIn, isAdmin, login, fetchMe, logout }
})
