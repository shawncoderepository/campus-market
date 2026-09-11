import type { App } from 'vue'
import { setup as setupPinia } from './pinia'
import { setup as setupRouter } from './router'

/**
 * 基础插件统一注册入口。
 * Axios 是请求客户端而非 Vue 插件，由领域 API 从 plugin/axios 显式引用。
 */
const modules = [setupPinia, setupRouter]

export default function setupPlugins(app: App) {
  modules.forEach((setup) => setup(app))
}
