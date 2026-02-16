<script setup>
import { ref, computed, onMounted, onUnmounted, h } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { NLayout, NLayoutSider, NLayoutContent, NMenu, NButton, NBadge, NDropdown, NAvatar, NSpace, NIcon } from 'naive-ui'
import { useUserStore } from '../store/user'
import { notificationApi, chatApi } from '../api/modules'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const collapsed = ref(false)
const activeKey = ref('home')
const unreadNotifications = ref(0)
const unreadMessages = ref(0)
const windowWidth = ref(window.innerWidth)

const isMobile = computed(() => windowWidth.value < 768)

const menuOptions = computed(() => [
  { 
    label: '首页', 
    key: 'home',
    icon: () => h(NIcon, null, { default: () => h('svg', { viewBox: '0 0 24 24', width: '18', height: '18' }, [
      h('path', { fill: 'currentColor', d: 'M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8z' })
    ])}),
  },
  { 
    label: '发布物品', 
    key: 'publish',
    icon: () => h(NIcon, null, { default: () => h('svg', { viewBox: '0 0 24 24', width: '18', height: '18' }, [
      h('path', { fill: 'currentColor', d: 'M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z' })
    ])}),
  },
  { 
    label: '心愿单', 
    key: 'wishlist',
    icon: () => h(NIcon, null, { default: () => h('svg', { viewBox: '0 0 24 24', width: '18', height: '18' }, [
      h('path', { fill: 'currentColor', d: 'M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z' })
    ])}),
  },
  { 
    label: '我的订单', 
    key: 'orders',
    icon: () => h(NIcon, null, { default: () => h('svg', { viewBox: '0 0 24 24', width: '18', height: '18' }, [
      h('path', { fill: 'currentColor', d: 'M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V5h14v14zM7 10h2v7H7zm4-3h2v10h-2zm4 6h2v4h-2z' })
    ])}),
  },
  { 
    label: '消息', 
    key: 'chat',
    icon: () => h(NIcon, null, { default: () => h('svg', { viewBox: '0 0 24 24', width: '18', height: '18' }, [
      h('path', { fill: 'currentColor', d: 'M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H6l-2 2V4h16v12z' })
    ])}),
  },
  { 
    label: '通知', 
    key: 'notifications',
    icon: () => h(NIcon, null, { default: () => h('svg', { viewBox: '0 0 24 24', width: '18', height: '18' }, [
      h('path', { fill: 'currentColor', d: 'M12 22c1.1 0 2-.9 2-2h-4c0 1.1.9 2 2 2zm6-6v-5c0-3.07-1.63-5.64-4.5-6.32V4c0-.83-.67-1.5-1.5-1.5s-1.5.67-1.5 1.5v.68C7.64 5.36 6 7.92 6 11v5l-2 2v1h16v-1l-2-2zm-2 1H8v-6c0-2.48 1.51-4.5 4-4.5s4 2.02 4 4.5v6z' })
    ])}),
  },
])

const userOptions = computed(() => {
  const options = [
    { label: '个人中心', key: 'profile' },
    { label: '编辑资料', key: 'profileEdit' },
    { label: '实名认证', key: 'verify' },
    { label: '诚信记录', key: 'credit' },
    { label: '举报管理', key: 'report' },
  ]
  if (userStore.isAdmin) {
    options.push({ label: '管理员后台', key: 'admin' })
  }
  options.push({ type: 'divider', key: 'd1' })
  options.push({ label: '退出登录', key: 'logout' })
  return options
})

const handleMenuSelect = (key) => {
  activeKey.value = key
  if (key === 'notifications') {
    router.push('/notifications')
  } else if (key === 'profileEdit') {
    router.push('/profile/edit')
  } else {
    router.push({ name: key.charAt(0).toUpperCase() + key.slice(1) })
  }
}

const handleUserSelect = (key) => {
  if (key === 'logout') {
    userStore.logout()
    router.push('/login')
  } else if (key === 'admin') {
    router.push('/admin')
  } else if (key === 'profileEdit') {
    router.push('/profile/edit')
  } else {
    router.push({ name: key.charAt(0).toUpperCase() + key.slice(1) })
  }
}

const fetchUnreadCounts = async () => {
  if (!userStore.isLoggedIn) return
  try {
    const [notifRes, chatRes] = await Promise.all([
      notificationApi.getUnreadCount(),
      chatApi.getUnreadCount()
    ])
    if (notifRes.code === 200) unreadNotifications.value = notifRes.data.count
    if (chatRes.code === 200) unreadMessages.value = chatRes.data.count
  } catch (error) {
    console.error('Failed to fetch unread counts:', error)
  }
}

const handleResize = () => {
  windowWidth.value = window.innerWidth
  if (isMobile.value) {
    collapsed.value = true
  }
}

onMounted(() => {
  window.addEventListener('resize', handleResize)
  if (isMobile.value) {
    collapsed.value = true
  }
  if (userStore.isLoggedIn) {
    userStore.fetchUserInfo()
    fetchUnreadCounts()
  }
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})
</script>

<template>
  <n-layout has-sider style="min-height: 100vh">
    <n-layout-sider
      bordered
      :collapsed="collapsed"
      collapse-mode="width"
      :collapsed-width="64"
      :width="220"
      :native-scrollbar="false"
      show-trigger
      @collapse="collapsed = true"
      @expand="collapsed = false"
      style="position: fixed; left: 0; top: 0; bottom: 0; z-index: 100;"
    >
      <div class="logo" :class="{ 'logo-collapsed': collapsed }">
        <span v-if="!collapsed">校园闲置交易</span>
        <span v-else>校</span>
      </div>
      
      <n-menu
        :collapsed="collapsed"
        :collapsed-width="64"
        :collapsed-icon-size="22"
        :options="menuOptions"
        :value="activeKey"
        @update:value="handleMenuSelect"
      />
      
      <div v-if="userStore.isLoggedIn" class="user-section">
        <n-dropdown :options="userOptions" @select="handleUserSelect" placement="right-start">
          <div class="user-info" :class="{ 'user-info-collapsed': collapsed }">
            <n-avatar round :size="collapsed ? 32 : 36">
              {{ userStore.userInfo?.username?.charAt(0)?.toUpperCase() }}
            </n-avatar>
            <div v-if="!collapsed" class="user-details">
              <div class="username">{{ userStore.userInfo?.username }}</div>
              <div class="credit">诚信值: {{ userStore.userInfo?.credit_score }}</div>
            </div>
          </div>
        </n-dropdown>
      </div>
      
      <div v-else class="auth-buttons" :class="{ 'auth-buttons-collapsed': collapsed }">
        <n-button v-if="!collapsed" block size="small" @click="router.push('/login')">登录</n-button>
        <n-button v-if="!collapsed" block type="primary" size="small" style="margin-top: 8px;" @click="router.push('/register')">注册</n-button>
        <n-button v-if="collapsed" size="small" quaternary @click="router.push('/login')">登</n-button>
      </div>
    </n-layout-sider>
    
    <n-layout :style="{ marginLeft: collapsed ? '64px' : '220px', transition: 'margin-left 0.3s' }">
      <n-layout-content style="padding: 16px; min-height: 100vh;">
        <router-view />
      </n-layout-content>
    </n-layout>
  </n-layout>
</template>

<style scoped>
.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: bold;
  color: #18a058;
  border-bottom: 1px solid #e0e0e6;
  cursor: pointer;
  transition: all 0.3s;
}

.logo-collapsed {
  font-size: 20px;
}

.user-section {
  position: absolute;
  bottom: 16px;
  left: 0;
  right: 0;
  padding: 0 12px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.user-info:hover {
  background-color: #f5f5f5;
}

.user-info-collapsed {
  justify-content: center;
  padding: 8px;
}

.user-details {
  flex: 1;
  min-width: 0;
}

.username {
  font-weight: 500;
  font-size: 14px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.credit {
  font-size: 12px;
  color: #999;
}

.auth-buttons {
  position: absolute;
  bottom: 16px;
  left: 0;
  right: 0;
  padding: 0 12px;
}

.auth-buttons-collapsed {
  display: flex;
  justify-content: center;
}

@media (max-width: 768px) {
  .user-section {
    display: none;
  }
  
  .auth-buttons {
    display: none;
  }
}
</style>
