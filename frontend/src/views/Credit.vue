<script setup>
import { ref, onMounted, h } from 'vue'
import { NCard, NDataTable, NTag, NDescriptions, NDescriptionsItem, useMessage } from 'naive-ui'
import { creditApi, authApi } from '../api/modules'
import { useUserStore } from '../store/user'

const message = useMessage()
const userStore = useUserStore()

const records = ref([])
const loading = ref(false)
const creditInfo = ref(null)

const typeMap = {
  evaluation_good: { text: '好评加分', type: 'success' },
  evaluation_bad: { text: '差评扣分', type: 'error' },
  violation: { text: '违规扣分', type: 'error' },
  admin_adjust: { text: '管理员调整', type: 'warning' },
  system: { text: '系统调整', type: 'info' }
}

const columns = [
  { title: '变更类型', key: 'change_type', render: (row) => h(NTag, { type: typeMap[row.change_type]?.type }, () => typeMap[row.change_type]?.text) },
  { title: '变更分值', key: 'change_score', render: (row) => h('span', { style: { color: row.change_score > 0 ? '#18a058' : '#d03050' } }, `${row.change_score > 0 ? '+' : ''}${row.change_score}`) },
  { title: '变更前', key: 'before_score' },
  { title: '变更后', key: 'after_score' },
  { title: '原因', key: 'reason', ellipsis: { tooltip: true } },
  { title: '时间', key: 'created_at', width: 160 }
]

const fetchData = async () => {
  loading.value = true
  try {
    const [recordsRes, userRes] = await Promise.all([
      creditApi.getRecords(),
      authApi.getUserInfo()
    ])
    if (recordsRes.code === 200) records.value = recordsRes.data
    if (userRes.code === 200) creditInfo.value = userRes.data
  } catch (error) {
    message.error('获取数据失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchData()
})
</script>

<template>
  <div>
    <n-card title="诚信值记录" style="margin-bottom: 16px;">
      <n-descriptions v-if="creditInfo" label-placement="left" :column="3">
        <n-descriptions-item label="当前诚信值">
          <n-tag :type="creditInfo.credit_score >= 80 ? 'success' : creditInfo.credit_score >= 60 ? 'warning' : 'error'" size="large">
            {{ creditInfo.credit_score }}
          </n-tag>
        </n-descriptions-item>
        <n-descriptions-item label="实名认证">
          <n-tag :type="creditInfo.is_verified ? 'success' : 'warning'">
            {{ creditInfo.is_verified ? '已认证' : '未认证' }}
          </n-tag>
        </n-descriptions-item>
      </n-descriptions>
    </n-card>
    
    <n-card title="变更记录">
      <n-data-table :columns="columns" :data="records" :loading="loading" />
    </n-card>
  </div>
</template>
