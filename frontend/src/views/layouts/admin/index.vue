<script setup lang="ts">
import { computed, h, onMounted, ref } from 'vue'
import { RouterView, useRoute, useRouter } from 'vue-router'
import {
  Avatar as AAvatar,
  Badge as ABadge,
  Breadcrumb as ABreadcrumb,
  BreadcrumbItem as ABreadcrumbItem,
  Button as AButton,
  Dropdown as ADropdown,
  Empty as AEmpty,
  Layout as ALayout,
  LayoutContent as ALayoutContent,
  LayoutHeader as ALayoutHeader,
  LayoutSider as ALayoutSider,
  Menu as AMenu,
  MenuItem as AMenuItem,
  Tooltip as ATooltip,
} from 'ant-design-vue'
import {
  AppstoreOutlined,
  BellOutlined,
  DashboardOutlined,
  FlagOutlined,
  HomeOutlined,
  InfoCircleOutlined,
  LogoutOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  ShopOutlined,
  ShoppingCartOutlined,
  TeamOutlined,
} from '@ant-design/icons-vue'
import { useUserStore } from '@/stores/user'
import { getAdminActivities, getAdminStats } from '@/common/apis/adminApi'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const collapsed = ref(false)
const noticeVisible = ref(false)
const pendingReportCount = ref(0)

const selectedKeys = computed(() => [route.path])
const openKeys = ref(['/admin'])

// 通知数据：来自后端真实动态，已读状态持久化到 localStorage
interface Notice {
  id: string
  text: string
  time: string
  color: string
  icon: ReturnType<typeof h> | null
  link: string
  read: boolean
}

const READ_KEY = 'admin_notice_read'
const readIds = ref<Set<string>>(new Set(JSON.parse(localStorage.getItem(READ_KEY) || '[]')))
const notices = ref<Notice[]>([])

// 依据动态 id 前缀映射图标与跳转页面
const TYPE_META: Record<string, { icon: () => ReturnType<typeof h>; link: string }> = {
  product: { icon: () => h(ShopOutlined), link: '/admin/goods' },
  order: { icon: () => h(ShoppingCartOutlined), link: '/admin/order' },
  report: { icon: () => h(FlagOutlined), link: '/admin/report' },
  user: { icon: () => h(TeamOutlined), link: '/admin/user' },
}

function persistRead() {
  localStorage.setItem(READ_KEY, JSON.stringify([...readIds.value]))
}

async function loadNotices() {
  try {
    const acts = await getAdminActivities()
    notices.value = acts.map((a) => {
      const type = a.id.split('-')[0]
      const meta = TYPE_META[type] ?? { icon: () => h(InfoCircleOutlined), link: '/admin/dashboard' }
      return {
        id: a.id,
        text: a.target ? `${a.user} ${a.action}「${a.target}」` : `${a.user} ${a.action}`,
        time: a.time,
        color: a.color,
        icon: meta.icon(),
        link: meta.link,
        read: readIds.value.has(a.id),
      }
    })
  } catch {
    notices.value = []
  }
}

const unreadCount = computed(() => notices.value.filter((n) => !n.read).length)

function onNoticeClick(item: Notice) {
  item.read = true
  readIds.value.add(item.id)
  persistRead()
  noticeVisible.value = false
  void router.push(item.link)
}

function markAllRead() {
  notices.value.forEach((n) => {
    n.read = true
    readIds.value.add(n.id)
  })
  persistRead()
}

// 面包屑
const breadcrumbs = computed(() => {
  const items = [{ title: '首页', path: '/admin/dashboard' }]
  const current = menuItems.value.find((m) => m.key === route.path)
  if (current && route.path !== '/admin/dashboard') {
    items.push({ title: current.label, path: route.path })
  }
  return items
})

const menuItems = computed(() => [
  { key: '/admin/dashboard', label: '数据概览', icon: () => h(DashboardOutlined), color: '#6366f1' },
  { key: '/admin/goods', label: '商品管理', icon: () => h(ShopOutlined), color: '#f59e0b' },
  { key: '/admin/order', label: '订单管理', icon: () => h(ShoppingCartOutlined), color: '#10b981' },
  { key: '/admin/report', label: '举报处理', icon: () => h(FlagOutlined), color: '#ef4444', badge: pendingReportCount.value || undefined },
  { key: '/admin/user', label: '用户管理', icon: () => h(TeamOutlined), color: '#8b5cf6' },
  { key: '/admin/category', label: '分类管理', icon: () => h(AppstoreOutlined), color: '#06b6d4' },
])

function handleMenuClick({ key }: { key: string | number }) {
  void router.push(String(key))
}

function handleLogout() {
  userStore.logout()
  void router.push('/login')
}

onMounted(async () => {
  try {
    const s = await getAdminStats()
    pendingReportCount.value = s.report_pending
  } catch {
    // 忽略角标加载失败
  }
  await loadNotices()
})
</script>

<template>
  <a-layout class="admin-layout" :class="{ 'sidebar-collapsed': collapsed }">
    <!-- 侧边栏 -->
    <a-layout-sider
      v-model:collapsed="collapsed"
      :width="220"
      :collapsed-width="72"
      collapsible
      :trigger="null"
      class="sidebar"
    >
      <!-- Logo -->
      <div class="brand">
        <div class="brand__logo">
          <span class="brand__icon">淘</span>
        </div>
        <transition name="fade">
          <div v-if="!collapsed" class="brand__text">
            <div class="brand__name">校园淘</div>
            <div class="brand__slogan">管理后台</div>
          </div>
        </transition>
      </div>

      <!-- 菜单 -->
      <div class="menu-wrapper">
        <a-menu
          v-model:open-keys="openKeys"
          :selected-keys="selectedKeys"
          mode="inline"
          class="menu"
          @click="handleMenuClick"
        >
          <a-menu-item v-for="item in menuItems" :key="item.key" class="menu-item">
            <div class="menu-item__content">
              <span class="menu-item__icon" :style="{ background: item.color + '20', color: item.color }">
                <component :is="item.icon" />
              </span>
              <span class="menu-item__label">{{ item.label }}</span>
              <a-badge v-if="item.badge && !collapsed" :count="item.badge" class="menu-item__badge" />
            </div>
          </a-menu-item>
        </a-menu>
      </div>

      <!-- 底部用户卡片 -->
      <div class="sidebar-footer">
        <div class="user-card" :class="{ collapsed }">
          <a-avatar :size="collapsed ? 36 : 40" class="user-card__avatar" :src="userStore.user?.avatar || undefined">
            {{ (userStore.user?.nickname || 'A').slice(0, 1) }}
          </a-avatar>
          <transition name="fade">
            <div v-if="!collapsed" class="user-card__info">
              <div class="user-card__name">{{ userStore.user?.nickname || '管理员' }}</div>
              <div class="user-card__role">超级管理员</div>
            </div>
          </transition>
        </div>
      </div>
    </a-layout-sider>

    <a-layout class="main-layout">
      <!-- 顶部导航 -->
      <a-layout-header class="header">
        <div class="header__left">
          <a-button type="text" class="header__toggle" @click="collapsed = !collapsed">
            <MenuUnfoldOutlined v-if="collapsed" />
            <MenuFoldOutlined v-else />
          </a-button>
          <a-breadcrumb class="header__breadcrumb">
            <a-breadcrumb-item v-for="item in breadcrumbs" :key="item.path">
              <router-link :to="item.path">{{ item.title }}</router-link>
            </a-breadcrumb-item>
          </a-breadcrumb>
        </div>

        <div class="header__right">
          <a-tooltip title="返回前台">
            <a-button type="text" class="header__action" @click="router.push('/')">
              <HomeOutlined />
            </a-button>
          </a-tooltip>
          <a-dropdown v-model:open="noticeVisible" :trigger="['click']" placement="bottomRight">
            <a-badge :count="unreadCount" size="small" class="header__badge">
              <a-button type="text" class="header__action" @click.stop="noticeVisible = !noticeVisible">
                <BellOutlined />
              </a-button>
            </a-badge>
            <template #overlay>
              <div class="notice-panel" @click.stop>
                <div class="notice-panel__header">
                  <span class="notice-panel__title">通知中心</span>
                  <a-button type="link" size="small" @click="markAllRead">全部已读</a-button>
                </div>
                <div class="notice-panel__list">
                  <a-empty v-if="!notices.length" description="暂无通知" :image-style="{ height: '60px' }" />
                  <div
                    v-for="item in notices"
                    :key="item.id"
                    class="notice-item"
                    :class="{ unread: !item.read }"
                    @click="onNoticeClick(item)"
                  >
                    <div class="notice-item__icon" :style="{ background: item.color + '15', color: item.color }">
                      <component :is="item.icon" />
                    </div>
                    <div class="notice-item__content">
                      <div class="notice-item__text">{{ item.text }}</div>
                      <div class="notice-item__time">{{ item.time }}</div>
                    </div>
                    <div v-if="!item.read" class="notice-item__dot"></div>
                  </div>
                </div>
                <div class="notice-panel__footer">
                  <a-button type="link" block @click="router.push('/admin/report')">查看全部通知</a-button>
                </div>
              </div>
            </template>
          </a-dropdown>
          <a-dropdown>
            <div class="header__user">
              <a-avatar :size="32" class="header__avatar" :src="userStore.user?.avatar || undefined">
                {{ (userStore.user?.nickname || 'A').slice(0, 1) }}
              </a-avatar>
              <span class="header__username">{{ userStore.user?.nickname || '管理员' }}</span>
            </div>
            <template #overlay>
              <a-menu>
                <a-menu-item key="logout" @click="handleLogout">
                  <LogoutOutlined />
                  退出登录
                </a-menu-item>
              </a-menu>
            </template>
          </a-dropdown>
        </div>
      </a-layout-header>

      <!-- 主内容区 -->
      <a-layout-content class="content">
        <div class="content__inner">
          <RouterView />
        </div>
      </a-layout-content>
    </a-layout>
  </a-layout>
</template>

<style scoped>
/* ===== 整体布局 ===== */
.admin-layout {
  min-height: 100vh;
  background: #f5f7fa;
}

.main-layout {
  background: transparent;
  margin-left: 220px;
  transition: margin-left 0.2s;
}

.admin-layout.sidebar-collapsed .main-layout {
  margin-left: 72px;
}

/* ===== 侧边栏 ===== */
.sidebar {
  background: linear-gradient(180deg, #1e1b4b 0%, #312e81 100%) !important;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.06);
  position: fixed !important;
  left: 0;
  top: 0;
  bottom: 0;
  height: 100vh;
  z-index: 100;
}

.sidebar :deep(.ant-layout-sider-children) {
  overflow: hidden;
}

.sidebar :deep(.ant-layout-sider-children) {
  display: flex;
  flex-direction: column;
}

/* Logo */
.brand {
  height: 72px;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 0 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.brand__logo {
  flex-shrink: 0;
}

.brand__icon {
  display: grid;
  place-items: center;
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #f59e0b, #f97316);
  border-radius: 10px;
  font-weight: 700;
  font-size: 18px;
  color: #fff;
  box-shadow: 0 4px 12px rgba(249, 115, 22, 0.35);
}

.brand__text {
  overflow: hidden;
}

.brand__name {
  font-size: 16px;
  font-weight: 700;
  color: #fff;
  line-height: 1.2;
}

.brand__slogan {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
  letter-spacing: 0.5px;
}

/* 菜单 */
.menu-wrapper {
  flex: 1;
  padding: 12px;
  overflow-y: auto;
}

.menu {
  background: transparent;
  border: none;
}

.menu :deep(.ant-menu-item) {
  height: 44px;
  line-height: 44px;
  margin: 4px 0;
  padding: 0 12px !important;
  border-radius: 8px;
  color: rgba(255, 255, 255, 0.65);
  transition: all 0.2s;
}

.menu :deep(.ant-menu-item:hover) {
  background: rgba(255, 255, 255, 0.08);
  color: #fff;
}

.menu :deep(.ant-menu-item-selected) {
  background: linear-gradient(135deg, rgba(249, 115, 22, 0.9), rgba(234, 88, 12, 0.9)) !important;
  color: #fff !important;
  box-shadow: 0 4px 12px rgba(249, 115, 22, 0.25);
}

.menu :deep(.ant-menu-item-selected .menu-item__icon) {
  background: rgba(255, 255, 255, 0.2) !important;
  color: #fff !important;
}

.menu-item__content {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
}

.menu-item__icon {
  display: grid;
  place-items: center;
  width: 32px;
  height: 32px;
  border-radius: 8px;
  font-size: 15px;
  flex-shrink: 0;
  transition: all 0.2s;
}

.menu-item__label {
  flex: 1;
  font-size: 14px;
  white-space: nowrap;
  overflow: hidden;
}

.menu-item__badge :deep(.ant-badge-count) {
  box-shadow: none;
  font-size: 11px;
  min-width: 18px;
  height: 18px;
  line-height: 18px;
  padding: 0 5px;
}

/* 侧边栏底部 */
.sidebar-footer {
  padding: 12px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
}

.user-card {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px;
  background: rgba(255, 255, 255, 0.06);
  border-radius: 10px;
  transition: all 0.2s;
}

.user-card.collapsed {
  justify-content: center;
  padding: 8px;
}

.user-card__avatar {
  background: linear-gradient(135deg, #f59e0b, #f97316);
  flex-shrink: 0;
}

.user-card__name {
  font-size: 13px;
  font-weight: 600;
  color: #fff;
  line-height: 1.2;
}

.user-card__role {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.45);
}

/* ===== 顶部导航 ===== */
.header {
  height: 64px;
  padding: 0 20px;
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
  position: sticky;
  top: 0;
  z-index: 99;
}

.header__left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header__toggle {
  font-size: 16px;
  color: #64748b;
}

.header__breadcrumb :deep(a) {
  color: #64748b;
}

.header__breadcrumb :deep(.ant-breadcrumb-separator) {
  color: #cbd5e1;
}

.header__right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.header__action {
  font-size: 16px;
  color: #64748b;
}

.header__badge :deep(.ant-badge-count) {
  box-shadow: none;
}

.header__user {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 4px 8px 4px 4px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s;
}

.header__user:hover {
  background: #f1f5f9;
}

.header__avatar {
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
}

.header__username {
  font-size: 13px;
  font-weight: 500;
  color: #334155;
}

/* ===== 内容区 ===== */
.content {
  padding: 20px;
  overflow-y: auto;
}

.content__inner {
  max-width: 1400px;
  margin: 0 auto;
}

/* ===== 动画 ===== */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* ===== 通知面板 ===== */
.notice-panel {
  width: 360px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
  overflow: hidden;
}

.notice-panel__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #f1f5f9;
}

.notice-panel__title {
  font-size: 15px;
  font-weight: 600;
  color: #1e293b;
}

.notice-panel__list {
  max-height: 400px;
  overflow-y: auto;
}

.notice-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 14px 20px;
  cursor: pointer;
  transition: background 0.2s;
  position: relative;
}

.notice-item:hover {
  background: #f8fafc;
}

.notice-item.unread {
  background: #eff6ff;
}

.notice-item.unread:hover {
  background: #dbeafe;
}

.notice-item__icon {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  display: grid;
  place-items: center;
  font-size: 16px;
  flex-shrink: 0;
}

.notice-item__content {
  flex: 1;
  min-width: 0;
}

.notice-item__text {
  font-size: 13px;
  color: #334155;
  line-height: 1.5;
}

.notice-item__time {
  font-size: 11px;
  color: #94a3b8;
  margin-top: 4px;
}

.notice-item__dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #3b82f6;
  flex-shrink: 0;
  margin-top: 6px;
}

.notice-panel__footer {
  padding: 12px 20px;
  border-top: 1px solid #f1f5f9;
}

/* ===== 响应式 ===== */
@media (max-width: 768px) {
  .brand__slogan,
  .header__username {
    display: none;
  }

  .header {
    padding: 0 12px;
  }

  .content {
    padding: 12px;
  }

  .notice-panel {
    width: 300px;
  }
}
</style>
