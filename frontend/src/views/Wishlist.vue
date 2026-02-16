<script setup>
import { ref, onMounted, h } from 'vue'
import { NCard, NButton, NSpace, NDataTable, NTag, NModal, NForm, NFormItem, NInput, NInputNumber, NSelect, useMessage, NEmpty } from 'naive-ui'
import { wishlistApi, goodsApi } from '../api/modules'

const message = useMessage()

const wishlists = ref([])
const categories = ref([])
const loading = ref(false)
const showModal = ref(false)
const showMatchModal = ref(false)
const currentWishlist = ref(null)
const matchResults = ref([])

const formRef = ref(null)
const formValue = ref({
  name: '',
  category: null,
  min_price: null,
  max_price: null,
  description: ''
})

const rules = {
  name: { required: true, message: '请输入物品名称', trigger: 'blur' }
}

const columns = [
  { title: '物品名称', key: 'name' },
  { title: '品类', key: 'category_name' },
  { title: '价格区间', key: 'price_range', render: (row) => `¥${row.min_price || 0} - ¥${row.max_price || '不限'}` },
  { title: '描述', key: 'description', ellipsis: { tooltip: true } },
  { title: '状态', key: 'match_status', render: (row) => h(NTag, { type: row.match_status === 'matched' ? 'success' : 'default' }, () => row.match_status_display) },
  { title: '匹配数', key: 'match_count' },
  { title: '创建时间', key: 'created_at' },
  { title: '操作', key: 'actions', render: (row) => h(NSpace, null, () => [
    h(NButton, { size: 'small', onClick: () => viewMatches(row) }, () => '查看匹配'),
    h(NButton, { size: 'small', onClick: () => handleRematch(row) }, () => '重新匹配'),
    h(NButton, { size: 'small', type: 'error', onClick: () => handleDelete(row) }, () => '删除')
  ])}
]

const fetchCategories = async () => {
  try {
    const res = await goodsApi.getCategories()
    if (res.code === 200) categories.value = res.data
  } catch (error) {
    console.error(error)
  }
}

const fetchWishlists = async () => {
  loading.value = true
  try {
    const res = await wishlistApi.getWishlists()
    if (res.code === 200) wishlists.value = res.data
  } catch (error) {
    message.error('获取心愿单失败')
  } finally {
    loading.value = false
  }
}

const handleCreate = async () => {
  try {
    await formRef.value?.validate()
    const res = await wishlistApi.createWishlist(formValue.value)
    if (res.code === 200) {
      message.success('创建成功')
      showModal.value = false
      fetchWishlists()
      formValue.value = { name: '', category: null, min_price: null, max_price: null, description: '' }
    } else {
      message.error(res.message || '创建失败')
    }
  } catch (error) {
    message.error('创建失败')
  }
}

const viewMatches = async (row) => {
  currentWishlist.value = row
  try {
    const res = await wishlistApi.getMatchResults(row.id)
    if (res.code === 200) {
      matchResults.value = res.data
      showMatchModal.value = true
    }
  } catch (error) {
    message.error('获取匹配结果失败')
  }
}

const handleRematch = async (row) => {
  try {
    const res = await wishlistApi.rematch(row.id)
    if (res.code === 200) {
      message.success('重新匹配成功')
      fetchWishlists()
    } else {
      message.error(res.message || '匹配失败')
    }
  } catch (error) {
    message.error('匹配失败')
  }
}

const handleDelete = async (row) => {
  try {
    const res = await wishlistApi.deleteWishlist(row.id)
    if (res.code === 200) {
      message.success('删除成功')
      fetchWishlists()
    }
  } catch (error) {
    message.error('删除失败')
  }
}

onMounted(() => {
  fetchCategories()
  fetchWishlists()
})
</script>

<template>
  <div>
    <n-card title="我的心愿单">
      <template #header-extra>
        <n-button type="primary" @click="showModal = true">新建心愿单</n-button>
      </template>
      
      <n-data-table :columns="columns" :data="wishlists" :loading="loading" />
    </n-card>

    <n-modal v-model:show="showModal" preset="card" title="新建心愿单" style="width: 500px;">
      <n-form ref="formRef" :model="formValue" :rules="rules" label-width="80">
        <n-form-item label="物品名称" path="name">
          <n-input v-model:value="formValue.name" placeholder="请输入想要的物品名称" />
        </n-form-item>
        <n-form-item label="品类" path="category">
          <n-select v-model:value="formValue.category" :options="categories.map(c => ({ label: c.name, value: c.id }))" placeholder="选择品类" />
        </n-form-item>
        <n-form-item label="价格区间">
          <n-space>
            <n-input-number v-model:value="formValue.min_price" :min="0" placeholder="最低价" style="width: 120px;" />
            <span>-</span>
            <n-input-number v-model:value="formValue.max_price" :min="0" placeholder="最高价" style="width: 120px;" />
          </n-space>
        </n-form-item>
        <n-form-item label="描述" path="description">
          <n-input v-model:value="formValue.description" type="textarea" placeholder="描述您的需求" :rows="3" />
        </n-form-item>
      </n-form>
      <template #footer>
        <n-space justify="end">
          <n-button @click="showModal = false">取消</n-button>
          <n-button type="primary" @click="handleCreate">创建</n-button>
        </n-space>
      </template>
    </n-modal>

    <n-modal v-model:show="showMatchModal" preset="card" title="匹配结果" style="width: 600px;">
      <n-empty v-if="matchResults.length === 0" description="暂无匹配结果" />
      <n-space vertical v-else>
        <n-card v-for="item in matchResults" :key="item.id" size="small">
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
              <div style="font-weight: bold;">{{ item.goods_name }}</div>
              <div style="color: #f56c6c;">¥{{ item.goods_price }}</div>
              <div style="color: #999; font-size: 12px;">卖家: {{ item.goods_seller_name }} (诚信值: {{ item.goods_seller_credit }})</div>
            </div>
            <div>
              <n-tag>匹配度: {{ (item.similarity_score * 100).toFixed(0) }}%</n-tag>
              <n-button size="small" style="margin-left: 8px;" @click="$router.push(`/goods/${item.goods_id}`)">查看详情</n-button>
            </div>
          </div>
        </n-card>
      </n-space>
    </n-modal>
  </div>
</template>
