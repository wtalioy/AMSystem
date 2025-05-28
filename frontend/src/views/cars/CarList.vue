<template>
  <div class="car-management">
    <h2>我的车辆</h2>
    <el-button type="primary" @click="navigateTo('/dashboard/customer/cars/add')">添加新车</el-button>
    <el-table :data="cars" style="width: 100%" v-loading="loading">
      <el-table-column prop="license" label="车牌号" />
      <el-table-column prop="brand" label="品牌" />
      <el-table-column prop="model" label="型号" />
      <el-table-column label="操作">
        <template #default="scope">
          <el-button @click="navigateTo(`/dashboard/customer/cars/${scope.row.id}`)">详情</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/authStore'

const router = useRouter()
const authStore = useAuthStore()
const cars = ref([])
const loading = ref(true)

const navigateTo = (path) => {
  router.push(path)
}

onMounted(async () => {
  try {
    // TODO: 调用后端API获取车辆列表
    cars.value = [
      { id: 1, license: '沪A12345', brand: '丰田', model: '凯美瑞' },
      { id: 2, license: '沪B67890', brand: '本田', model: '雅阁' }
    ]
  } catch (error) {
    console.error('获取车辆列表失败:', error)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.car-management {
  padding: 20px;
}
</style>