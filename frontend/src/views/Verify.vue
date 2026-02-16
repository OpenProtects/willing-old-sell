<script setup>
import { ref } from 'vue'
import { NCard, NForm, NFormItem, NInput, NButton, NSpace, NAlert, useMessage } from 'naive-ui'
import { authApi } from '../api/modules'
import { useUserStore } from '../store/user'

const message = useMessage()
const userStore = useUserStore()

const formRef = ref(null)
const loading = ref(false)
const formValue = ref({
  real_name: '',
  id_card: '',
  school_id: ''
})

const rules = {
  real_name: { required: true, message: '请输入真实姓名', trigger: 'blur' },
  id_card: [
    { required: true, message: '请输入身份证号', trigger: 'blur' },
    { pattern: /^\d{17}[\dXx]$/, message: '身份证号格式不正确', trigger: 'blur' }
  ]
}

const handleSubmit = async () => {
  try {
    await formRef.value?.validate()
    loading.value = true
    const res = await authApi.verifyRealname(formValue.value)
    if (res.code === 200) {
      message.success('实名认证成功')
      userStore.updateUserInfo({ is_verified: true, real_name: formValue.value.real_name })
    } else {
      message.error(res.message || '认证失败')
    }
  } catch (error) {
    message.error('认证失败')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div>
    <n-card title="实名认证" style="max-width: 600px; margin: 0 auto;">
      <n-alert v-if="userStore.isVerified" type="success" style="margin-bottom: 16px;">
        您已完成实名认证
      </n-alert>
      
      <n-alert v-else type="info" style="margin-bottom: 16px;">
        请填写真实信息完成实名认证，认证后可进行交易
      </n-alert>
      
      <n-form ref="formRef" :model="formValue" :rules="rules" label-width="100" :disabled="userStore.isVerified">
        <n-form-item label="真实姓名" path="real_name">
          <n-input v-model:value="formValue.real_name" placeholder="请输入真实姓名" />
        </n-form-item>
        <n-form-item label="身份证号" path="id_card">
          <n-input v-model:value="formValue.id_card" placeholder="请输入身份证号" maxlength="18" />
        </n-form-item>
        <n-form-item label="学号/工号" path="school_id">
          <n-input v-model:value="formValue.school_id" placeholder="请输入学号或工号（可选）" />
        </n-form-item>
        
        <n-space v-if="!userStore.isVerified">
          <n-button type="primary" :loading="loading" @click="handleSubmit">提交认证</n-button>
        </n-space>
      </n-form>
    </n-card>
  </div>
</template>
