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
  Tag as ATag,
} from 'ant-design-vue'
import {
  AppstoreOutlined,
  CloudOutlined,
  DashboardOutlined,
  DatabaseOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  UnorderedListOutlined,
} from '@ant-design/icons-vue'

const route = useRoute()
const router = useRouter()
const collapsed = ref(false)

const selectedKeys = computed(() => [route.path])
const menuItems = [
  { key: '/dashboard', label: '工作台', icon: () => h(DashboardOutlined) },
  { key: '/order', label: '订单示例', icon: () => h(UnorderedListOutlined) },
  { key: '/components', label: '组件示例', icon: () => h(AppstoreOutlined) },
  { key: '/request', label: '请求示例', icon: () => h(CloudOutlined) },
  { key: '/state', label: '状态管理', icon: () => h(DatabaseOutlined) },
]

function handleMenuClick({ key }: { key: string | number }) {
  void router.push(String(key))
}
</script>

<template>
  <a-layout class="app-layout">
    <a-layout-sider v-model:collapsed="collapsed" collapsible :trigger="null" breakpoint="lg">
      <div class="brand">
        <span class="brand__mark">O</span>
        <span v-if="!collapsed" class="brand__name">OrbAI Template</span>
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
          <a-tag color="blue">开发模板</a-tag>
          <a-avatar>O</a-avatar>
        </div>
      </a-layout-header>

      <a-layout-content class="content">
        <RouterView />
      </a-layout-content>
      <a-layout-footer class="footer">OrbAI Vue Template · Vue 3 + TypeScript</a-layout-footer>
    </a-layout>
  </a-layout>
</template>

<style scoped>
.app-layout { min-height: 100vh; }
.brand { height: 64px; display: flex; align-items: center; justify-content: center; gap: 10px; color: #fff; overflow: hidden; }
.brand__mark { display: grid; flex: 0 0 auto; width: 32px; height: 32px; place-items: center; border-radius: 9px; background: linear-gradient(135deg, #ff8a3d, #ff6a00); font-weight: 800; }
.brand__name { white-space: nowrap; font-weight: 650; }
.topbar { display: flex; align-items: center; justify-content: space-between; height: 64px; padding: 0 20px; background: #fff; border-bottom: 1px solid #edf0f5; }
.topbar__toggle { font-size: 18px; }
.topbar__right { display: flex; align-items: center; gap: 12px; }
.content { min-width: 0; margin: 20px; }
.footer { padding: 16px; color: #98a2b3; text-align: center; }
@media (max-width: 640px) { .content { margin: 12px; } }
</style>
