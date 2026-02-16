<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { NCard, NForm, NFormItem, NInput, NButton, NSpace, NAvatar, NUpload, useMessage } from 'naive-ui'
import { authApi } from '../api/modules'
import { useUserStore } from '../store/user'

const router = useRouter()
const message = useMessage()
const userStore = useUserStore()

const formRef = ref(null)
const loading = ref(false)
const avatarLoading = ref(false)
const formValue = ref({
  username: '',
  phone: '',
  email: '',
  avatar: null
})

const rules = {
  username: { required: true, message: '请输入用户名', trigger: 'blur' },
  phone: { pattern: /^1[3-9]\d{9}$/, message: '手机号格式不正确', trigger: 'blur' },
  email: { type: 'email', message: '邮箱格式不正确', trigger: 'blur' }
}

const avatarUrl = ref('')

const fetchUserInfo = async () => {
  try {
    const res = await authApi.getUserInfo()
    if (res.code === 200) {
      formValue.value = {
        username: res.data.username,
        phone: res.data.phone || '',
        email: res.data.email || '',
        avatar: res.data.avatar
      }
      if (res.data.avatar) {
        avatarUrl.value = `http://127.0.0.1:8000${res.data.avatar}`
      }
    }
  } catch (error) {
    message.error('获取用户信息失败')
  }
}

const handleSubmit = async () => {
  try {
    await formRef.value?.validate()
    loading.value = true
    const res = await authApi.updateUserInfo(formValue.value)
    if (res.code === 200) {
      message.success('更新成功')
      userStore.updateUserInfo(res.data)
    } else {
      message.error(res.message || '更新失败')
    }
  } catch (error) {
    message.error('更新失败')
  } finally {
    loading.value = false
  }
}

const handleUpload = async ({ file, onFinish, onError }) => {
  const formData = new FormData()
  formData.append('file', file.file)
  avatarLoading.value = true
  
  try {
    const res = await authApi.uploadAvatar(formData)
    if (res.code === 200) {
      formValue.value.avatar = res.data.url
      avatarUrl.value = `http://127.0.0.1:8000${res.data.url}`
      message.success('头像上传成功')
      onFinish()
    } else {
      message.error(res.message || '上传失败')
      onError()
    }
  } catch (error) {
    console.error('Upload error:', error)
    message.error('上传失败')
    onError()
  } finally {
    avatarLoading.value = false
  }
}

onMounted(() => {
  fetchUserInfo()
})
</script>

<template>
  <div>
    <n-card title="编辑个人信息" style="max-width: 600px; margin: 0 auto;">
      <n-form ref="formRef" :model="formValue" :rules="rules" label-width="80">
        <n-form-item label="头像">
          <n-space align="center">
            <n-avatar round :size="64" :src="avatarUrl">
              {{ formValue.username?.charAt(0)?.toUpperCase() }}
            </n-avatar>
            <n-upload :show-file-list="false" :custom-request="handleUpload" accept="image/*">
              <n-button size="small" :loading="avatarLoading">更换头像</n-button>
            </n-upload>
          </n-space>
        </n-form-item>
        <n-form-item label="用户名" path="username">
          <n-input v-model:value="formValue.username" placeholder="请输入用户名" />
        </n-form-item>
        <n-form-item label="手机号" path="phone">
          <n-input v-model:value="formValue.phone" placeholder="请输入手机号" />
        </n-form-item>
        <n-form-item label="邮箱" path="email">
          <n-input v-model:value="formValue.email" placeholder="请输入邮箱" />
        </n-form-item>
        <n-space>
          <n-button type="primary" :loading="loading" @click="handleSubmit">保存</n-button>
          <n-button @click="router.push('/profile')">返回</n-button>
        </n-space>
      </n-form>
    </n-card>
  </div>
</template>
