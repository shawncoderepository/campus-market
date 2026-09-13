<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import {
  Avatar as AAvatar,
  Button as AButton,
  Card as ACard,
  Descriptions as ADescriptions,
  DescriptionsItem as ADescriptionsItem,
  Empty as AEmpty,
  Form as AForm,
  FormItem as AFormItem,
  Input as AInput,
  InputPassword as AInputPassword,
  message,
  Modal as AModal,
  Spin as ASpin,
  TabPane as ATabPane,
  Tabs as ATabs,
  Tag as ATag,
  Upload as AUpload,
} from 'ant-design-vue'
import {
  CameraOutlined,
  ClockCircleOutlined,
  CommentOutlined,
  CreditCardOutlined,
  FlagOutlined,
  HeartOutlined,
  IdcardOutlined,
  LoadingOutlined,
  LockOutlined,
  MailOutlined,
  PhoneOutlined,
  SafetyCertificateOutlined,
  ShoppingOutlined,
  StarOutlined,
  TagsOutlined,
  TeamOutlined,
  UserOutlined,
} from '@ant-design/icons-vue'
import GoodsCard from '@/components/GoodsCard.vue'
import { getMyGoods, offShelfGoods, uploadImage } from '@/common/apis/goodsApi'
import { getReceivedReviews } from '@/common/apis/reviewApi'
import { changePassword, getMyStats, updateProfile, type UserStats } from '@/common/apis/userApi'
import { useUserStore } from '@/stores/user'
import type { GoodsItem, Review } from '@/common/types/business'

const router = useRouter()
const userStore = useUserStore()
const goodsLoading = ref(false)
const statsLoading = ref(true)
const myGoods = ref<GoodsItem[]>([])
const reviews = ref<Review[]>([])
const stats = ref<UserStats | null>(null)

// 编辑资料
const editVisible = ref(false)
const saving = ref(false)
const avatarLoading = ref(false)
const editForm = reactive({ nickname: '', phone: '', student_no: '', avatar: '' })

// 修改密码
const pwdVisible = ref(false)
const pwdSaving = ref(false)
const pwdForm = reactive({ old_password: '', new_password: '', confirm: '' })

const user = computed(() => userStore.user)
const isAdmin = computed(() => userStore.isAdmin)

// 信用分等级
const creditLevel = computed(() => {
  const s = user.value?.credit_score ?? 100
  if (s >= 90) return { text: '优秀', color: '#10b981' }
  if (s >= 70) return { text: '良好', color: '#6366f1' }
  if (s >= 50) return { text: '一般', color: '#f59e0b' }
  return { text: '较差', color: '#ef4444' }
})

const registerDate = computed(() => {
  const t = user.value?.created_at
  return t ? new Date(t).toLocaleDateString('zh-CN') : '—'
})

async function loadData() {
  goodsLoading.value = true
  statsLoading.value = true
  try {
    const [goodsRes, reviewRes, statsRes] = await Promise.all([
      getMyGoods({ page_size: 100 }),
      userStore.user ? getReceivedReviews(userStore.user.id, { page_size: 50 }) : Promise.resolve({ list: [], total: 0, page: 1, page_size: 50 }),
      getMyStats(),
    ])
    myGoods.value = goodsRes.list
    reviews.value = reviewRes.list
    stats.value = statsRes
  } catch { /* 已提示 */ } finally {
    goodsLoading.value = false
    statsLoading.value = false
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

function openPwd() {
  pwdForm.old_password = ''
  pwdForm.new_password = ''
  pwdForm.confirm = ''
  pwdVisible.value = true
}

async function savePwd() {
  if (!pwdForm.old_password || !pwdForm.new_password) return message.warning('请填写完整')
  if (pwdForm.new_password !== pwdForm.confirm) return message.warning('两次输入的新密码不一致')
  pwdSaving.value = true
  try {
    await changePassword({ old_password: pwdForm.old_password, new_password: pwdForm.new_password })
    message.success('密码修改成功')
    pwdVisible.value = false
  } catch { /* 已提示 */ } finally {
    pwdSaving.value = false
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
  <div class="my page-mid">
    <!-- ===== 资料卡 ===== -->
    <div class="my__profile">
      <div class="my__profile-banner"></div>
      <div class="my__profile-inner">
        <div class="my__avatar-wrap" @click="openEdit">
          <a-avatar :size="88" class="my__avatar" :src="user?.avatar || undefined">
            {{ (user?.nickname || '我').slice(0, 1) }}
          </a-avatar>
          <span class="my__avatar-edit"><CameraOutlined /></span>
        </div>
        <div class="my__info">
          <div class="my__name">
            {{ user?.nickname || user?.username }}
            <a-tag v-if="isAdmin" color="orange" class="my__role-tag">
              <SafetyCertificateOutlined /> 管理员
            </a-tag>
            <a-tag v-else color="blue" class="my__role-tag">
              <UserOutlined /> 学生
            </a-tag>
          </div>
          <div class="my__username">@{{ user?.username }}</div>
          <div class="my__sub">
            <span class="my__chip" :style="{ color: creditLevel.color }">
              <CreditCardOutlined /> 信用分 <b>{{ user?.credit_score ?? 100 }}</b> · {{ creditLevel.text }}
            </span>
            <span v-if="stats?.avg_rating != null" class="my__chip">
              <StarOutlined /> 评分 <b>{{ stats.avg_rating }}</b>
            </span>
            <span class="my__chip"><ClockCircleOutlined /> {{ registerDate }} 加入</span>
          </div>
        </div>
        <div class="my__actions">
          <a-button type="primary" ghost @click="openEdit">
            <template #icon><IdcardOutlined /></template>编辑资料
          </a-button>
          <a-button @click="openPwd">
            <template #icon><LockOutlined /></template>修改密码
          </a-button>
        </div>
      </div>
    </div>

    <!-- ===== 统计卡片 ===== -->
    <a-spin :spinning="statsLoading">
      <div class="my__stats">
        <div class="stat" @click="router.push('/my')">
          <div class="stat__icon" style="background:#fff7ed;color:#f59e0b"><TagsOutlined /></div>
          <div class="stat__body">
            <div class="stat__value">{{ stats?.goods_on_sale ?? 0 }}</div>
            <div class="stat__label">在卖商品</div>
          </div>
        </div>
        <div class="stat">
          <div class="stat__icon" style="background:#eff6ff;color:#6366f1"><ShoppingOutlined /></div>
          <div class="stat__body">
            <div class="stat__value">{{ stats?.order_buy_total ?? 0 }}</div>
            <div class="stat__label">我买到的</div>
          </div>
        </div>
        <div class="stat">
          <div class="stat__icon" style="background:#ecfdf5;color:#10b981"><ShoppingOutlined /></div>
          <div class="stat__body">
            <div class="stat__value">{{ stats?.order_sell_total ?? 0 }}</div>
            <div class="stat__label">我卖出的</div>
          </div>
        </div>
        <div class="stat" @click="router.push('/favorites')">
          <div class="stat__icon" style="background:#fdf2f8;color:#ec4899"><HeartOutlined /></div>
          <div class="stat__body">
            <div class="stat__value">{{ stats?.favorite_total ?? 0 }}</div>
            <div class="stat__label">我的收藏</div>
          </div>
        </div>
        <div class="stat">
          <div class="stat__icon" style="background:#f0f9ff;color:#06b6d4"><CommentOutlined /></div>
          <div class="stat__body">
            <div class="stat__value">{{ stats?.review_received_total ?? 0 }}</div>
            <div class="stat__label">收到评价</div>
          </div>
        </div>
        <!-- 管理员额外统计 -->
        <template v-if="isAdmin">
          <div class="stat" @click="router.push('/admin/user')">
            <div class="stat__icon" style="background:#f5f3ff;color:#8b5cf6"><TeamOutlined /></div>
            <div class="stat__body">
              <div class="stat__value">{{ stats?.user_total ?? 0 }}</div>
              <div class="stat__label">平台用户</div>
            </div>
          </div>
          <div class="stat" @click="router.push('/admin/report')">
            <div class="stat__icon" style="background:#fef2f2;color:#ef4444"><FlagOutlined /></div>
            <div class="stat__body">
              <div class="stat__value">{{ stats?.report_pending ?? 0 }}</div>
              <div class="stat__label">待处理举报</div>
            </div>
          </div>
        </template>
      </div>
    </a-spin>

    <!-- ===== 标签页 ===== -->
    <a-card class="my__section">
      <a-tabs default-active-key="info" class="my__tabs">
        <!-- 个人信息 -->
        <a-tab-pane key="info" tab="个人信息">
          <a-descriptions :column="{ xs: 1, sm: 2 }" bordered class="my__desc">
            <a-descriptions-item label="昵称">{{ user?.nickname || '—' }}</a-descriptions-item>
            <a-descriptions-item label="用户名">@{{ user?.username }}</a-descriptions-item>
            <a-descriptions-item label="角色">
              <a-tag v-if="isAdmin" color="orange">管理员</a-tag>
              <a-tag v-else color="blue">学生</a-tag>
            </a-descriptions-item>
            <a-descriptions-item label="账号状态">
              <a-tag :color="user?.status === 1 ? 'green' : 'red'">{{ user?.status === 1 ? '正常' : '已禁用' }}</a-tag>
            </a-descriptions-item>
            <a-descriptions-item label="手机号">
              <span v-if="user?.phone"><PhoneOutlined /> {{ user.phone }}</span><span v-else>—</span>
            </a-descriptions-item>
            <a-descriptions-item label="学号">
              <span v-if="user?.student_no"><MailOutlined /> {{ user.student_no }}</span><span v-else>—</span>
            </a-descriptions-item>
            <a-descriptions-item label="信用分">
              <span :style="{ color: creditLevel.color, fontWeight: 700 }">{{ user?.credit_score ?? 100 }}（{{ creditLevel.text }}）</span>
            </a-descriptions-item>
            <a-descriptions-item label="注册时间">{{ registerDate }}</a-descriptions-item>
          </a-descriptions>
          <div class="my__info-actions">
            <a-button type="primary" @click="openEdit"><template #icon><IdcardOutlined /></template>编辑资料</a-button>
            <a-button @click="openPwd"><template #icon><LockOutlined /></template>修改密码</a-button>
            <a-button v-if="isAdmin" type="dashed" @click="router.push('/admin')">进入管理后台</a-button>
          </div>
        </a-tab-pane>

        <!-- 我的商品 -->
        <a-tab-pane key="goods" :tab="`我的商品 (${myGoods.length})`">
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
        </a-tab-pane>

        <!-- 收到的评价 -->
        <a-tab-pane key="reviews" :tab="`收到的评价 (${reviews.length})`">
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
        </a-tab-pane>
      </a-tabs>
    </a-card>

    <!-- ===== 编辑资料弹窗 ===== -->
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

    <!-- ===== 修改密码弹窗 ===== -->
    <a-modal v-model:open="pwdVisible" title="修改密码" :confirm-loading="pwdSaving" @ok="savePwd">
      <a-form layout="vertical">
        <a-form-item label="原密码" required>
          <a-input-password v-model:value="pwdForm.old_password" placeholder="请输入原密码" />
        </a-form-item>
        <a-form-item label="新密码" required>
          <a-input-password v-model:value="pwdForm.new_password" placeholder="至少 6 位" />
        </a-form-item>
        <a-form-item label="确认新密码" required>
          <a-input-password v-model:value="pwdForm.confirm" placeholder="再次输入新密码" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<style scoped>
.my { width: 100%; }

/* ===== 资料卡 ===== */
.my__profile { position: relative; background: #fff; border-radius: 16px; overflow: hidden; margin-bottom: 20px; box-shadow: var(--shadow-card); }
.my__profile-banner { height: 120px; background: linear-gradient(120deg, #ff8a3d 0%, #ff6a00 55%, #ff5e3a 100%); }
.my__profile-inner { display: flex; align-items: center; gap: 20px; padding: 0 26px 24px; margin-top: -44px; }
.my__avatar-wrap { position: relative; flex-shrink: 0; cursor: pointer; }
.my__avatar { border: 4px solid #fff; box-shadow: var(--shadow-card); }
.my__avatar-edit { position: absolute; right: 0; bottom: 2px; width: 26px; height: 26px; border-radius: 50%; background: #ff6a00; color: #fff; display: grid; place-items: center; font-size: 13px; border: 2px solid #fff; }
.my__info { flex: 1; padding-top: 50px; min-width: 0; }
.my__name { font-size: 22px; font-weight: 800; color: #2b2622; display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.my__role-tag { display: inline-flex; align-items: center; gap: 3px; }
.my__username { color: #b0a79d; font-size: 13px; margin-top: 2px; }
.my__sub { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 10px; }
.my__chip { display: inline-flex; align-items: center; gap: 5px; background: #faf6f1; border-radius: 999px; padding: 4px 12px; font-size: 12px; color: #8a8078; }
.my__chip b { font-size: 14px; }
.my__actions { display: flex; gap: 10px; padding-top: 50px; flex-shrink: 0; }

/* ===== 统计卡片 ===== */
.my__stats { display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 14px; margin-bottom: 20px; }
.stat { display: flex; align-items: center; gap: 12px; background: #fff; border-radius: 14px; padding: 16px; box-shadow: var(--shadow-card); cursor: pointer; transition: transform .15s; }
.stat:hover { transform: translateY(-3px); }
.stat__icon { width: 44px; height: 44px; border-radius: 12px; display: grid; place-items: center; font-size: 20px; flex-shrink: 0; }
.stat__value { font-size: 22px; font-weight: 800; color: #2b2622; line-height: 1.1; }
.stat__label { font-size: 12px; color: #a39a90; margin-top: 2px; }

/* ===== 标签页 ===== */
.my__section { border-radius: 16px; box-shadow: var(--shadow-card); }
.my__tabs :deep(.ant-tabs-nav) { margin-bottom: 16px; }
.my__desc :deep(.ant-descriptions-item-label) { color: #8a8078; }
.my__info-actions { display: flex; gap: 10px; margin-top: 20px; flex-wrap: wrap; }

/* ===== 商品 / 评价 ===== */
.my__grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 16px; }
.my__cell-foot { display: flex; justify-content: space-between; align-items: center; margin-top: 8px; }
.my__review { display: flex; gap: 12px; padding: 14px 0; border-bottom: 1px solid #f5f0ea; }
.my__review:last-child { border-bottom: none; }
.my__review-head { display: flex; gap: 10px; align-items: center; }
.my__review-rating { color: #ffa940; }
.my__review-content { color: #5c554d; margin-top: 4px; }
.my__avatar-upload { display: flex; align-items: center; cursor: pointer; }

@media (max-width: 640px) {
  .my__profile-inner { flex-wrap: wrap; }
  .my__info, .my__actions { padding-top: 0; }
}
</style>
