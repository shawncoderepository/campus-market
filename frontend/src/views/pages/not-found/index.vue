<script setup lang="ts">
import { useRouter } from 'vue-router'
import { Button as AButton, Result as AResult } from 'ant-design-vue'

const router = useRouter()
</script>

<template>
  <div class="not-found">
    <a-result status="404" title="404" sub-title="抱歉，你访问的页面不存在。">
      <template #extra><a-button type="primary" @click="router.replace('/')">返回首页</a-button></template>
    </a-result>
  </div>
</template>

<style scoped>
.not-found { display: grid; min-height: 100vh; place-items: center; background: #f5f7fb; }
</style>
