<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { NCard, NForm, NFormItem, NInput, NButton, NSpace, useMessage } from 'naive-ui'
import { useUserStore } from '../store/user'

const router = useRouter()
const message = useMessage()
const userStore = useUserStore()

const formRef = ref(null)
const loading = ref(false)
const formValue = ref({
  username: '',
  password: '',
  password_confirm: '',
  phone: '',
  email: ''
})

const rules = {
  username: { required: true, message: '请输入用户名', trigger: 'blur' },
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少6位', trigger: 'blur' }
  ],
  password_confirm: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { validator: (rule, value) => value === formValue.value.password, message: '两次密码不一致', trigger: 'blur' }
  ],
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '手机号格式不正确', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '邮箱格式不正确', trigger: 'blur' }
  ]
}

const handleRegister = async () => {
  try {
    await formRef.value?.validate()
    loading.value = true
    const res = await userStore.register(formValue.value)
    if (res.code === 200) {
      message.success('注册成功')
      router.push('/')
    } else {
      message.error(res.message || '注册失败')
    }
  } catch (error) {
    message.error(error.message || '注册失败')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div style="min-height: 100vh; display: flex; align-items: center; justify-content: center; background: #f5f5f5;">
    <n-card title="用户注册" style="width: 400px;">
      <n-form ref="formRef" :model="formValue" :rules="rules">
        <n-form-item label="用户名" path="username">
          <n-input v-model:value="formValue.username" placeholder="请输入用户名" />
        </n-form-item>
        <n-form-item label="密码" path="password">
          <n-input v-model:value="formValue.password" type="password" placeholder="请输入密码（至少6位）" />
        </n-form-item>
        <n-form-item label="确认密码" path="password_confirm">
          <n-input v-model:value="formValue.password_confirm" type="password" placeholder="请再次输入密码" />
        </n-form-item>
        <n-form-item label="手机号" path="phone">
          <n-input v-model:value="formValue.phone" placeholder="请输入手机号" />
        </n-form-item>
        <n-form-item label="邮箱" path="email">
          <n-input v-model:value="formValue.email" placeholder="请输入邮箱" />
        </n-form-item>
        <n-space vertical style="width: 100%;">
          <n-button type="primary" block :loading="loading" @click="handleRegister">注册</n-button>
          <n-button block @click="router.push('/login')">已有账号？去登录</n-button>
        </n-space>
      </n-form>
    </n-card>
  </div>
</template>
