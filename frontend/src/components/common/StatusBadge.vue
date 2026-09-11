<script setup lang="ts">
import { computed } from 'vue'
import { Tag as ATag } from 'ant-design-vue'

const props = defineProps<{ status: 'enabled' | 'disabled' | 'pending' }>()

const presentation = computed(() => ({
  enabled: { color: 'success', text: '已启用' },
  disabled: { color: 'default', text: '已停用' },
  pending: { color: 'processing', text: '处理中' },
}[props.status]))
</script>

<template>
  <a-tag :color="presentation.color">{{ presentation.text }}</a-tag>
</template>
