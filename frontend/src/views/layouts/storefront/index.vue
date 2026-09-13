<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
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
import { getMyBargains } from '@/common/apis/bargainApi'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const keyword = ref('')
const unread = ref(0)
const bargainPending = ref(0)
let badgeTimer: ReturnType<typeof setInterval> | null = null

const avatarText = computed(() => (userStore.user?.nickname || userStore.user?.username || '我').slice(0, 1))

function onSearch() {
  const kw = keyword.value.trim()
  void router.push({ path: '/', query: kw ? { keyword: kw } : {} })
}

function go(path: string) {
  void router.push(path)
}

function isActive(path: string) {
  return route.path.startsWith(path)
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

// 待我响应的议价数：会话最新一条为待响应(status=1)且出自对方
async function refreshBargainPending() {
  if (!userStore.isLoggedIn) return
  try {
    const list = await getMyBargains()
    const myId = userStore.user?.id
    bargainPending.value = list.filter((r) => {
      if (r.status !== 1) return false
      const iAmSeller = r.seller_id === myId
      // 我是卖家则待响应的是买家出价；我是买家则待响应的是卖家还价
      return iAmSeller ? r.role === 'buyer' : r.role === 'seller'
    }).length
  } catch {
    /* 忽略议价数拉取失败 */
  }
}

function refreshBadges() {
  refreshUnread()
  refreshBargainPending()
}

// 路由 query 变化时同步搜索框（如 Hero 区搜索、回退前进）
watch(
  () => route.query.keyword,
  (val) => {
    keyword.value = String(val || '')
  },
)

onMounted(() => {
  keyword.value = String(route.query.keyword || '')
  refreshBadges()
  // 轮询保持角标最新（新消息/新出价及时出现）
  badgeTimer = setInterval(refreshBadges, 5000)
})

onUnmounted(() => {
  if (badgeTimer) clearInterval(badgeTimer)
})

// 从消息/议价页返回或切换路由后刷新角标（已读/已响应后及时清除）
watch(
  () => route.path,
  () => refreshBadges(),
)
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
          <!-- 导航菜单：首页文字 + 纯图标横排 -->
          <nav class="nav__links">
            <div class="nav__link nav__link--text" :class="{ active: route.path === '/' }" @click="go('/')">首页</div>
            <a-badge :count="unread" :offset="[4, 2]" :number-style="{ fontSize: '10px' }">
              <div class="nav__link" :class="{ active: isActive('/message') }" title="消息" @click="go('/message')">
                <MessageOutlined class="nav__link-icon" />
              </div>
            </a-badge>
            <a-badge :count="bargainPending" :offset="[4, 2]" :number-style="{ fontSize: '10px' }">
              <div class="nav__link" :class="{ active: isActive('/bargain') }" title="议价" @click="go('/bargain')">
                <TagsOutlined class="nav__link-icon" />
              </div>
            </a-badge>
            <div class="nav__link" :class="{ active: isActive('/favorites') }" title="收藏" @click="go('/favorites')">
              <HeartOutlined class="nav__link-icon" />
            </div>
            <div class="nav__link" :class="{ active: isActive('/order') }" title="订单" @click="go('/order')">
              <ShoppingOutlined class="nav__link-icon" />
            </div>
          </nav>

          <span class="nav__divider"></span>

          <a-button type="primary" size="large" class="nav__publish" @click="go('/publish')">
            <template #icon><PlusOutlined /></template>
            发布闲置
          </a-button>

          <a-dropdown v-if="userStore.isLoggedIn" trigger="click">
            <div class="nav__user">
              <a-avatar class="nav__avatar" :src="userStore.user?.avatar || undefined">
                {{ avatarText }}
              </a-avatar>
              <span class="nav__username">{{ userStore.user?.nickname || userStore.user?.username }}</span>
            </div>
            <template #overlay>
              <a-menu @click="onUserMenuClick">
                <a-menu-item key="/my"><UserOutlined /> 个人中心</a-menu-item>
                <a-menu-item v-if="userStore.isAdmin" key="/admin">进入后台</a-menu-item>
                <a-menu-item key="logout">退出登录</a-menu-item>
              </a-menu>
            </template>
          </a-dropdown>
          <a-button v-else type="primary" ghost size="large" @click="go('/login')">登录 / 注册</a-button>
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
.storefront { height: 100vh; display: flex; flex-direction: column; background: var(--bg, #faf7f2); overflow: hidden; }
.nav { flex-shrink: 0; z-index: 100; background: #fff; border-bottom: 1px solid #f2ece4; box-shadow: 0 2px 10px rgba(43,38,34,0.04); }
.nav__inner { display: flex; align-items: center; gap: 20px; width: 100%; max-width: 1440px; margin: 0 auto; padding: 0 28px; height: 64px; }
.nav__brand { display: flex; align-items: center; gap: 10px; cursor: pointer; flex-shrink: 0; }
.nav__logo { width: 38px; height: 38px; display: grid; place-items: center; border-radius: 12px; background: linear-gradient(135deg, #ff8a3d, #ff6a00); color: #fff; font-weight: 800; font-size: 19px; box-shadow: 0 4px 12px rgba(255,106,0,0.3); }
.nav__title { font-size: 19px; font-weight: 800; background: linear-gradient(120deg, #ff6a00, #ff5e3a); -webkit-background-clip: text; background-clip: text; color: transparent; }

/* 中间搜索框：自适应伸展占据剩余空间 */
.nav__search { flex: 1; max-width: 520px; margin: 0 auto; }

/* 右侧操作区 */
.nav__actions { display: flex; align-items: center; gap: 10px; flex-shrink: 0; }
.nav__links { display: flex; align-items: center; gap: 2px; }
.nav__link { display: grid; place-items: center; width: 38px; height: 38px; border-radius: 10px; cursor: pointer; color: #6b645d; transition: color 0.15s ease, background-color 0.15s ease; }
.nav__link--text { width: auto; padding: 0 12px; font-size: 15px; font-weight: 600; white-space: nowrap; }
.nav__link--text.active { color: #ff6a00; }
.nav__link:hover { color: #ff6a00; background: #fff1e6; }
.nav__link.active { color: #ff6a00; background: #fff1e6; }
.nav__link-icon { font-size: 19px; }
.nav__divider { width: 1px; height: 22px; background: #f0e9e1; margin: 0 4px; }
.nav__publish { flex-shrink: 0; box-shadow: 0 4px 12px rgba(255,106,0,0.28); }
.nav__user { display: flex; align-items: center; gap: 8px; cursor: pointer; padding: 4px 8px 4px 4px; border-radius: 22px; transition: background 0.15s ease; }
.nav__user:hover { background: #fff1e6; }
.nav__username { font-size: 14px; color: #2b2622; max-width: 90px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.nav__avatar { background: linear-gradient(135deg, #ff8a3d, #ff6a00); flex-shrink: 0; }

.storefront__main { flex: 1; width: 100%; padding: 20px 28px 24px; overflow-y: auto; display: flex; flex-direction: column; }
.storefront__main > * { flex-shrink: 0; }
.storefront__footer { flex-shrink: 0; padding: 10px 20px; text-align: center; color: var(--ink-faint, #c9c2ba); font-size: 13px; background: transparent; }
@media (max-width: 1100px) {
  .nav__search { width: 280px; }
}
@media (max-width: 1100px) {
  .nav__username { display: none; }
}
@media (max-width: 900px) {
  .nav__publish { display: none; }
  .nav__divider { display: none; }
}
@media (max-width: 768px) {
  .nav__inner { gap: 12px; padding: 0 16px; }
  .nav__title { display: none; }
  .nav__search { max-width: none; }
}
</style>
