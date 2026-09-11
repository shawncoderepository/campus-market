<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { RouterView, useRoute, useRouter } from 'vue-router'
import {
  Avatar as AAvatar,
  Badge as ABadge,
  Button as AButton,
  Dropdown as ADropdown,
  InputSearch as AInputSearch,
  Menu as AMenu,
  MenuItem as AMenuItem,
} from 'ant-design-vue'
import {
  HeartOutlined,
  MessageOutlined,
  PlusOutlined,
  ShoppingOutlined,
  TagsOutlined,
  UserOutlined,
} from '@ant-design/icons-vue'
import { useUserStore } from '@/stores/user'
import { getUnreadCount } from '@/common/apis/messageApi'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const keyword = ref('')
const unread = ref(0)

const avatarText = computed(() => (userStore.user?.nickname || userStore.user?.username || '我').slice(0, 1))

function onSearch() {
  const kw = keyword.value.trim()
  void router.push({ path: '/', query: kw ? { keyword: kw } : {} })
}

function go(path: string) {
  void router.push(path)
}

function onUserMenuClick({ key }: { key: string | number }) {
  if (key === 'logout') {
    userStore.logout()
    void router.push('/login')
  } else {
    go(String(key))
  }
}

async function refreshUnread() {
  if (!userStore.isLoggedIn) return
  try {
    const res = await getUnreadCount()
    unread.value = res.count
  } catch {
    /* 忽略未读数拉取失败 */
  }
}

onMounted(() => {
  keyword.value = String(route.query.keyword || '')
  refreshUnread()
})
</script>

<template>
  <div class="storefront">
    <header class="nav">
      <div class="nav__inner">
        <div class="nav__brand" @click="go('/')">
          <span class="nav__logo">淘</span>
          <span class="nav__title">校园淘</span>
        </div>

        <div class="nav__search">
          <a-input-search
            v-model:value="keyword"
            placeholder="搜索闲置好物，如 教材 / 键盘 / iPad"
            enter-button
            size="large"
            @search="onSearch"
          />
        </div>

        <div class="nav__actions">
          <a-button type="primary" size="large" @click="go('/publish')">
            <template #icon><PlusOutlined /></template>
            发布闲置
          </a-button>

          <a-badge :count="unread" :offset="[-6, 6]">
            <a-button type="text" class="nav__icon" @click="go('/message')">
              <MessageOutlined />
            </a-button>
          </a-badge>
          <a-button type="text" class="nav__icon" @click="go('/bargain')">
            <TagsOutlined />
          </a-button>
          <a-button type="text" class="nav__icon" @click="go('/favorites')">
            <HeartOutlined />
          </a-button>
          <a-button type="text" class="nav__icon" @click="go('/order')">
            <ShoppingOutlined />
          </a-button>

          <a-dropdown v-if="userStore.isLoggedIn" trigger="click">
            <a-avatar class="nav__avatar" :src="userStore.user?.avatar || undefined">
              {{ avatarText }}
            </a-avatar>
            <template #overlay>
              <a-menu @click="onUserMenuClick">
                <a-menu-item key="/my"><UserOutlined /> 个人中心</a-menu-item>
                <a-menu-item v-if="userStore.isAdmin" key="/admin">进入后台</a-menu-item>
                <a-menu-item key="logout">退出登录</a-menu-item>
              </a-menu>
            </template>
          </a-dropdown>
          <a-button v-else type="default" @click="go('/login')">登录 / 注册</a-button>
        </div>
      </div>
    </header>

    <main class="storefront__main">
      <RouterView />
    </main>

    <footer class="storefront__footer">
      校园二手交易与智能议价助手 · 让闲置流动起来
    </footer>
  </div>
</template>

<style scoped>
.storefront { min-height: 100vh; display: flex; flex-direction: column; background: #f5f7fb; }
.nav { position: sticky; top: 0; z-index: 100; background: #fff; border-bottom: 1px solid #edf0f5; box-shadow: 0 2px 8px rgba(0,0,0,0.03); }
.nav__inner { max-width: 1200px; margin: 0 auto; padding: 0 16px; height: 68px; display: flex; align-items: center; gap: 24px; }
.nav__brand { display: flex; align-items: center; gap: 10px; cursor: pointer; flex-shrink: 0; }
.nav__logo { width: 40px; height: 40px; display: grid; place-items: center; border-radius: 10px; background: linear-gradient(135deg, #2563eb, #4f46e5); color: #fff; font-weight: 800; font-size: 20px; }
.nav__title { font-size: 20px; font-weight: 700; color: #1f2937; }
.nav__search { flex: 1; max-width: 480px; }
.nav__actions { display: flex; align-items: center; gap: 8px; flex-shrink: 0; }
.nav__icon { font-size: 20px; color: #4b5563; }
.nav__avatar { cursor: pointer; background: #2563eb; }
.storefront__main { flex: 1; width: 100%; max-width: 1200px; margin: 0 auto; padding: 20px 16px 40px; }
.storefront__footer { padding: 20px; text-align: center; color: #98a2b3; font-size: 13px; }
@media (max-width: 768px) {
  .nav__inner { gap: 12px; }
  .nav__title { display: none; }
  .nav__search { max-width: none; }
}
</style>
