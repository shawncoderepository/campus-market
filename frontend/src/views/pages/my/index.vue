<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import {
  Avatar as AAvatar,
  Button as AButton,
  Card as ACard,
  Empty as AEmpty,
  Form as AForm,
  FormItem as AFormItem,
  Input as AInput,
  message,
  Modal as AModal,
  Spin as ASpin,
  Tag as ATag,
  Upload as AUpload,
} from 'ant-design-vue'
import { CameraOutlined, LoadingOutlined } from '@ant-design/icons-vue'
import GoodsCard from '@/components/GoodsCard.vue'
import { getMyGoods, offShelfGoods, uploadImage } from '@/common/apis/goodsApi'
import { getReceivedReviews } from '@/common/apis/reviewApi'
import { updateProfile } from '@/common/apis/userApi'
import { useUserStore } from '@/stores/user'
import type { GoodsItem, Review } from '@/common/types/business'

const router = useRouter()
const userStore = useUserStore()
const goodsLoading = ref(false)
const myGoods = ref<GoodsItem[]>([])
const reviews = ref<Review[]>([])
const editVisible = ref(false)
const saving = ref(false)
const avatarLoading = ref(false)

const editForm = reactive<{ nickname: string; phone: string; student_no: string; avatar: string }>({ nickname: '', phone: '', student_no: '', avatar: '' })

async function loadData() {
  goodsLoading.value = true
  try {
    const [goodsRes, reviewRes] = await Promise.all([
      getMyGoods({ page_size: 100 }),
      userStore.user ? getReceivedReviews(userStore.user.id, { page_size: 50 }) : Promise.resolve({ list: [], total: 0, page: 1, page_size: 50 }),
    ])
    myGoods.value = goodsRes.list
    reviews.value = reviewRes.list
  } catch { /* 已提示 */ } finally {
    goodsLoading.value = false
  }
}

function openEdit() {
  const u = userStore.user
  editForm.nickname = u?.nickname || ''
  editForm.phone = u?.phone || ''
  editForm.student_no = u?.student_no || ''
  editForm.avatar = u?.avatar || ''
  editVisible.value = true
}

async function saveProfile() {
  saving.value = true
  try {
    await updateProfile({ ...editForm })
    await userStore.fetchMe()
    message.success('资料已更新')
    editVisible.value = false
  } catch { /* 已提示 */ } finally {
    saving.value = false
  }
}

async function uploadAvatar(options: { file: unknown; onSuccess?: (b: unknown) => void; onError?: (e: Error) => void }) {
  avatarLoading.value = true
  try {
    const url = await uploadImage(options.file as File)
    editForm.avatar = url
    options.onSuccess?.(url)
  } catch (err) {
    options.onError?.(err as Error)
  } finally {
    avatarLoading.value = false
  }
}

async function onOffShelf(id: number) {
  try {
    await offShelfGoods(id)
    message.success('已下架')
    await loadData()
  } catch { /* 已提示 */ }
}

const statusTag = (s: number) => ({ 1: { text: '在售', color: 'green' }, 2: { text: '已售', color: 'blue' }, 3: { text: '已下架', color: 'default' } })[s]

onMounted(async () => {
  if (!userStore.user) await userStore.fetchMe()
  await loadData()
})
</script>

<template>
  <div class="my">
    <!-- 资料卡 -->
    <a-card class="my__profile">
      <div class="my__profile-inner">
        <a-avatar :size="72" :src="userStore.user?.avatar || undefined">{{ (userStore.user?.nickname || '我').slice(0, 1) }}</a-avatar>
        <div class="my__info">
          <div class="my__name">{{ userStore.user?.nickname || userStore.user?.username }}</div>
          <div class="my__sub">
            <span>信用分 {{ userStore.user?.credit_score ?? 100 }}</span>
            <span v-if="userStore.user?.student_no">学号 {{ userStore.user.student_no }}</span>
            <a-tag v-if="userStore.isAdmin" color="purple">管理员</a-tag>
          </div>
        </div>
        <a-button @click="openEdit">编辑资料</a-button>
      </div>
    </a-card>

    <!-- 我的商品 -->
    <a-card class="my__section" title="我的商品">
      <a-spin :spinning="goodsLoading">
        <a-empty v-if="!myGoods.length" description="还没有发布商品">
          <a-button type="primary" @click="router.push('/publish')">去发布</a-button>
        </a-empty>
        <div v-else class="my__grid">
          <div v-for="item in myGoods" :key="item.id" class="my__cell">
            <GoodsCard :goods="item" @click="(id) => router.push(`/goods/${id}`)" />
            <div class="my__cell-foot">
              <a-tag :color="statusTag(item.status)?.color">{{ statusTag(item.status)?.text }}</a-tag>
              <a-button v-if="item.status === 1" size="small" danger @click="onOffShelf(item.id)">下架</a-button>
            </div>
          </div>
        </div>
      </a-spin>
    </a-card>

    <!-- 收到的评价 -->
    <a-card class="my__section" title="收到的评价">
      <a-empty v-if="!reviews.length" description="还没有收到评价" />
      <div v-for="r in reviews" :key="r.id" class="my__review">
        <a-avatar :src="r.reviewer_avatar || undefined">{{ r.reviewer_nickname.slice(0, 1) }}</a-avatar>
        <div class="my__review-body">
          <div class="my__review-head">
            <b>{{ r.reviewer_nickname }}</b>
            <span class="my__review-rating">{{ '★'.repeat(r.rating) }}</span>
          </div>
          <div class="my__review-content">{{ r.content || '对方没有留下评价内容' }}</div>
        </div>
      </div>
    </a-card>

    <!-- 编辑资料弹窗 -->
    <a-modal v-model:open="editVisible" title="编辑资料" :confirm-loading="saving" @ok="saveProfile">
      <a-form layout="vertical">
        <a-form-item label="头像">
          <a-upload :custom-request="uploadAvatar" :show-upload-list="false" accept="image/*">
            <div class="my__avatar-upload">
              <a-avatar :size="64" :src="editForm.avatar || undefined">
                <CameraOutlined v-if="!avatarLoading" />
              </a-avatar>
              <LoadingOutlined v-if="avatarLoading" />
              <span style="margin-left:10px;color:#98a2b3">点击更换头像</span>
            </div>
          </a-upload>
        </a-form-item>
        <a-form-item label="昵称"><a-input v-model:value="editForm.nickname" :maxlength="32" /></a-form-item>
        <a-form-item label="手机号"><a-input v-model:value="editForm.phone" :maxlength="20" /></a-form-item>
        <a-form-item label="学号"><a-input v-model:value="editForm.student_no" :maxlength="32" /></a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<style scoped>
.my { max-width: 1000px; margin: 0 auto; }
.my__profile { border-radius: 12px; margin-bottom: 20px; }
.my__profile-inner { display: flex; align-items: center; gap: 18px; }
.my__info { flex: 1; }
.my__name { font-size: 20px; font-weight: 700; }
.my__sub { display: flex; gap: 16px; margin-top: 6px; color: #98a2b3; font-size: 13px; }
.my__section { border-radius: 12px; margin-bottom: 20px; }
.my__grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 16px; }
.my__cell-foot { display: flex; justify-content: space-between; align-items: center; margin-top: 6px; }
.my__review { display: flex; gap: 12px; padding: 12px 0; border-bottom: 1px solid #f0f2f5; }
.my__review:last-child { border-bottom: none; }
.my__review-head { display: flex; gap: 10px; align-items: center; }
.my__review-rating { color: #f59e0b; }
.my__review-content { color: #4b5563; margin-top: 4px; }
.my__avatar-upload { display: flex; align-items: center; cursor: pointer; }
</style>
