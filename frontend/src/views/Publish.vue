<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { NCard, NForm, NFormItem, NInput, NInputNumber, NSelect, NButton, NSpace, NUpload, useMessage } from 'naive-ui'
import { goodsApi } from '../api/modules'

const router = useRouter()
const message = useMessage()

const formRef = ref(null)
const loading = ref(false)
const categories = ref([])
const fileList = ref([])
const uploadedUrls = ref({})
const formValue = ref({
  name: '',
  category: null,
  description: '',
  price: null,
  condition: 'good',
  pickup_location: ''
})

const rules = {
  name: { required: true, message: '请输入物品名称', trigger: 'blur' },
  category: { required: true, type: 'number', message: '请选择品类', trigger: 'change' },
  description: { required: true, message: '请输入物品描述', trigger: 'blur' },
  price: { required: true, type: 'number', message: '请输入价格', trigger: 'blur' },
  condition: { required: true, message: '请选择成色', trigger: 'change' }
}

const categoryOptions = computed(() => 
  categories.value.map(c => ({ label: c.name, value: c.id }))
)

const conditionOptions = [
  { label: '全新', value: 'new' },
  { label: '几乎全新', value: 'like_new' },
  { label: '良好', value: 'good' },
  { label: '一般', value: 'fair' },
  { label: '较差', value: 'poor' }
]

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

const handleUpload = async ({ file, onFinish, onError, onProgress }) => {
  const formData = new FormData()
  formData.append('file', file.file)
  
  try {
    const res = await goodsApi.uploadImage(formData)
    if (res.code === 200) {
      uploadedUrls.value[file.id] = res.data.url
      onFinish()
    } else {
      message.error(res.message || '上传失败')
      onError()
    }
  } catch (error) {
    console.error('Upload error:', error)
    message.error('上传失败')
    onError()
  }
}

const handleRemove = ({ file }) => {
  delete uploadedUrls.value[file.id]
}

const handleSubmit = async () => {
  try {
    await formRef.value?.validate()
    
    const urls = Object.values(uploadedUrls.value)
    const pendingFiles = fileList.value.filter(f => f.status !== 'finished')
    if (pendingFiles.length > 0) {
      message.warning('请等待图片上传完成')
      return
    }
    
    loading.value = true
    
    const data = {
      ...formValue.value,
      images: urls
    }
    
    const res = await goodsApi.createGoods(data)
    if (res.code === 200 || res.code === 201) {
      message.success('发布成功')
      router.push('/')
    } else {
      message.error(res.message || '发布失败')
    }
  } catch (error) {
    console.error('Submit error:', error)
    message.error(error.message || '发布失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchCategories()
})
</script>

<template>
  <div>
    <n-card title="发布闲置物品">
      <n-form ref="formRef" :model="formValue" :rules="rules" label-width="100">
        <n-form-item label="物品名称" path="name">
          <n-input v-model:value="formValue.name" placeholder="请输入物品名称" maxlength="200" />
        </n-form-item>
        
        <n-form-item label="品类" path="category">
          <n-select v-model:value="formValue.category" :options="categoryOptions" placeholder="请选择品类" />
        </n-form-item>
        
        <n-form-item label="物品描述" path="description">
          <n-input v-model:value="formValue.description" type="textarea" placeholder="请详细描述物品情况" :rows="4" maxlength="1000" show-count />
        </n-form-item>
        
        <n-form-item label="价格" path="price">
          <n-input-number v-model:value="formValue.price" :min="0" :precision="2" placeholder="请输入价格" style="width: 200px;">
            <template #prefix>¥</template>
          </n-input-number>
        </n-form-item>
        
        <n-form-item label="成色" path="condition">
          <n-select v-model:value="formValue.condition" :options="conditionOptions" placeholder="请选择成色" />
        </n-form-item>
        
        <n-form-item label="取货地点" path="pickup_location">
          <n-input v-model:value="formValue.pickup_location" placeholder="请输入取货地点" maxlength="200" />
        </n-form-item>
        
        <n-form-item label="图片">
          <n-upload
            v-model:file-list="fileList"
            list-type="image-card"
            :max="5"
            :custom-request="handleUpload"
            @remove="handleRemove"
            accept="image/*"
          />
          <div style="color: #999; font-size: 12px;">最多上传5张图片</div>
        </n-form-item>
        
        <n-space>
          <n-button type="primary" :loading="loading" @click="handleSubmit">发布</n-button>
          <n-button @click="router.back()">取消</n-button>
        </n-space>
      </n-form>
    </n-card>
  </div>
</template>
