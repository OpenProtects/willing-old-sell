<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { NCard, NTabs, NTabPane, NDataTable, NTag, NButton, NSpace, NModal, NInput, NInputNumber, NSelect, useMessage, NEmpty, NPagination } from 'naive-ui'
import { authApi, goodsApi, reportApi, creditApi } from '../api/modules'
import { useUserStore } from '../store/user'

const router = useRouter()
const message = useMessage()
const userStore = useUserStore()

const loading = ref(false)
const activeTab = ref('users')

const users = ref([])
const goods = ref([])
const reports = ref([])

const pagination = ref({ page: 1, pageSize: 10, count: 0 })

const showCreditModal = ref(false)
const selectedUser = ref(null)
const creditAdjust = ref({ change_score: 0, reason: '' })

const showHandleModal = ref(false)
const selectedReport = ref(null)
const handleResult = ref({ status: 'resolved', result: '', credit_deduction: 0 })

const userColumns = [
  { title: 'ID', key: 'id', width: 60 },
  { title: '用户名', key: 'username' },
  { title: '手机号', key: 'phone' },
  { title: '诚信值', key: 'credit_score', render: (row) => h(NTag, { type: row.credit_score >= 80 ? 'success' : row.credit_score >= 60 ? 'warning' : 'error' }, () => row.credit_score) },
  { title: '实名认证', key: 'is_verified', render: (row) => h(NTag, { type: row.is_verified ? 'success' : 'warning' }, () => row.is_verified ? '已认证' : '未认证') },
  { title: '注册时间', key: 'date_joined', width: 160 },
  { title: '操作', key: 'actions', render: (row) => h(NButton, { size: 'small', onClick: () => openCreditModal(row) }, () => '调整诚信值') }
]

const goodsColumns = [
  { title: 'ID', key: 'id', width: 60 },
  { title: '名称', key: 'name' },
  { title: '价格', key: 'price', render: (row) => `¥${row.price}` },
  { title: '状态', key: 'status', render: (row) => {
    const map = { on_sale: 'success', off_sale: 'warning', sold: 'default' }
    return h(NTag, { type: map[row.status] }, () => row.status_display)
  }},
  { title: '卖家', key: 'seller_name' },
  { title: '发布时间', key: 'created_at', width: 160 }
]

const reportColumns = [
  { title: 'ID', key: 'id', width: 60 },
  { title: '举报人', key: 'reporter_name' },
  { title: '被举报人', key: 'reported_user_name' },
  { title: '类型', key: 'report_type_display' },
  { title: '状态', key: 'status', render: (row) => {
    const map = { pending: 'warning', processing: 'info', resolved: 'success', rejected: 'default' }
    return h(NTag, { type: map[row.status] }, () => row.status_display)
  }},
  { title: '提交时间', key: 'created_at', width: 160 },
  { title: '操作', key: 'actions', render: (row) => row.status === 'pending' ? h(NButton, { size: 'small', type: 'primary', onClick: () => openHandleModal(row) }, () => '处理') : null }
]

const isMobile = computed(() => window.innerWidth < 768)

const fetchUsers = async () => {
  loading.value = true
  try {
    const res = await authApi.getUsers({ page: pagination.value.page })
    if (res.code === 200) {
      users.value = res.data
      pagination.value.count = res.count || res.data.length
    }
  } catch (error) {
    message.error('获取用户列表失败')
  } finally {
    loading.value = false
  }
}

const fetchGoods = async () => {
  loading.value = true
  try {
    const res = await goodsApi.getGoodsList({ page: pagination.value.page, status: 'all' })
    if (res.code === 200) {
      goods.value = res.data
      pagination.value.count = res.count || res.data.length
    }
  } catch (error) {
    message.error('获取物品列表失败')
  } finally {
    loading.value = false
  }
}

const fetchReports = async () => {
  loading.value = true
  try {
    const res = await reportApi.list({ page: pagination.value.page })
    if (res.code === 200) {
      reports.value = res.data
      pagination.value.count = res.count || res.data.length
    }
  } catch (error) {
    message.error('获取举报列表失败')
  } finally {
    loading.value = false
  }
}

const openCreditModal = (user) => {
  selectedUser.value = user
  creditAdjust.value = { change_score: 0, reason: '' }
  showCreditModal.value = true
}

const handleCreditAdjust = async () => {
  try {
    const res = await creditApi.adjust({
      user_id: selectedUser.value.id,
      change_score: creditAdjust.value.change_score,
      reason: creditAdjust.value.reason
    })
    if (res.code === 200) {
      message.success('调整成功')
      showCreditModal.value = false
      fetchUsers()
    } else {
      message.error(res.message || '调整失败')
    }
  } catch (error) {
    message.error('调整失败')
  }
}

const openHandleModal = (report) => {
  selectedReport.value = report
  handleResult.value = { status: 'resolved', result: '', credit_deduction: 0 }
  showHandleModal.value = true
}

const handleReport = async () => {
  try {
    const res = await reportApi.handleReport(selectedReport.value.id, handleResult.value)
    if (res.code === 200) {
      message.success('处理成功')
      showHandleModal.value = false
      fetchReports()
    } else {
      message.error(res.message || '处理失败')
    }
  } catch (error) {
    message.error('处理失败')
  }
}

const handleTabChange = (tab) => {
  pagination.value.page = 1
  if (tab === 'users') fetchUsers()
  else if (tab === 'goods') fetchGoods()
  else if (tab === 'reports') fetchReports()
}

const handlePageChange = (page) => {
  pagination.value.page = page
  handleTabChange(activeTab.value)
}

onMounted(() => {
  if (!userStore.isAdmin) {
    message.warning('无权访问管理员后台')
    router.push('/')
    return
  }
  fetchUsers()
})
</script>

<template>
  <div>
    <n-card title="管理员后台">
      <n-tabs v-model:value="activeTab" @update:value="handleTabChange">
        <n-tab-pane name="users" tab="用户管理">
          <n-data-table :columns="userColumns" :data="users" :loading="loading" />
        </n-tab-pane>
        <n-tab-pane name="goods" tab="物品管理">
          <n-data-table :columns="goodsColumns" :data="goods" :loading="loading" />
        </n-tab-pane>
        <n-tab-pane name="reports" tab="举报处理">
          <n-data-table :columns="reportColumns" :data="reports" :loading="loading" />
        </n-tab-pane>
      </n-tabs>
      
      <div style="margin-top: 16px; display: flex; justify-content: center;">
        <n-pagination
          v-model:page="pagination.page"
          :page-count="Math.ceil(pagination.count / pagination.pageSize)"
          @update:page="handlePageChange"
        />
      </div>
    </n-card>

    <n-modal v-model:show="showCreditModal" preset="card" title="调整诚信值" style="width: 400px;">
      <n-space vertical>
        <div>用户: {{ selectedUser?.username }}</div>
        <div>当前诚信值: {{ selectedUser?.credit_score }}</div>
        <n-input-number v-model:value="creditAdjust.change_score" :min="-100" :max="100" placeholder="调整分值（正数加分，负数扣分）" style="width: 100%;" />
        <n-input v-model:value="creditAdjust.reason" placeholder="调整原因" />
      </n-space>
      <template #footer>
        <n-space justify="end">
          <n-button @click="showCreditModal = false">取消</n-button>
          <n-button type="primary" @click="handleCreditAdjust">确认</n-button>
        </n-space>
      </template>
    </n-modal>

    <n-modal v-model:show="showHandleModal" preset="card" title="处理举报" style="width: 500px;">
      <n-space vertical>
        <div>举报人: {{ selectedReport?.reporter_name }}</div>
        <div>被举报人: {{ selectedReport?.reported_user_name }}</div>
        <div>类型: {{ selectedReport?.report_type_display }}</div>
        <div>描述: {{ selectedReport?.description }}</div>
        <n-select v-model:value="handleResult.status" :options="[
          { label: '举报成立', value: 'resolved' },
          { label: '举报驳回', value: 'rejected' }
        ]" placeholder="处理结果" />
        <n-input-number v-if="handleResult.status === 'resolved'" v-model:value="handleResult.credit_deduction" :min="0" :max="50" placeholder="扣除诚信值" style="width: 100%;" />
        <n-input v-model:value="handleResult.result" type="textarea" placeholder="处理说明" :rows="3" />
      </n-space>
      <template #footer>
        <n-space justify="end">
          <n-button @click="showHandleModal = false">取消</n-button>
          <n-button type="primary" @click="handleReport">确认处理</n-button>
        </n-space>
      </template>
    </n-modal>
  </div>
</template>
