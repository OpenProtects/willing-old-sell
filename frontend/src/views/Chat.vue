<script setup>
import { ref, onMounted, onUnmounted, nextTick, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { NAvatar, NEmpty, NScrollbar, NInput, NButton, useMessage } from 'naive-ui'
import { chatApi } from '../api/modules'
import { useUserStore } from '../store/user'

const route = useRoute()
const router = useRouter()
const message = useMessage()
const userStore = useUserStore()

const chatRooms = ref([])
const currentRoom = ref(null)
const messages = ref([])
const newMessage = ref('')
const loading = ref(false)
const scrollbarRef = ref(null)
const inputRef = ref(null)
const wsConnected = ref(false)
const wsConnecting = ref(false)

const chatWs = ref(null)
const reconnectTimer = ref(null)
const heartbeatTimer = ref(null)
const reconnectAttempts = ref(0)
const maxReconnectAttempts = 10

const isMobile = computed(() => window.innerWidth <= 768)
const showChatList = ref(true)
const currentUserId = computed(() => userStore.userInfo?.id)

const isSelfMessage = (msg) => {
  return msg.sender_id === currentUserId.value
}

const fetchChatRooms = async () => {
  loading.value = true
  try {
    const res = await chatApi.getChatRooms()
    if (res.code === 200) {
      chatRooms.value = res.data
      if (route.params.id) {
        const room = chatRooms.value.find(r => r.id === parseInt(route.params.id))
        if (room) openRoom(room)
      }
    }
  } catch (error) {
    console.error('Failed to fetch chat rooms:', error)
  } finally {
    loading.value = false
  }
}

const openRoom = async (room) => {
  currentRoom.value = room
  showChatList.value = false
  router.push(`/chat/${room.id}`)
  loading.value = true
  
  try {
    const res = await chatApi.getChatRoom(room.id)
    if (res.code === 200) {
      currentRoom.value = res.data.room
      messages.value = res.data.messages
      nextTick(() => scrollToBottom())
      connectChatWs(room.id)
    }
  } catch (error) {
    message.error('获取聊天记录失败')
  } finally {
    loading.value = false
  }
}

const startHeartbeat = () => {
  stopHeartbeat()
  heartbeatTimer.value = setInterval(() => {
    if (chatWs.value && chatWs.value.readyState === WebSocket.OPEN) {
      chatWs.value.send(JSON.stringify({ type: 'ping' }))
    }
  }, 30000)
}

const stopHeartbeat = () => {
  if (heartbeatTimer.value) {
    clearInterval(heartbeatTimer.value)
    heartbeatTimer.value = null
  }
}

const connectChatWs = (roomId) => {
  if (chatWs.value) {
    chatWs.value.close()
    chatWs.value = null
  }
  
  stopHeartbeat()
  wsConnecting.value = true
  wsConnected.value = false
  
  const token = localStorage.getItem('token')
  if (!token) {
    message.error('请先登录')
    return
  }
  
  const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  const wsHost = window.location.hostname + ':8000'
  const wsUrl = `${wsProtocol}//${wsHost}/ws/chat/${roomId}/?token=${token}`
  
  console.log('Connecting to WebSocket:', wsUrl)
  
  try {
    chatWs.value = new WebSocket(wsUrl)
    
    chatWs.value.onopen = () => {
      console.log('WebSocket connected')
      wsConnected.value = true
      wsConnecting.value = false
      reconnectAttempts.value = 0
      startHeartbeat()
    }
    
    chatWs.value.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        console.log('WebSocket message received:', data)
        
        if (data.type === 'message') {
          const exists = messages.value.some(m => m.id === data.data.id)
          if (!exists) {
            messages.value.push(data.data)
            scrollToBottom()
          }
        } else if (data.type === 'pong') {
          console.log('Pong received')
        }
      } catch (e) {
        console.error('Parse message error:', e)
      }
    }
    
    chatWs.value.onerror = (error) => {
      console.error('WebSocket error:', error)
      wsConnecting.value = false
    }
    
    chatWs.value.onclose = (event) => {
      console.log('WebSocket closed:', event.code, event.reason)
      wsConnected.value = false
      wsConnecting.value = false
      stopHeartbeat()
      
      if (event.code !== 1000 && reconnectAttempts.value < maxReconnectAttempts && currentRoom.value) {
        reconnectAttempts.value++
        console.log(`Reconnecting... attempt ${reconnectAttempts.value}`)
        reconnectTimer.value = setTimeout(() => {
          if (currentRoom.value) {
            connectChatWs(currentRoom.value.id)
          }
        }, 2000)
      }
    }
  } catch (error) {
    console.error('WebSocket creation error:', error)
    wsConnecting.value = false
  }
}

const sendMessage = () => {
  if (!newMessage.value.trim()) return
  
  if (!chatWs.value || chatWs.value.readyState !== WebSocket.OPEN) {
    message.error('连接已断开，正在重连...')
    if (currentRoom.value) {
      connectChatWs(currentRoom.value.id)
    }
    return
  }
  
  const content = newMessage.value.trim()
  const tempId = Date.now()
  
  const tempMessage = {
    id: tempId,
    sender_id: currentUserId.value,
    sender_name: userStore.userInfo?.username,
    content: content,
    created_at: new Date().toLocaleString('zh-CN'),
    pending: true
  }
  
  messages.value.push(tempMessage)
  scrollToBottom()
  
  try {
    chatWs.value.send(JSON.stringify({
      type: 'chat_message',
      content: content
    }))
    newMessage.value = ''
    
    setTimeout(() => {
      const idx = messages.value.findIndex(m => m.id === tempId)
      if (idx !== -1 && messages.value[idx].pending) {
        messages.value[idx].pending = false
      }
    }, 1000)
    
    nextTick(() => {
      inputRef.value?.focus()
    })
  } catch (error) {
    console.error('Send message error:', error)
    message.error('发送失败')
    const idx = messages.value.findIndex(m => m.id === tempId)
    if (idx !== -1) {
      messages.value.splice(idx, 1)
    }
  }
}

const scrollToBottom = () => {
  nextTick(() => {
    if (scrollbarRef.value) {
      scrollbarRef.value.scrollTo({ top: 999999, behavior: 'smooth' })
    }
  })
}

const goBack = () => {
  showChatList.value = true
  currentRoom.value = null
  router.push('/chat')
}

const formatTime = (timeStr) => {
  if (!timeStr) return ''
  const date = new Date(timeStr)
  const now = new Date()
  const isToday = date.toDateString() === now.toDateString()
  
  if (isToday) {
    return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  }
  
  const yesterday = new Date(now)
  yesterday.setDate(yesterday.getDate() - 1)
  if (date.toDateString() === yesterday.toDateString()) {
    return '昨天 ' + date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  }
  
  return date.toLocaleDateString('zh-CN', { month: '2-digit', day: '2-digit' }) + ' ' + 
         date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

onMounted(async () => {
  if (!userStore.userInfo && userStore.isLoggedIn) {
    await userStore.fetchUserInfo()
  }
  fetchChatRooms()
})

onUnmounted(() => {
  stopHeartbeat()
  if (chatWs.value) {
    chatWs.value.close()
  }
  if (reconnectTimer.value) {
    clearTimeout(reconnectTimer.value)
  }
})
</script>

<template>
  <div class="chat-container">
    <div class="chat-sidebar" :class="{ 'mobile-hidden': currentRoom && isMobile }">
      <div class="sidebar-header">
        <h3>消息</h3>
      </div>
      <div class="chat-list">
        <n-empty v-if="chatRooms.length === 0" description="暂无消息" />
        <div 
          v-for="room in chatRooms" 
          :key="room.id" 
          class="chat-item"
          :class="{ active: currentRoom?.id === room.id }"
          @click="openRoom(room)"
        >
          <div class="avatar-wrapper">
            <n-avatar round :size="48" class="avatar">
              {{ room.other_user_name?.charAt(0)?.toUpperCase() }}
            </n-avatar>
            <span v-if="room.unread_count > 0" class="unread-badge">
              {{ room.unread_count > 99 ? '99+' : room.unread_count }}
            </span>
          </div>
          <div class="chat-info">
            <div class="chat-header-row">
              <span class="chat-name">{{ room.other_user_name }}</span>
              <span class="chat-time">{{ room.updated_at ? formatTime(room.updated_at) : '' }}</span>
            </div>
            <div class="chat-preview">
              <span class="goods-tag">{{ room.goods_name }}</span>
              <span v-if="room.last_message" class="last-message">
                {{ room.last_message.content }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div class="chat-main" :class="{ 'mobile-full': !showChatList && isMobile }">
      <template v-if="currentRoom">
        <div class="chat-header">
          <button class="back-btn" @click="goBack">
            <svg viewBox="0 0 24 24" width="24" height="24">
              <path fill="currentColor" d="M20 11H7.83l5.59-5.59L12 4l-8 8 8 8 1.41-1.41L7.83 13H20v-2z"/>
            </svg>
          </button>
          <div class="header-info">
            <span class="header-name">{{ currentRoom.other_user_name }}</span>
            <span class="header-goods" @click="router.push(`/goods/${currentRoom.goods_id}`)">
              {{ currentRoom.goods_name }}
            </span>
          </div>
          <div class="ws-status" :class="{ connected: wsConnected, connecting: wsConnecting }">
            {{ wsConnected ? '已连接' : (wsConnecting ? '连接中...' : '未连接') }}
          </div>
        </div>
        
        <div class="chat-messages">
          <n-scrollbar ref="scrollbarRef" style="height: 100%;">
            <div class="messages-wrapper">
              <n-empty v-if="messages.length === 0" description="暂无消息，发送第一条消息吧" />
              <div 
                v-for="msg in messages" 
                :key="msg.id" 
                class="message-item"
                :class="{ 'self': isSelfMessage(msg), 'pending': msg.pending }"
              >
                <div class="message-avatar">
                  <n-avatar round :size="36">
                    {{ msg.sender_name?.charAt(0)?.toUpperCase() }}
                  </n-avatar>
                </div>
                <div class="message-content">
                  <div class="message-info">
                    <span class="sender-name">{{ msg.sender_name }}</span>
                    <span class="message-time">{{ formatTime(msg.created_at) }}</span>
                  </div>
                  <div class="message-bubble">
                    {{ msg.content }}
                    <span v-if="msg.pending" class="pending-indicator">...</span>
                  </div>
                </div>
              </div>
            </div>
          </n-scrollbar>
        </div>
        
        <div class="chat-input-area">
          <div class="input-wrapper">
            <n-input
              ref="inputRef"
              v-model:value="newMessage"
              type="text"
              placeholder="输入消息..."
              @keyup.enter="sendMessage"
            />
            <n-button 
              type="primary" 
              @click="sendMessage"
              :disabled="!newMessage.trim()"
            >
              发送
            </n-button>
          </div>
        </div>
      </template>
      
      <template v-else>
        <div class="no-chat-selected">
          <n-empty description="选择一个聊天开始对话" />
        </div>
      </template>
    </div>
  </div>
</template>

<style scoped>
.chat-container {
  display: flex;
  height: calc(100vh - 120px);
  min-height: 500px;
  background: #fff;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.chat-sidebar {
  width: 320px;
  border-right: 1px solid #e5e5e5;
  display: flex;
  flex-direction: column;
  background: #f5f5f5;
}

.sidebar-header {
  padding: 16px 20px;
  background: #ededed;
  border-bottom: 1px solid #d9d9d9;
}

.sidebar-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 500;
  color: #333;
}

.chat-list {
  flex: 1;
  overflow-y: auto;
}

.chat-item {
  display: flex;
  padding: 12px 16px;
  cursor: pointer;
  transition: background-color 0.2s;
  border-bottom: 1px solid #e5e5e5;
  background: #fff;
}

.chat-item:hover {
  background: #f0f0f0;
}

.chat-item.active {
  background: #e8e8e8;
}

.avatar-wrapper {
  position: relative;
  margin-right: 12px;
}

.avatar {
  background: #07c160;
  color: #fff;
  font-weight: 500;
}

.unread-badge {
  position: absolute;
  top: -4px;
  right: -4px;
  min-width: 18px;
  height: 18px;
  padding: 0 5px;
  background: #f5222d;
  color: #fff;
  font-size: 11px;
  border-radius: 9px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.chat-info {
  flex: 1;
  min-width: 0;
}

.chat-header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.chat-name {
  font-size: 15px;
  font-weight: 500;
  color: #333;
}

.chat-time {
  font-size: 12px;
  color: #999;
}

.chat-preview {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.goods-tag {
  font-size: 12px;
  color: #07c160;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.last-message {
  font-size: 13px;
  color: #999;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #f5f5f5;
}

.chat-header {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  background: #ededed;
  border-bottom: 1px solid #d9d9d9;
}

.back-btn {
  display: none;
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
  margin-right: 8px;
  color: #333;
}

.header-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.header-name {
  font-size: 16px;
  font-weight: 500;
  color: #333;
}

.header-goods {
  font-size: 12px;
  color: #07c160;
  cursor: pointer;
}

.header-goods:hover {
  text-decoration: underline;
}

.ws-status {
  font-size: 12px;
  padding: 4px 8px;
  border-radius: 4px;
  background: #f0f0f0;
  color: #999;
}

.ws-status.connected {
  background: #e6f7e6;
  color: #07c160;
}

.ws-status.connecting {
  background: #fff7e6;
  color: #fa8c16;
}

.chat-messages {
  flex: 1;
  overflow: hidden;
  background: #f5f5f5;
}

.messages-wrapper {
  padding: 16px;
  min-height: 100%;
}

.message-item {
  display: flex;
  margin-bottom: 16px;
}

.message-item.self {
}

.message-item.pending {
  opacity: 0.7;
}

.message-avatar {
  flex-shrink: 0;
}

.message-content {
  max-width: 60%;
  margin: 0 8px;
}

.message-item.self .message-content {
}

.message-info {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.message-item.self .message-info {
}

.sender-name {
  font-size: 12px;
  color: #999;
}

.message-time {
  font-size: 11px;
  color: #bbb;
}

.message-bubble {
  padding: 10px 14px;
  background: #fff;
  border-radius: 8px;
  font-size: 14px;
  line-height: 1.5;
  word-break: break-word;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
  position: relative;
}

.message-item.self .message-bubble {
  background: #95ec69;
  color: #333;
}

.pending-indicator {
  margin-left: 4px;
  color: #999;
}

.chat-input-area {
  padding: 12px 16px;
  background: #f5f5f5;
  border-top: 1px solid #e5e5e5;
}

.input-wrapper {
  display: flex;
  gap: 12px;
  align-items: center;
}

.input-wrapper :deep(.n-input) {
  flex: 1;
}

.input-wrapper :deep(.n-input .n-input__input-el) {
  font-size: 14px;
}

.no-chat-selected {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

@media (max-width: 768px) {
  .chat-container {
    height: calc(100vh - 80px);
    border-radius: 0;
  }
  
  .chat-sidebar {
    position: absolute;
    width: 100%;
    z-index: 10;
  }
  
  .chat-sidebar.mobile-hidden {
    display: none;
  }
  
  .chat-main.mobile-full {
    width: 100%;
  }
  
  .back-btn {
    display: block;
  }
  
  .message-content {
    max-width: 75%;
  }
}
</style>
