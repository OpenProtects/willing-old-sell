import api from './index'

export const authApi = {
  register: (data) => api.post('/auth/register/', data),
  login: (data) => api.post('/auth/login/', data),
  getUserInfo: () => api.get('/auth/users/'),
  getUsers: (params) => api.get('/auth/users/', { params }),
  updateUserInfo: (data) => api.patch('/auth/users/', data),
  verifyRealname: (data) => api.post('/auth/users/verify_realname/', data),
  changePassword: (data) => api.post('/auth/users/change_password/', data),
  getCreditRecords: () => api.get('/auth/users/credit_records/'),
  uploadAvatar: (formData) => api.post('/auth/users/upload_avatar/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
}

export const goodsApi = {
  getCategories: () => api.get('/goods/categories/'),
  getGoodsList: (params) => api.get('/goods/goods/', { params }),
  getGoodsDetail: (id) => api.get(`/goods/goods/${id}/`),
  createGoods: (data) => api.post('/goods/goods/', data),
  updateGoods: (id, data) => api.patch(`/goods/goods/${id}/`, data),
  deleteGoods: (id) => api.delete(`/goods/goods/${id}/`),
  getMyGoods: () => api.get('/goods/goods/my_goods/'),
  offShelf: (id) => api.post(`/goods/goods/${id}/off_shelf/`),
  onShelf: (id) => api.post(`/goods/goods/${id}/on_shelf/`),
  uploadImage: (formData) => api.post('/goods/upload/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
}

export const wishlistApi = {
  getWishlists: () => api.get('/wishlist/wishlists/'),
  createWishlist: (data) => api.post('/wishlist/wishlists/', data),
  updateWishlist: (id, data) => api.patch(`/wishlist/wishlists/${id}/`, data),
  deleteWishlist: (id) => api.delete(`/wishlist/wishlists/${id}/`),
  getMatchResults: (id) => api.get(`/wishlist/wishlists/${id}/match_results/`),
  rematch: (id) => api.post(`/wishlist/wishlists/${id}/rematch/`),
}

export const orderApi = {
  getOrders: (params) => api.get('/orders/orders/', { params }),
  getOrderDetail: (id) => api.get(`/orders/orders/${id}/`),
  createOrder: (data) => api.post('/orders/orders/', data),
  payOrder: (id) => api.post(`/orders/orders/${id}/pay/`),
  confirmOrder: (id) => api.post(`/orders/orders/${id}/confirm/`),
  cancelOrder: (id) => api.post(`/orders/orders/${id}/cancel/`),
  createEvaluation: (data) => api.post('/orders/evaluations/', data),
}

export const chatApi = {
  getChatRooms: () => api.get('/chat/rooms/'),
  getChatRoom: (id) => api.get(`/chat/rooms/${id}/`),
  sendMessage: (data) => api.post('/chat/rooms/send_message/', data),
  getOrCreateRoom: (params) => api.get('/chat/rooms/get_or_create_room/', { params }),
  getUnreadCount: () => api.get('/chat/rooms/unread_count/'),
}

export const reportApi = {
  getReports: (params) => api.get('/report/reports/', { params }),
  createReport: (data) => api.post('/report/reports/', data),
  handleReport: (id, data) => api.post(`/report/reports/${id}/handle/`, data),
  getMyReports: () => api.get('/report/reports/my_reports/'),
  getReportedMe: () => api.get('/report/reports/reported_me/'),
}

export const creditApi = {
  getRecords: (params) => api.get('/credit/records/', { params }),
  adjustCredit: (data) => api.post('/credit/records/adjust/', data),
  getUserCredit: (params) => api.get('/credit/records/user_credit/', { params }),
}

export const notificationApi = {
  getNotifications: (params) => api.get('/auth/notifications/', { params }),
  markRead: (id) => api.post(`/auth/notifications/${id}/mark_read/`),
  markAllRead: () => api.post('/auth/notifications/mark_all_read/'),
  getUnreadCount: () => api.get('/auth/notifications/unread_count/'),
}
