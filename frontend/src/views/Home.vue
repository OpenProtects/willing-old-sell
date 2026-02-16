<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { NCard, NGrid, NGi, NInput, NSelect, NButton, NSpace, NPagination, NTag, NEmpty, NSpin } from 'naive-ui'
import { goodsApi } from '../api/modules'

const router = useRouter()

const loading = ref(false)
const goodsList = ref([])
const categories = ref([])
const pagination = ref({ page: 1, pageSize: 12, count: 0 })
const filters = ref({
  keyword: '',
  category: null,
  min_price: null,
  max_price: null
})

const isMobile = computed(() => window.innerWidth < 768)

const categoryOptions = computed(() => [
  { label: '全部', value: null },
  ...categories.value.map(c => ({ label: c.name, value: c.id }))
])

const fetchCategories = async () => {
  try {
    const res = await goodsApi.getCategories()
    if (res.code === 200) {
      categories.value = res.data
    }
  } catch (error) {
    console.error('Failed to fetch categories:', error)
  }
}

const fetchGoods = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.value.page,
      ...filters.value
    }
    const res = await goodsApi.getGoodsList(params)
    if (res.code === 200) {
      goodsList.value = res.data
      pagination.value.count = res.count || res.data.length
    }
  } catch (error) {
    console.error('Failed to fetch goods:', error)
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.value.page = 1
  fetchGoods()
}

const handlePageChange = (page) => {
  pagination.value.page = page
  fetchGoods()
}

const getConditionColor = (condition) => {
  const colors = { new: 'success', like_new: 'info', good: 'default', fair: 'warning', poor: 'error' }
  return colors[condition] || 'default'
}

const getImageUrl = (images) => {
  if (!images || images.length === 0) return ''
  const url = images[0]
  if (typeof url === 'object' && url !== null) {
    return ''
  }
  if (url.startsWith('http')) return url
  return `http://127.0.0.1:8000${url}`
}

onMounted(() => {
  fetchCategories()
  fetchGoods()
})
</script>

<template>
  <div class="home-container">
    <div class="search-bar">
      <div class="search-inputs">
        <n-input 
          v-model:value="filters.keyword" 
          placeholder="搜索物品名称或描述..." 
          clearable
          @keyup.enter="handleSearch"
        >
          <template #prefix>
            <svg viewBox="0 0 24 24" width="18" height="18" style="color: #999;">
              <path fill="currentColor" d="M15.5 14h-.79l-.28-.27a6.5 6.5 0 0 0 1.48-5.34c-.47-2.78-2.79-5-5.59-5.34a6.505 6.505 0 0 0-7.27 7.27c.34 2.8 2.56 5.12 5.34 5.59a6.5 6.5 0 0 0 5.34-1.48l.27.28v.79l4.25 4.25c.41.41 1.08.41 1.49 0 .41-.41.41-1.08 0-1.49L15.5 14zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/>
            </svg>
          </template>
        </n-input>
        <n-select 
          v-model:value="filters.category" 
          :options="categoryOptions" 
          placeholder="选择品类" 
          clearable
          style="width: 150px;"
        />
        <n-button type="primary" @click="handleSearch">
          搜索
        </n-button>
      </div>
      <n-button type="primary" @click="router.push('/publish')">
        <template #icon>
          <svg viewBox="0 0 24 24" width="16" height="16">
            <path fill="currentColor" d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/>
          </svg>
        </template>
        发布物品
      </n-button>
    </div>

    <n-spin :show="loading">
      <n-empty v-if="goodsList.length === 0 && !loading" description="暂无物品" style="margin-top: 60px;" />
      <div v-else class="goods-grid">
        <div 
          v-for="goods in goodsList" 
          :key="goods.id" 
          class="goods-card"
          @click="router.push(`/goods/${goods.id}`)"
        >
          <div class="goods-image">
            <img v-if="goods.images?.length" :src="getImageUrl(goods.images)" />
            <div v-else class="no-image">
              <svg viewBox="0 0 24 24" width="48" height="48">
                <path fill="#ccc" d="M21 19V5c0-1.1-.9-2-2-2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2zM8.5 13.5l2.5 3.01L14.5 12l4.5 6H5l3.5-4.5z"/>
              </svg>
            </div>
            <n-tag 
              v-if="goods.condition" 
              :type="getConditionColor(goods.condition)" 
              size="small"
              class="condition-tag"
            >
              {{ goods.condition_display }}
            </n-tag>
          </div>
          <div class="goods-info">
            <div class="goods-name">{{ goods.name }}</div>
            <div class="goods-price">¥{{ goods.price }}</div>
            <div class="goods-meta">
              <div class="seller-info">
                <div class="seller-avatar">
                  {{ goods.seller_name?.charAt(0)?.toUpperCase() }}
                </div>
                <span class="seller-name">{{ goods.seller_name }}</span>
              </div>
              <div class="seller-credit">
                诚信: {{ goods.seller_credit }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </n-spin>

    <div class="pagination-wrapper" v-if="pagination.count > pagination.pageSize">
      <n-pagination
        v-model:page="pagination.page"
        :page-count="Math.ceil(pagination.count / pagination.pageSize)"
        @update:page="handlePageChange"
        :page-slot="isMobile ? 5 : 9"
      />
    </div>
  </div>
</template>

<style scoped>
.home-container {
  max-width: 1400px;
  margin: 0 auto;
}

.search-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: #fff;
  border-radius: 12px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.search-inputs {
  display: flex;
  gap: 12px;
  flex: 1;
}

.search-inputs :deep(.n-input) {
  max-width: 300px;
}

.goods-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 20px;
}

.goods-card {
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.goods-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.goods-image {
  position: relative;
  width: 100%;
  height: 200px;
  background: #f5f5f5;
}

.goods-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.no-image {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.condition-tag {
  position: absolute;
  top: 10px;
  right: 10px;
}

.goods-info {
  padding: 16px;
}

.goods-name {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin-bottom: 8px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.goods-price {
  font-size: 22px;
  font-weight: bold;
  color: #f56c6c;
  margin-bottom: 12px;
}

.goods-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 12px;
  border-top: 1px solid #f0f0f0;
}

.seller-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.seller-avatar {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: #18a058;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 500;
}

.seller-name {
  font-size: 13px;
  color: #666;
}

.seller-credit {
  font-size: 12px;
  color: #999;
  background: #f5f5f5;
  padding: 2px 8px;
  border-radius: 10px;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 32px;
  padding: 16px 0;
}

@media (max-width: 768px) {
  .search-bar {
    flex-direction: column;
    align-items: stretch;
  }
  
  .search-inputs {
    flex-direction: column;
  }
  
  .search-inputs :deep(.n-input) {
    max-width: none;
  }
  
  .goods-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
  }
  
  .goods-image {
    height: 140px;
  }
  
  .goods-info {
    padding: 12px;
  }
  
  .goods-name {
    font-size: 14px;
  }
  
  .goods-price {
    font-size: 18px;
  }
}
</style>
