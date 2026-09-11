<script setup lang="ts">
import { computed } from 'vue'
import { RouterView } from 'vue-router'
import { App as AApp, ConfigProvider as AConfigProvider } from 'ant-design-vue'

const appTitle = computed(() => import.meta.env.VITE_APP_TITLE || 'OrbAI Vue Template')
</script>

<template>
  <!-- 主题令牌集中配置，后续换肤时只修改这一处。 -->
  <a-config-provider
    :theme="{
      token: {
        colorPrimary: '#2563eb',
        borderRadius: 8,
        colorBgLayout: '#f5f7fb',
      },
    }"
  >
    <a-app>
      <div class="page-transition-wrap">
        <RouterView v-slot="{ Component }">
          <Transition name="page">
            <component :is="Component" :key="$route.fullPath" />
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
