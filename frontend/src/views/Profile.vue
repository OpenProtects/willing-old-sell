<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { NCard, NDescriptions, NDescriptionsItem, NAvatar, NTag, NButton, NSpace, useMessage } from 'naive-ui'
import { useUserStore } from '../store/user'
import { authApi } from '../api/modules'

const router = useRouter()
const userStore = useUserStore()
const message = useMessage()

const userInfo = ref(null)

const fetchUserInfo = async () => {
  try {
    const res = await authApi.getUserInfo()
    if (res.code === 200) {
      userInfo.value = res.data
      userStore.updateUserInfo(res.data)
    }
  } catch (error) {
    message.error('获取用户信息失败')
  }
}

onMounted(() => {
  fetchUserInfo()
})
</script>

<template>
  <div>
    <n-card title="个人中心">
      <template #header-extra>
        <n-button type="primary" @click="router.push('/profile/edit')">编辑资料</n-button>
      </template>
      
      <n-descriptions label-placement="left" :column="1" bordered>
        <n-descriptions-item label="头像">
          <n-avatar round :size="48" :src="userInfo?.avatar">{{ userInfo?.username?.charAt(0)?.toUpperCase() }}</n-avatar>
        </n-descriptions-item>
        <n-descriptions-item label="用户名">{{ userInfo?.username }}</n-descriptions-item>
        <n-descriptions-item label="手机号">{{ userInfo?.phone || '未设置' }}</n-descriptions-item>
        <n-descriptions-item label="邮箱">{{ userInfo?.email || '未设置' }}</n-descriptions-item>
        <n-descriptions-item label="真实姓名">{{ userInfo?.real_name || '未认证' }}</n-descriptions-item>
        <n-descriptions-item label="学号/工号">{{ userInfo?.school_id || '未设置' }}</n-descriptions-item>
        <n-descriptions-item label="诚信值">
          <n-tag :type="userInfo?.credit_score >= 80 ? 'success' : userInfo?.credit_score >= 60 ? 'warning' : 'error'">
            {{ userInfo?.credit_score }}
          </n-tag>
        </n-descriptions-item>
        <n-descriptions-item label="实名认证">
          <n-tag :type="userInfo?.is_verified ? 'success' : 'warning'">
            {{ userInfo?.is_verified ? '已认证' : '未认证' }}
          </n-tag>
        </n-descriptions-item>
        <n-descriptions-item label="注册时间">{{ userInfo?.date_joined }}</n-descriptions-item>
        <n-descriptions-item label="最后登录">{{ userInfo?.last_login || '从未登录' }}</n-descriptions-item>
      </n-descriptions>
      
      <n-space style="margin-top: 24px;">
        <n-button @click="$router.push('/verify')">实名认证</n-button>
        <n-button @click="$router.push('/credit')">查看诚信记录</n-button>
        <n-button @click="$router.push('/report')">举报管理</n-button>
      </n-space>
    </n-card>
  </div>
</template>
