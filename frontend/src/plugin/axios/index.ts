import axios, { type AxiosRequestConfig } from 'axios'
import type { ApiResponse } from '@/common/types/api'
import { setupInterceptors } from './interceptors'

/**
 * 统一 HTTP 实例：领域 API 只通过此插件发起请求，不直接创建 axios 实例。
 */
const axiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: Number(import.meta.env.VITE_API_TIMEOUT) || 10_000,
})

setupInterceptors(axiosInstance)

/** 内部统一执行与响应解包，业务模块不直接调用此函数。 */
async function execute<T>(config: AxiosRequestConfig): Promise<T> {
  const response = await axiosInstance.request<ApiResponse<T>>(config)
  const body = response.data
  if (body.code !== 0) throw new Error(body.message || '接口返回异常')
  return body.data
}

/**
 * 业务统一使用的 HTTP 客户端。
 * 调用示例：http.get<T>(url, params)、http.post<T>(url, data)。
 */
export const http = {
  get<T>(url: string, params?: unknown, config: AxiosRequestConfig = {}) {
    return execute<T>({ ...config, url, params, method: 'GET' })
  },

  post<T, D = unknown>(url: string, data?: D, config: AxiosRequestConfig<D> = {}) {
    return execute<T>({ ...config, url, data, method: 'POST' })
  },

  put<T, D = unknown>(url: string, data?: D, config: AxiosRequestConfig<D> = {}) {
    return execute<T>({ ...config, url, data, method: 'PUT' })
  },

  delete<T>(url: string, config: AxiosRequestConfig = {}) {
    return execute<T>({ ...config, url, method: 'DELETE' })
  },
}

export default http
