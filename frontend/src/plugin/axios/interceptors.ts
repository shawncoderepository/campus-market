import type { AxiosError, AxiosInstance } from 'axios'
import { message } from 'ant-design-vue'
import type { ApiResponse } from '@/common/types/api'

/** 集中注册请求与响应拦截器，由 axios/index.ts 创建实例后调用。 */
export function setupInterceptors(instance: AxiosInstance) {
  instance.interceptors.request.use((config) => {
    // 示例：接入登录后可从用户 Store 读取 token，切勿在代码中硬编码密钥。
    const token = localStorage.getItem('access_token')
    if (token) config.headers.Authorization = `Bearer ${token}`
    return config
  })

  instance.interceptors.response.use(
    (response) => {
      const body = response.data as Partial<ApiResponse<unknown>>
      if (typeof body.code === 'number' && body.code !== 0) {
        const error = new Error(body.message || '接口返回异常')
        message.error(error.message)
        return Promise.reject(error)
      }
      return response
    },
    (error: AxiosError<{ message?: string }>) => {
      const text = error.response?.data?.message || error.message || '网络请求失败'
      message.error(text)
      return Promise.reject(error)
    },
  )
}
