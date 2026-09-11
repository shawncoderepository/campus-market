import { fileURLToPath, URL } from 'node:url'
import vue from '@vitejs/plugin-vue'
import { defineConfig, loadEnv } from 'vite'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')

  return {
    // 组件不自动注册，各 Vue 文件显式导入自身使用的 Ant Design Vue 组件。
    plugins: [vue()],
    resolve: {
      alias: { '@': fileURLToPath(new URL('./src', import.meta.url)) },
    },
    // 资源基础路径与路由 history 的 base 应保持一致。
    base: env.VITE_ROUTE_BASE || '/',
    server: {
      host: true,
      port: 5173,
      strictPort: true,
      // 代理到本地 FastAPI 后端；/uploads 为商品图片等静态资源。
      proxy: {
        '/api': { target: 'http://localhost:8000', changeOrigin: true },
        '/uploads': { target: 'http://localhost:8000', changeOrigin: true },
      },
    },
    build: { outDir: 'dist', emptyOutDir: true },
  }
})
