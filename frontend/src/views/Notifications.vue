<script setup>
import { ref, onMounted } from 'vue'
import { NCard, NList, NListItem, NThing, NTag, NButton, NSpace, NEmpty, useMessage } from 'naive-ui'
import { notificationApi } from '../api/modules'

const message = useMessage()
const notifications = ref([])
const loading = ref(false)

const typeMap = {
  match: { text: '心愿匹配', type: 'success' },
  order: { text: '订单通知', type: 'info' },
  evaluation: { text: '评价通知', type: 'warning' },
  report: { text: '举报处理', type: 'error' },
  system: { text: '系统通知', type: 'default' }
}

const fetchNotifications = async () => {
  loading.value = true
  try {
    const res = await notificationApi.getNotifications()
    if (res.code === 200) notifications.value = res.data
  } catch (error) {
    message.error('获取通知失败')
  } finally {
    loading.value = false
  }
}

const markRead = async (id) => {
  try {
    await notificationApi.markRead(id)
    const item = notifications.value.find(n => n.id === id)
    if (item) item.is_read = true
  } catch (error) {
    message.error('操作失败')
  }
}

const markAllRead = async () => {
  try {
    await notificationApi.markAllRead()
    notifications.value.forEach(n => n.is_read = true)
    message.success('全部标记已读')
  } catch (error) {
    message.error('操作失败')
  }
}

onMounted(() => {
  fetchNotifications()
})
</script>

<template>
  <div>
    <n-card title="通知中心">
      <template #header-extra>
        <n-button @click="markAllRead">全部标记已读</n-button>
      </template>
      
      <n-empty v-if="notifications.length === 0" description="暂无通知" />
      <n-list>
        <n-list-item v-for="item in notifications" :key="item.id">
          <n-thing :title="item.title" :description="item.content">
            <template #header-extra>
              <n-space align="center">
                <n-tag :type="typeMap[item.notification_type]?.type">{{ typeMap[item.notification_type]?.text }}</n-tag>
                <n-tag v-if="!item.is_read" type="error" size="small">未读</n-tag>
              </n-space>
            </template>
            <template #footer>
              <n-space justify="space-between">
                <span style="color: #999; font-size: 12px;">{{ item.created_at }}</span>
                <n-button v-if="!item.is_read" size="small" @click="markRead(item.id)">标记已读</n-button>
              </n-space>
            </template>
          </n-thing>
        </n-list-item>
      </n-list>
    </n-card>
  </div>
</template>
