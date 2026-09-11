<script setup lang="ts">
withDefaults(
  defineProps<{
    title: string
    description?: string
  }>(),
  { description: '' },
)
</script>

<template>
  <header class="page-header">
    <div>
      <h1>{{ title }}</h1>
      <p v-if="description">{{ description }}</p>
    </div>
    <!-- 具名插槽让调用方按需放置按钮、筛选器等操作。 -->
    <div v-if="$slots.extra" class="page-header__extra">
      <slot name="extra" />
    </div>
  </header>
</template>

<style scoped>
.page-header { display: flex; align-items: flex-start; justify-content: space-between; gap: 16px; }
h1 { margin: 0; color: #172033; font-size: 24px; line-height: 1.35; }
p { margin: 6px 0 0; color: #667085; }
.page-header__extra { display: flex; flex-wrap: wrap; gap: 8px; }
@media (max-width: 640px) { .page-header { flex-direction: column; } }
</style>
