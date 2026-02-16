<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { NCard, NButton, NSpace, NTag, NDescriptions, NDescriptionsItem, NImage, NImageGroup, NModal, useMessage } from 'naive-ui'
import { goodsApi, orderApi, chatApi } from '../api/modules'
import { useUserStore } from '../store/user'

const route = useRoute()
const router = useRouter()
const message = useMessage()
const userStore = useUserStore()

const goods = ref(null)
const loading = ref(false)
const showOrderModal = ref(false)

const getImageUrl = (url) => {
  if (!url) return ''
  if (url.startsWith('http')) return url
  return `http://127.0.0.1:8000${url}`
}

const fetchGoods = async () => {
  loading.value = true
  try {
    const res = await goodsApi.getGoodsDetail(route.params.id)
    if (res.code === 200) {
      goods.value = res.data
    } else {
      message.error('物品不存在')
      router.push('/')
    }
  } catch (error) {
    message.error('获取物品详情失败')
    router.push('/')
  } finally {
    loading.value = false
  }
}

const handleChat = async () => {
  if (!userStore.isLoggedIn) {
    message.warning('请先登录')
    router.push('/login')
    return
  }
  try {
    const res = await chatApi.getOrCreateRoom({
      receiver_id: goods.value.seller_id,
      goods_id: goods.value.id,
      goods_name: goods.value.name
    })
    if (res.code === 200) {
      router.push(`/chat/${res.data.id}`)
    }
  } catch (error) {
    message.error('创建聊天失败')
  }
}

const handleBuy = async () => {
  if (!userStore.isLoggedIn) {
    message.warning('请先登录')
    router.push('/login')
    return
  }
  if (!userStore.isVerified) {
    message.warning('请先完成实名认证')
    router.push('/verify')
    return
  }
  showOrderModal.value = true
}

const confirmBuy = async () => {
  try {
    const res = await orderApi.createOrder({ goods_id: goods.value.id })
    if (res.code === 200) {
      message.success('订单创建成功')
      showOrderModal.value = false
      router.push('/orders')
    } else {
      message.error(res.message || '创建订单失败')
    }
  } catch (error) {
    message.error(error.message || '创建订单失败')
  }
}

onMounted(() => {
  fetchGoods()
})
</script>

<template>
  <div v-if="goods">
    <n-card>
      <n-space :size="24">
        <div style="width: 400px;">
          <n-image-group>
            <n-space vertical>
              <n-image
                v-if="goods.images?.length"
                :src="getImageUrl(goods.images[0])"
                object-fit="cover"
                style="width: 400px; height: 400px; border-radius: 8px;"
              />
              <div v-else style="width: 400px; height: 400px; background: #f5f5f5; border-radius: 8px; display: flex; align-items: center; justify-content: center;">
                暂无图片
              </div>
            </n-space>
          </n-image-group>
        </div>
        
        <div style="flex: 1;">
          <h1 style="margin-bottom: 16px;">{{ goods.name }}</h1>
          <div style="font-size: 28px; color: #f56c6c; font-weight: bold; margin-bottom: 16px;">
            ¥{{ goods.price }}
          </div>
          
          <n-descriptions :column="1" label-placement="left" bordered>
            <n-descriptions-item label="品类">{{ goods.category_name }}</n-descriptions-item>
            <n-descriptions-item label="成色">
              <n-tag type="info">{{ goods.condition_display }}</n-tag>
            </n-descriptions-item>
            <n-descriptions-item label="取货地点">{{ goods.pickup_location || '未设置' }}</n-descriptions-item>
            <n-descriptions-item label="浏览次数">{{ goods.view_count }}</n-descriptions-item>
            <n-descriptions-item label="发布时间">{{ goods.created_at }}</n-descriptions-item>
          </n-descriptions>
          
          <n-space style="margin-top: 24px;">
            <n-button type="primary" size="large" @click="handleBuy" :disabled="goods.seller_id === userStore.userInfo?.id">
              立即购买
            </n-button>
            <n-button size="large" @click="handleChat">联系卖家</n-button>
          </n-space>
          
          <n-card style="margin-top: 24px;" title="卖家信息">
            <n-descriptions :column="1" label-placement="left">
              <n-descriptions-item label="用户名">{{ goods.seller_name }}</n-descriptions-item>
              <n-descriptions-item label="诚信值">{{ goods.seller_credit }}</n-descriptions-item>
              <n-descriptions-item label="实名认证">
                <n-tag :type="goods.seller_verified ? 'success' : 'warning'">
                  {{ goods.seller_verified ? '已认证' : '未认证' }}
                </n-tag>
              </n-descriptions-item>
            </n-descriptions>
          </n-card>
        </div>
      </n-space>
    </n-card>
    
    <n-card style="margin-top: 16px;" title="物品描述">
      <div style="white-space: pre-wrap;">{{ goods.description }}</div>
    </n-card>

    <n-modal v-model:show="showOrderModal" preset="dialog" title="确认购买">
      <p>确定要购买此物品吗？</p>
      <p>物品：{{ goods?.name }}</p>
      <p>价格：¥{{ goods?.price }}</p>
      <template #action>
        <n-button @click="showOrderModal = false">取消</n-button>
        <n-button type="primary" @click="confirmBuy">确认购买</n-button>
      </template>
    </n-modal>
  </div>
</template>
