<script setup lang="ts">
import { Button as AButton, Popconfirm as APopconfirm } from 'ant-design-vue'

withDefaults(
  defineProps<{ label?: string; title?: string; danger?: boolean }>(),
  { label: '删除', title: '确定执行此操作吗？', danger: false },
)

const emit = defineEmits<{ confirm: [] }>()
</script>

<template>
  <a-popconfirm :title="title" ok-text="确定" cancel-text="取消" @confirm="emit('confirm')">
    <a-button :danger="danger"><slot>{{ label }}</slot></a-button>
  </a-popconfirm>
</template>
