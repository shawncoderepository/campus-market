<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Button as AButton, Card as ACard, Form as AForm, FormItem as AFormItem, Input as AInput, InputPassword as AInputPassword, message } from 'ant-design-vue'
import { LockOutlined, UserOutlined } from '@ant-design/icons-vue'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const loading = ref(false)
const form = reactive({ username: '', password: '' })

async function onSubmit() {
  if (!form.username || !form.password) {
    message.warning('请输入用户名和密码')
    return
  }
  loading.value = true
  try {
    await userStore.login(form.username, form.password)
    message.success('登录成功')
    const redirect = String(route.query.redirect || '/')
    void router.push(redirect)
  } catch {
    /* 拦截器已提示 */
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="auth">
    <a-card class="auth__card">
      <div class="auth__brand">
        <span class="auth__logo">淘</span>
        <h2>欢迎登录校园淘</h2>
        <p>校园二手交易与智能议价助手</p>
      </div>
      <a-form layout="vertical" @submit.prevent="onSubmit">
        <a-form-item label="用户名">
          <a-input v-model:value="form.username" size="large" placeholder="请输入用户名">
            <template #prefix><UserOutlined /></template>
          </a-input>
        </a-form-item>
        <a-form-item label="密码">
          <a-input-password v-model:value="form.password" size="large" placeholder="请输入密码" @press-enter="onSubmit">
            <template #prefix><LockOutlined /></template>
          </a-input-password>
        </a-form-item>
        <a-button type="primary" html-type="submit" size="large" block :loading="loading">登 录</a-button>
      </a-form>
      <div class="auth__footer">
        还没有账号？<a @click="router.push('/register')">立即注册</a>
      </div>
    </a-card>
  </div>
</template>

<style scoped>
.auth { min-height: 100vh; display: grid; place-items: center; background: linear-gradient(135deg, #eef2ff 0%, #f5f7fb 100%); padding: 20px; }
.auth__card { width: 100%; max-width: 400px; border-radius: 14px; box-shadow: 0 8px 30px rgba(37, 99, 235, 0.08); }
.auth__brand { text-align: center; margin-bottom: 24px; }
.auth__logo { display: inline-grid; width: 56px; height: 56px; place-items: center; border-radius: 14px; background: linear-gradient(135deg, #2563eb, #4f46e5); color: #fff; font-size: 28px; font-weight: 800; margin-bottom: 12px; }
.auth__brand h2 { margin: 0 0 4px; font-size: 20px; }
.auth__brand p { margin: 0; color: #98a2b3; font-size: 13px; }
.auth__footer { margin-top: 16px; text-align: center; }
</style>
