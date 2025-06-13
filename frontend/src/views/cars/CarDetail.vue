<template>
  <div class="car-detail">
    <h2>车辆详情</h2>
    
    <el-form 
      :model="form" 
      label-width="120px" 
      label-position="left"
      v-loading="loading"
    >
      <el-form-item label="车牌号">
        <el-input v-model="form.car_id" disabled />
      </el-form-item>
      
      <el-form-item label="车辆类型">
        <el-select 
          v-model="form.car_type" 
          placeholder="请选择车辆类型"
          filterable
          style="width: 100%"
        >
          <el-option
            v-for="type in carTypes"
            :key="type"
            :label="type"
            :value="type"
          />
        </el-select>
      </el-form-item>
      
      <el-form-item label="维护历史">
        <el-button type="text" @click="viewMaintenanceHistory">
          查看维护历史记录
        </el-button>
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
import { ElMessage } from 'element-plus'
import cars from '@/api/cars'

const route = useRoute()
const router = useRouter()
const form = ref({
  car_id: '',
  car_type: ''
})
const carTypes = ref([])
const loading = ref(true)

const navigateTo = (path) => {
  router.push(path)
}

// 查看维护历史
const viewMaintenanceHistory = () => {
  router.push(`/dashboard/customer/cars/${route.params.id}/maintenance-history`)
}

// 获取车辆详情
const fetchCarDetail = async () => {
  try {
    loading.value = true
    const carId = route.params.id
    const response = await cars.getCarDetail(carId)
    form.value = response.data
  } catch (error) {
    ElMessage.error('获取车辆详情失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

// 获取车辆类型列表
const fetchCarTypes = async () => {
  try {
    const response = await cars.getCarTypes()
    carTypes.value = response.data
  } catch (error) {
    ElMessage.error('获取车辆类型失败: ' + error.message)
  }
}

// 保存修改
const handleSave = async () => {
  try {
    loading.value = true
    await cars.updateCar(form.value.car_id, {
      car_type: form.value.car_type
    })
    ElMessage.success('车辆信息更新成功')
    navigateTo('/dashboard/customer/cars')
  } catch (error) {
    ElMessage.error('保存失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await fetchCarTypes()
  await fetchCarDetail()
})
</script>

<style scoped>
.car-detail {
  padding: 20px;
  max-width: 600px;
}
</style>