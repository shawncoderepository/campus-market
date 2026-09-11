<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { Button as AButton, Card as ACard, Form as AForm, FormItem as AFormItem, Input as AInput, InputPassword as AInputPassword, message } from 'ant-design-vue'
import { register } from '@/common/apis/userApi'

const router = useRouter()
const loading = ref(false)
const form = reactive({ username: '', password: '', confirm: '', nickname: '', student_no: '' })

async function onSubmit() {
  if (!form.username || form.username.length < 3) return message.warning('用户名至少 3 个字符')
  if (!form.password || form.password.length < 6) return message.warning('密码至少 6 位')
  if (form.password !== form.confirm) return message.warning('两次密码不一致')
  loading.value = true
  try {
    await register({ username: form.username, password: form.password, nickname: form.nickname, student_no: form.student_no })
    message.success('注册成功，请登录')
    void router.push('/login')
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
        <h2>注册新账号</h2>
        <p>加入校园二手交易</p>
      </div>
      <a-form layout="vertical" @submit.prevent="onSubmit">
        <a-form-item label="用户名" required>
          <a-input v-model:value="form.username" size="large" placeholder="3-32 个字符" />
        </a-form-item>
        <a-form-item label="昵称">
          <a-input v-model:value="form.nickname" size="large" placeholder="选填，默认用户名" />
        </a-form-item>
        <a-form-item label="学号">
          <a-input v-model:value="form.student_no" size="large" placeholder="选填" />
        </a-form-item>
        <a-form-item label="密码" required>
          <a-input-password v-model:value="form.password" size="large" placeholder="至少 6 位" />
        </a-form-item>
        <a-form-item label="确认密码" required>
          <a-input-password v-model:value="form.confirm" size="large" placeholder="再次输入密码" @press-enter="onSubmit" />
        </a-form-item>
        <a-button type="primary" html-type="submit" size="large" block :loading="loading">注 册</a-button>
      </a-form>
      <div class="auth__footer">
        已有账号？<a @click="router.push('/login')">去登录</a>
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
