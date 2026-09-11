import { createApp } from 'vue'
import 'ant-design-vue/dist/reset.css'
import './styles/index.css'
import App from './App.vue'
import setupPlugins from './plugin'

/**
 * 应用唯一入口：全局插件统一在此注册，业务模块不要重复创建 Vue 实例。
 */
const app = createApp(App)

setupPlugins(app)
app.mount('#app')
