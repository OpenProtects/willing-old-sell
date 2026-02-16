<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { NCard, NForm, NFormItem, NInput, NButton, NSpace, useMessage } from 'naive-ui'
import { useUserStore } from '../store/user'

const router = useRouter()
const route = useRoute()
const message = useMessage()
const userStore = useUserStore()

const formRef = ref(null)
const loading = ref(false)
const formValue = ref({
  username: '',
  password: ''
})

const rules = {
  username: { required: true, message: '请输入用户名', trigger: 'blur' },
  password: { required: true, message: '请输入密码', trigger: 'blur' }
}

const handleLogin = async () => {
  try {
    await formRef.value?.validate()
    loading.value = true
    const res = await userStore.login(formValue.value)
    if (res.code === 200) {
      message.success('登录成功')
      const redirect = route.query.redirect || '/'
      router.push(redirect)
    } else {
      message.error(res.message || '登录失败')
    }
  } catch (error) {
    message.error(error.message || '登录失败')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div style="min-height: 100vh; display: flex; align-items: center; justify-content: center; background: #f5f5f5;">
    <n-card title="用户登录" style="width: 400px;">
      <n-form ref="formRef" :model="formValue" :rules="rules">
        <n-form-item label="用户名" path="username">
          <n-input v-model:value="formValue.username" placeholder="请输入用户名" />
        </n-form-item>
        <n-form-item label="密码" path="password">
          <n-input v-model:value="formValue.password" type="password" placeholder="请输入密码" @keyup.enter="handleLogin" />
        </n-form-item>
        <n-space vertical style="width: 100%;">
          <n-button type="primary" block :loading="loading" @click="handleLogin">登录</n-button>
          <n-button block @click="router.push('/register')">没有账号？去注册</n-button>
        </n-space>
      </n-form>
    </n-card>
  </div>
</template>
