<script setup>
import { ref, onMounted, h } from 'vue'
import { useRouter } from 'vue-router'
import { NCard, NTabs, NTabPane, NDataTable, NTag, NButton, NSpace, NModal, NInput, useMessage } from 'naive-ui'
import { orderApi } from '../api/modules'
import { useUserStore } from '../store/user'

const router = useRouter()
const message = useMessage()
const userStore = useUserStore()

const orders = ref([])
const loading = ref(false)
const activeTab = ref('all')
const showEvalModal = ref(false)
const currentOrder = ref(null)
const evalContent = ref('')
const evalRating = ref('good')

const statusMap = {
  pending: { text: '待支付', type: 'warning' },
  paid: { text: '已支付', type: 'info' },
  completed: { text: '已完成', type: 'success' },
  cancelled: { text: '已取消', type: 'default' }
}

const columns = [
  { title: '订单号', key: 'order_no', width: 180 },
  { title: '物品', key: 'goods_name' },
  { title: '金额', key: 'amount', render: (row) => `¥${row.amount}` },
  { title: '状态', key: 'status', render: (row) => h(NTag, { type: statusMap[row.status]?.type }, () => statusMap[row.status]?.text) },
  { title: '对方', key: 'other', render: (row) => row.buyer_name === userStore.userInfo?.username ? row.seller_name : row.buyer_name },
  { title: '创建时间', key: 'created_at', width: 160 },
  { title: '操作', key: 'actions', width: 200, render: (row) => {
    const isBuyer = row.buyer_name === userStore.userInfo?.username
    const buttons = [
      h(NButton, { size: 'small', onClick: () => router.push(`/goods/${row.goods}`) }, () => '查看物品')
    ]
    if (row.status === 'pending' && isBuyer) {
      buttons.push(h(NButton, { size: 'small', type: 'primary', onClick: () => handlePay(row) }, () => '支付'))
    }
    if (row.status === 'paid' && isBuyer) {
      buttons.push(h(NButton, { size: 'small', type: 'success', onClick: () => handleConfirm(row) }, () => '确认收货'))
    }
    if (row.status === 'completed' && isBuyer && !row.evaluation) {
      buttons.push(h(NButton, { size: 'small', type: 'info', onClick: () => openEvalModal(row) }, () => '评价'))
    }
    if (['pending', 'paid'].includes(row.status)) {
      buttons.push(h(NButton, { size: 'small', type: 'error', onClick: () => handleCancel(row) }, () => '取消'))
    }
    return h(NSpace, null, () => buttons)
  }}
]

const fetchOrders = async () => {
  loading.value = true
  try {
    const params = activeTab.value === 'all' ? {} : { status: activeTab.value }
    const res = await orderApi.getOrders(params)
    if (res.code === 200) orders.value = res.data
  } catch (error) {
    message.error('获取订单失败')
  } finally {
    loading.value = false
  }
}

const handlePay = async (order) => {
  try {
    const res = await orderApi.payOrder(order.id)
    if (res.code === 200) {
      message.success('支付成功')
      fetchOrders()
    } else {
      message.error(res.message || '支付失败')
    }
  } catch (error) {
    message.error('支付失败')
  }
}

const handleConfirm = async (order) => {
  try {
    const res = await orderApi.confirmOrder(order.id)
    if (res.code === 200) {
      message.success('确认收货成功')
      fetchOrders()
    } else {
      message.error(res.message || '确认失败')
    }
  } catch (error) {
    message.error('确认失败')
  }
}

const handleCancel = async (order) => {
  try {
    const res = await orderApi.cancelOrder(order.id)
    if (res.code === 200) {
      message.success('订单已取消')
      fetchOrders()
    }
  } catch (error) {
    message.error('取消失败')
  }
}

const openEvalModal = (order) => {
  currentOrder.value = order
  evalRating.value = 'good'
  evalContent.value = ''
  showEvalModal.value = true
}

const handleSubmitEval = async () => {
  try {
    const res = await orderApi.createEvaluation({
      order: currentOrder.value.id,
      rating: evalRating.value,
      content: evalContent.value
    })
    if (res.code === 200) {
      message.success('评价成功')
      showEvalModal.value = false
      fetchOrders()
    } else {
      message.error(res.message || '评价失败')
    }
  } catch (error) {
    message.error('评价失败')
  }
}

onMounted(() => {
  fetchOrders()
})
</script>

<template>
  <div>
    <n-card title="我的订单">
      <n-tabs v-model:value="activeTab" @update:value="fetchOrders">
        <n-tab-pane name="all" tab="全部" />
        <n-tab-pane name="pending" tab="待支付" />
        <n-tab-pane name="paid" tab="已支付" />
        <n-tab-pane name="completed" tab="已完成" />
      </n-tabs>
      
      <n-data-table :columns="columns" :data="orders" :loading="loading" style="margin-top: 16px;" />
    </n-card>

    <n-modal v-model:show="showEvalModal" preset="card" title="评价订单" style="width: 400px;">
      <n-space vertical>
        <div>
          <span>评价类型：</span>
          <n-button-group>
            <n-button :type="evalRating === 'good' ? 'primary' : 'default'" @click="evalRating = 'good'">好评</n-button>
            <n-button :type="evalRating === 'neutral' ? 'primary' : 'default'" @click="evalRating = 'neutral'">中评</n-button>
            <n-button :type="evalRating === 'bad' ? 'primary' : 'default'" @click="evalRating = 'bad'">差评</n-button>
          </n-button-group>
        </div>
        <n-input v-model:value="evalContent" type="textarea" placeholder="请输入评价内容（可选）" :rows="3" />
      </n-space>
      <template #footer>
        <n-space justify="end">
          <n-button @click="showEvalModal = false">取消</n-button>
          <n-button type="primary" @click="handleSubmitEval">提交评价</n-button>
        </n-space>
      </template>
    </n-modal>
  </div>
</template>
