<script setup lang="ts">
import { computed, h, ref } from 'vue'
import { RouterView, useRoute, useRouter } from 'vue-router'
import {
  Avatar as AAvatar,
  Button as AButton,
  Layout as ALayout,
  LayoutContent as ALayoutContent,
  LayoutFooter as ALayoutFooter,
  LayoutHeader as ALayoutHeader,
  LayoutSider as ALayoutSider,
  Menu as AMenu,
} from 'ant-design-vue'
import {
  AppstoreOutlined,
  DashboardOutlined,
  FlagOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  ShopOutlined,
  ShoppingCartOutlined,
  TeamOutlined,
} from '@ant-design/icons-vue'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const collapsed = ref(false)

const selectedKeys = computed(() => [route.path])
const menuItems = [
  { key: '/admin/dashboard', label: '数据概览', icon: () => h(DashboardOutlined) },
  { key: '/admin/goods', label: '商品管理', icon: () => h(ShopOutlined) },
  { key: '/admin/order', label: '订单管理', icon: () => h(ShoppingCartOutlined) },
  { key: '/admin/report', label: '举报处理', icon: () => h(FlagOutlined) },
  { key: '/admin/user', label: '用户管理', icon: () => h(TeamOutlined) },
  { key: '/admin/category', label: '分类管理', icon: () => h(AppstoreOutlined) },
]

function handleMenuClick({ key }: { key: string | number }) {
  void router.push(String(key))
}
</script>

<template>
  <a-layout class="admin-layout">
    <a-layout-sider v-model:collapsed="collapsed" collapsible :trigger="null" breakpoint="lg">
      <div class="brand">
        <span class="brand__mark">管</span>
        <span v-if="!collapsed" class="brand__name">校园淘 · 管理端</span>
      </div>
      <a-menu
        theme="dark"
        mode="inline"
        :items="menuItems"
        :selected-keys="selectedKeys"
        @click="handleMenuClick"
      />
    </a-layout-sider>

    <a-layout>
      <a-layout-header class="topbar">
        <a-button type="text" class="topbar__toggle" @click="collapsed = !collapsed">
          <MenuUnfoldOutlined v-if="collapsed" />
          <MenuFoldOutlined v-else />
        </a-button>
        <div class="topbar__right">
          <a-button type="link" @click="router.push('/')">返回前台</a-button>
          <a-avatar>{{ (userStore.user?.nickname || 'A').slice(0, 1) }}</a-avatar>
        </div>
      </a-layout-header>

      <a-layout-content class="content">
        <RouterView />
      </a-layout-content>
      <a-layout-footer class="footer">校园二手交易管理后台</a-layout-footer>
    </a-layout>
  </a-layout>
</template>

<style scoped>
.admin-layout { min-height: 100vh; }
.brand { height: 64px; display: flex; align-items: center; justify-content: center; gap: 10px; color: #fff; overflow: hidden; }
.brand__mark { display: grid; flex: 0 0 auto; width: 32px; height: 32px; place-items: center; border-radius: 9px; background: #2563eb; font-weight: 800; }
.brand__name { white-space: nowrap; font-weight: 650; }
.topbar { display: flex; align-items: center; justify-content: space-between; height: 64px; padding: 0 20px; background: #fff; border-bottom: 1px solid #edf0f5; }
.topbar__toggle { font-size: 18px; }
.topbar__right { display: flex; align-items: center; gap: 12px; }
.content { min-width: 0; margin: 20px; }
.footer { padding: 16px; color: #98a2b3; text-align: center; }
@media (max-width: 640px) { .content { margin: 12px; } }
</style>
