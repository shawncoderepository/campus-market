<script setup lang="ts">
import { computed } from 'vue'
import { RouterView } from 'vue-router'
import { App as AApp, ConfigProvider as AConfigProvider, message } from 'ant-design-vue'

// 全局消息提示时长：1 秒
message.config({
  duration: 1,
  maxCount: 3,
})

const appTitle = computed(() => import.meta.env.VITE_APP_TITLE || 'OrbAI Vue Template')
</script>

<template>
  <!-- 主题令牌集中配置，后续换肤时只修改这一处。 -->
  <a-config-provider
    :theme="{
      token: {
        colorPrimary: '#ff6a00',
        colorInfo: '#ff6a00',
        colorLink: '#ff6a00',
        borderRadius: 10,
        colorBgLayout: '#faf7f2',
        colorTextBase: '#2b2622',
      },
    }"
  >
    <a-app>
      <div class="page-transition-wrap">
        <RouterView v-slot="{ Component }">
          <Transition name="page">
            <!-- key 用顶层路由路径：同一布局内切换子路由不重建布局，避免整页闪烁 -->
            <component :is="Component" :key="$route.matched[0]?.path || $route.path" />
          </Transition>
        </RouterView>
      </div>
    </a-app>
  </a-config-provider>
</template>

<style>
/* 交叉淡入淡出：离开元素绝对定位脱离文档流，避免布局跳动和闪烁 */
.page-transition-wrap { position: relative; min-height: 100vh; }
.page-enter-active,
.page-leave-active { transition: opacity 0.15s ease; }
.page-enter-from,
.page-leave-to { opacity: 0; }
.page-leave-active { position: absolute; inset: 0; width: 100%; }
</style>
