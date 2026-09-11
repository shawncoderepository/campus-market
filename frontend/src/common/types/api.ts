/** 推荐的后端统一响应结构，可按实际接口规范调整。 */
export interface ApiResponse<T> {
  code: number
  message: string
  data: T
}

/** 通用分页结构。 */
export interface PageResult<T> {
  list: T[]
  total: number
  page: number
  pageSize: number
}
