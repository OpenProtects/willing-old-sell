<script setup>
import { ref, onMounted, h } from 'vue'
import { NCard, NDataTable, NTag, NButton, NSpace, NModal, NForm, NFormItem, NInput, NSelect, useMessage } from 'naive-ui'
import { reportApi } from '../api/modules'
import { useUserStore } from '../store/user'

const message = useMessage()
const userStore = useUserStore()

const reports = ref([])
const loading = ref(false)
const showModal = ref(false)
const formRef = ref(null)
const formValue = ref({
  reported_user: null,
  report_type: 'other',
  description: '',
  evidence: []
})

const rules = {
  reported_user: { required: true, type: 'number', message: '请输入被举报用户ID', trigger: 'blur' },
  report_type: { required: true, message: '请选择举报类型', trigger: 'change' },
  description: { required: true, message: '请输入举报描述', trigger: 'blur' }
}

const typeOptions = [
  { label: '虚假物品信息', value: 'fake_info' },
  { label: '恶意聊天', value: 'malicious_chat' },
  { label: '交易欺诈', value: 'fraud' },
  { label: '其他', value: 'other' }
]

const columns = [
  { title: '被举报人', key: 'reported_user_name' },
  { title: '类型', key: 'report_type_display' },
  { title: '描述', key: 'description', ellipsis: { tooltip: true } },
  { title: '状态', key: 'status', render: (row) => {
    const map = { pending: 'warning', processing: 'info', resolved: 'success', rejected: 'default' }
    return h(NTag, { type: map[row.status] }, () => row.status_display)
  }},
  { title: '结果', key: 'result', ellipsis: { tooltip: true } },
  { title: '提交时间', key: 'created_at' }
]

const fetchReports = async () => {
  loading.value = true
  try {
    const res = await reportApi.getMyReports()
    if (res.code === 200) reports.value = res.data
  } catch (error) {
    message.error('获取举报记录失败')
  } finally {
    loading.value = false
  }
}

const handleSubmit = async () => {
  try {
    await formRef.value?.validate()
    const res = await reportApi.createReport(formValue.value)
    if (res.code === 200) {
      message.success('举报提交成功')
      showModal.value = false
      formValue.value = { reported_user: null, report_type: 'other', description: '', evidence: [] }
      fetchReports()
    } else {
      message.error(res.message || '提交失败')
    }
  } catch (error) {
    message.error('提交失败')
  }
}

onMounted(() => {
  fetchReports()
})
</script>

<template>
  <div>
    <n-card title="举报管理">
      <template #header-extra>
        <n-button type="primary" @click="showModal = true">发起举报</n-button>
      </template>
      
      <n-data-table :columns="columns" :data="reports" :loading="loading" />
    </n-card>

    <n-modal v-model:show="showModal" preset="card" title="发起举报" style="width: 500px;">
      <n-form ref="formRef" :model="formValue" :rules="rules" label-width="100">
        <n-form-item label="被举报用户ID" path="reported_user">
          <n-input v-model:value="formValue.reported_user" placeholder="请输入被举报用户的ID" />
        </n-form-item>
        <n-form-item label="举报类型" path="report_type">
          <n-select v-model:value="formValue.report_type" :options="typeOptions" />
        </n-form-item>
        <n-form-item label="举报描述" path="description">
          <n-input v-model:value="formValue.description" type="textarea" placeholder="请详细描述举报原因" :rows="4" />
        </n-form-item>
      </n-form>
      <template #footer>
        <n-space justify="end">
          <n-button @click="showModal = false">取消</n-button>
          <n-button type="primary" @click="handleSubmit">提交</n-button>
        </n-space>
      </template>
    </n-modal>
  </div>
</template>
