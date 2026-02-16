import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '../store/user'

const routes = [
  {
    path: '/',
    component: () => import('../views/Layout.vue'),
    children: [
      { path: '', name: 'Home', component: () => import('../views/Home.vue') },
      { path: 'goods/:id', name: 'GoodsDetail', component: () => import('../views/GoodsDetail.vue') },
      { path: 'publish', name: 'Publish', component: () => import('../views/Publish.vue'), meta: { requiresAuth: true } },
      { path: 'wishlist', name: 'Wishlist', component: () => import('../views/Wishlist.vue'), meta: { requiresAuth: true } },
      { path: 'orders', name: 'Orders', component: () => import('../views/Orders.vue'), meta: { requiresAuth: true } },
      { path: 'chat', name: 'Chat', component: () => import('../views/Chat.vue'), meta: { requiresAuth: true } },
      { path: 'chat/:id', name: 'ChatRoom', component: () => import('../views/Chat.vue'), meta: { requiresAuth: true } },
      { path: 'profile', name: 'Profile', component: () => import('../views/Profile.vue'), meta: { requiresAuth: true } },
      { path: 'profile/edit', name: 'ProfileEdit', component: () => import('../views/ProfileEdit.vue'), meta: { requiresAuth: true } },
      { path: 'verify', name: 'Verify', component: () => import('../views/Verify.vue'), meta: { requiresAuth: true } },
      { path: 'report', name: 'Report', component: () => import('../views/Report.vue'), meta: { requiresAuth: true } },
      { path: 'credit', name: 'Credit', component: () => import('../views/Credit.vue'), meta: { requiresAuth: true } },
      { path: 'notifications', name: 'Notifications', component: () => import('../views/Notifications.vue'), meta: { requiresAuth: true } },
      { path: 'admin', name: 'Admin', component: () => import('../views/Admin.vue'), meta: { requiresAuth: true, requiresAdmin: true } },
    ]
  },
  { path: '/login', name: 'Login', component: () => import('../views/Login.vue') },
  { path: '/register', name: 'Register', component: () => import('../views/Register.vue') },
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  
  if (to.meta.requiresAuth && !userStore.isLoggedIn) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
  } else if (to.meta.requiresAdmin && !userStore.isAdmin) {
    next({ name: 'Home' })
  } else {
    next()
  }
})

export default router
