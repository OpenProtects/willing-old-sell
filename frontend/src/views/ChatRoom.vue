<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { NCard, NSpace, NButton, NInput, NAvatar, NEmpty, NScrollbar, useMessage } from 'naive-ui'
import { chatApi } from '../api/modules'
import { useUserStore } from '../store/user'

const route = useRoute()
const router = useRouter()
const message = useMessage()
const userStore = useUserStore()

const room = ref(null)
const messages = ref([])
const newMessage = ref('')
const loading = ref(false)
const scrollbarRef = ref(null)

const fetchChatRoom = async () => {
  try {
    const res = await chatApi.getChatRoom(route.params.id)
    if (res.code === 200) {
      room.value = res.data.room
      messages.value = res.data.messages
      nextTick(() => {
        scrollToBottom()
      })
    } else {
      message.error('聊天室不存在')
      router.push('/chat')
    }
  } catch (error) {
    message.error('获取聊天记录失败')
    router.push('/chat')
  }
}

const sendMessage = async () => {
  if (!newMessage.value.trim()) return
  loading.value = true
  try {
    const res = await chatApi.sendMessage({
      room_id: room.value.id,
      receiver_id: room.value.other_user_id,
      content: newMessage.value.trim()
    })
    if (res.code === 200) {
      messages.value.push(res.data)
      newMessage.value = ''
      nextTick(() => {
        scrollToBottom()
      })
    }
  } catch (error) {
    message.error('发送失败')
  } finally {
    loading.value = false
  }
}

const scrollToBottom = () => {
  if (scrollbarRef.value) {
    scrollbarRef.value.scrollTo({ top: 999999 })
  }
}

onMounted(() => {
  fetchChatRoom()
})
</script>

<template>
  <div>
    <n-card :title="room?.other_user_name || '聊天'" style="height: calc(100vh - 130px); display: flex; flex-direction: column;">
      <template #header-extra>
        <n-button text @click="router.push('/chat')">返回列表</n-button>
      </template>
      
      <div v-if="room" style="flex: 1; display: flex; flex-direction: column; overflow: hidden;">
        <div v-if="room.goods_name" style="padding: 8px 0; border-bottom: 1px solid #eee; margin-bottom: 12px;">
          关于物品：<span style="color: #18a058; cursor: pointer;" @click="router.push(`/goods/${room.goods_id}`)">{{ room.goods_name }}</span>
        </div>
        
        <n-scrollbar ref="scrollbarRef" style="flex: 1;">
          <n-empty v-if="messages.length === 0" description="暂无消息，发送第一条消息吧" />
          <div v-else style="padding: 12px;">
            <div v-for="msg in messages" :key="msg.id" :style="{ display: 'flex', justifyContent: msg.sender === userStore.userInfo?.id ? 'flex-end' : 'flex-start', marginBottom: '16px' }">
              <div :style="{ display: 'flex', alignItems: 'flex-start', flexDirection: msg.sender === userStore.userInfo?.id ? 'row-reverse' : 'row' }">
                <n-avatar round size="small" style="margin: 0 8px;">{{ msg.sender_name?.charAt(0)?.toUpperCase() }}</n-avatar>
                <div>
                  <div :style="{ textAlign: msg.sender === userStore.userInfo?.id ? 'right' : 'left', fontSize: '12px', color: '#999', marginBottom: '4px' }">
                    {{ msg.sender_name }} {{ msg.created_at }}
                  </div>
                  <div :style="{ 
                    background: msg.sender === userStore.userInfo?.id ? '#18a058' : '#f5f5f5', 
                    color: msg.sender === userStore.userInfo?.id ? '#fff' : '#333',
                    padding: '8px 12px', 
                    borderRadius: '8px',
                    maxWidth: '300px',
                    wordBreak: 'break-word'
                  }">
                    {{ msg.content }}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </n-scrollbar>
        
        <n-space style="margin-top: 12px;">
          <n-input v-model:value="newMessage" placeholder="输入消息" @keyup.enter="sendMessage" style="flex: 1;" />
          <n-button type="primary" :loading="loading" @click="sendMessage">发送</n-button>
        </n-space>
      </div>
    </n-card>
  </div>
</template>
