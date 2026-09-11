import { computed, ref } from 'vue'
import { defineStore } from 'pinia'

/**
 * Pinia Setup Store 示例：展示 state、getter 和 action 的基本写法。
 * 新业务请复制此结构并按领域命名，例如 useUserStore。
 */
export const useCounterStore = defineStore('counter', () => {
  const count = ref(0)
  const history = ref<number[]>([])
  const doubled = computed(() => count.value * 2)

  function increment() {
    count.value += 1
    history.value.push(count.value)
  }

  function reset() {
    count.value = 0
    history.value = []
  }

  return { count, history, doubled, increment, reset }
})
