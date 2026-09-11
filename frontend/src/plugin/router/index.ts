import type { App } from 'vue'
import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import StorefrontLayout from '@/views/layouts/storefront/index.vue'
import AdminLayout from '@/views/layouts/admin/index.vue'
import { useUserStore } from '@/stores/user'

/**
 * 路由：/ 前台（商品展示），/admin 后台管理，/login /register 独立页。
 * meta.requiresAuth 需登录，meta.requiresAdmin 需管理员。
 */
const routes: RouteRecordRaw[] = [
  {
    path: '/',
    component: StorefrontLayout,
    children: [
      { path: '', name: 'Home', component: () => import('@/views/pages/home/index.vue'), meta: { title: '首页' } },
      { path: 'goods/:id', name: 'GoodsDetail', component: () => import('@/views/pages/goods-detail/index.vue'), meta: { title: '商品详情' } },
      { path: 'publish', name: 'Publish', component: () => import('@/views/pages/publish/index.vue'), meta: { title: '发布商品', requiresAuth: true } },
      { path: 'favorites', name: 'Favorites', component: () => import('@/views/pages/favorites/index.vue'), meta: { title: '我的收藏', requiresAuth: true } },
      { path: 'bargain', name: 'Bargain', component: () => import('@/views/pages/bargain/index.vue'), meta: { title: '议价中心', requiresAuth: true } },
      { path: 'message', name: 'Message', component: () => import('@/views/pages/message/index.vue'), meta: { title: '消息', requiresAuth: true } },
      { path: 'order', name: 'Order', component: () => import('@/views/pages/order/index.vue'), meta: { title: '我的订单', requiresAuth: true } },
      { path: 'my', name: 'My', component: () => import('@/views/pages/my/index.vue'), meta: { title: '个人中心', requiresAuth: true } },
    ],
  },
  { path: '/login', name: 'Login', component: () => import('@/views/pages/login/index.vue'), meta: { title: '登录' } },
  { path: '/register', name: 'Register', component: () => import('@/views/pages/register/index.vue'), meta: { title: '注册' } },
  {
    path: '/admin',
    component: AdminLayout,
    redirect: '/admin/dashboard',
    meta: { requiresAuth: true, requiresAdmin: true },
    children: [
      { path: 'dashboard', name: 'AdminDashboard', component: () => import('@/views/pages/admin/dashboard/index.vue'), meta: { title: '数据概览' } },
      { path: 'goods', name: 'AdminGoods', component: () => import('@/views/pages/admin/goods/index.vue'), meta: { title: '商品管理' } },
      { path: 'order', name: 'AdminOrder', component: () => import('@/views/pages/admin/order/index.vue'), meta: { title: '订单管理' } },
      { path: 'report', name: 'AdminReport', component: () => import('@/views/pages/admin/report/index.vue'), meta: { title: '举报处理' } },
      { path: 'user', name: 'AdminUser', component: () => import('@/views/pages/admin/user/index.vue'), meta: { title: '用户管理' } },
      { path: 'category', name: 'AdminCategory', component: () => import('@/views/pages/admin/category/index.vue'), meta: { title: '分类管理' } },
    ],
  },
  { path: '/:pathMatch(.*)*', name: 'NotFound', component: () => import('@/views/pages/not-found/index.vue'), meta: { title: '页面不存在' } },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.VITE_ROUTE_BASE || '/'),
  routes,
  scrollBehavior: () => ({ top: 0 }),
})

// 鉴权守卫：未登录跳登录页，非管理员访问 /admin 跳首页。
router.beforeEach(async (to) => {
  const userStore = useUserStore()
  if (userStore.isLoggedIn && !userStore.user) {
    await userStore.fetchMe()
  }
  if (to.meta.requiresAuth && !userStore.isLoggedIn) {
    return { path: '/login', query: { redirect: to.fullPath } }
  }
  if (to.meta.requiresAdmin && !userStore.isAdmin) {
    return { path: '/' }
  }
  return true
})

router.afterEach((to) => {
  const appTitle = import.meta.env.VITE_APP_TITLE || '校园二手交易'
  document.title = to.meta.title ? `${String(to.meta.title)} - ${appTitle}` : appTitle
})

export function setup(app: App) {
  app.use(router)
}

export default router
