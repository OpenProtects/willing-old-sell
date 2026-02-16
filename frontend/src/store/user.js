import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '../api/modules'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const userInfo = ref(JSON.parse(localStorage.getItem('userInfo') || 'null'))

  const isLoggedIn = computed(() => !!token.value)
  const isAdmin = computed(() => userInfo.value?.is_admin || false)
  const isVerified = computed(() => userInfo.value?.is_verified || false)

  async function login(credentials) {
    const res = await authApi.login(credentials)
    if (res.code === 200) {
      token.value = res.data.token.access
      userInfo.value = res.data.user
      localStorage.setItem('token', res.data.token.access)
      localStorage.setItem('userInfo', JSON.stringify(res.data.user))
    }
    return res
  }

  async function register(data) {
    const res = await authApi.register(data)
    if (res.code === 200) {
      token.value = res.data.token.access
      userInfo.value = res.data.user
      localStorage.setItem('token', res.data.token.access)
      localStorage.setItem('userInfo', JSON.stringify(res.data.user))
    }
    return res
  }

  async function fetchUserInfo() {
    if (!token.value) return
    try {
      const res = await authApi.getUserInfo()
      if (res.code === 200) {
        userInfo.value = res.data
        localStorage.setItem('userInfo', JSON.stringify(res.data))
      }
    } catch (error) {
      console.error('Failed to fetch user info:', error)
    }
  }

  function logout() {
    token.value = ''
    userInfo.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('userInfo')
  }

  function updateUserInfo(info) {
    userInfo.value = { ...userInfo.value, ...info }
    localStorage.setItem('userInfo', JSON.stringify(userInfo.value))
  }

  return {
    token,
    userInfo,
    isLoggedIn,
    isAdmin,
    isVerified,
    login,
    register,
    logout,
    fetchUserInfo,
    updateUserInfo
  }
})
