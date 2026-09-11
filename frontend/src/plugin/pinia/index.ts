import type { App } from 'vue'
import { createPinia } from 'pinia'

/** 全局只创建一个 Pinia 实例，具体状态按领域拆分 store 文件。 */
const pinia = createPinia()

/** 由 plugin/index.ts 统一调用并注册 Pinia。 */
export function setup(app: App) {
  app.use(pinia)
}

export default pinia
