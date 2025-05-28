<template>
  <div class="car-detail">
    <h2>车辆详情</h2>
    <el-form :model="form" label-width="100px" v-loading="loading">
      <el-form-item label="车牌号">
        <el-input v-model="form.license" />
      </el-form-item>
      <el-form-item label="品牌">
        <el-input v-model="form.brand" />
      </el-form-item>
      <el-form-item label="型号">
        <el-input v-model="form.model" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="handleSave">保存</el-button>
        <el-button @click="navigateTo('/dashboard/customer/cars')">返回</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/store/authStore'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const form = ref({})
const loading = ref(true)

onMounted(async () => {
  try {
    // TODO: 根据route.params.id调用API获取车辆详情
    form.value = {
      id: route.params.id,
      license: '沪A12345',
      brand: '丰田',
      model: '凯美瑞'
    }
  } catch (error) {
    console.error('获取车辆详情失败:', error)
  } finally {
    loading.value = false
  }
})

const handleSave = async () => {
  try {
    // TODO: 调用API更新车辆信息
    console.log('保存修改:', form.value)
    router.push('/dashboard/customer/cars')
  } catch (error) {
    console.error('保存失败:', error)
  }
}
</script>

<style scoped>
.car-detail {
  padding: 20px;
  max-width: 600px;
}
</style>