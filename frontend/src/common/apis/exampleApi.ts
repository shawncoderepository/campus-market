import { http } from '@/plugin/axios'
import type { PageResult } from '@/common/types/api'

export interface ExampleItem {
  id: number
  name: string
  status: 'enabled' | 'disabled'
  createdAt: string
}

export interface CreateExampleItemPayload {
  name: string
}

const mockItems: ExampleItem[] = [
  { id: 1, name: '示例记录 A', status: 'enabled', createdAt: '2026-01-12 09:30' },
  { id: 2, name: '示例记录 B', status: 'disabled', createdAt: '2026-02-18 14:20' },
  { id: 3, name: '示例记录 C', status: 'enabled', createdAt: '2026-03-26 17:45' },
]

/**
 * 列表查询示例。开发环境默认返回本地假数据，便于模板开箱预览；
 * 设置 VITE_ENABLE_MOCK=false 后会请求真实的 GET /examples。
 */
export async function getExampleList(): Promise<PageResult<ExampleItem>> {
  if (import.meta.env.VITE_ENABLE_MOCK === 'true') {
    await new Promise((resolve) => window.setTimeout(resolve, 450))
    return { list: mockItems, total: mockItems.length, page: 1, pageSize: 10 }
  }

  return http.get<PageResult<ExampleItem>>('/examples')
}

/** POST 新增示例。开发环境返回本地模拟结果，生产环境请求 POST /examples。 */
export async function createExampleItem(payload: CreateExampleItemPayload): Promise<ExampleItem> {
  if (import.meta.env.VITE_ENABLE_MOCK === 'true') {
    await new Promise((resolve) => window.setTimeout(resolve, 350))
    return {
      id: Date.now(),
      name: payload.name,
      status: 'enabled',
      createdAt: new Date().toLocaleString('zh-CN'),
    }
  }

  return http.post<ExampleItem, CreateExampleItemPayload>('/examples', payload)
}
