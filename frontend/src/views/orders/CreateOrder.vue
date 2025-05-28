<template>
  <div class="order-create">
    <h2>新建维修订单</h2>
    <el-form :model="form" label-width="120px" ref="formRef">
      <el-form-item label="选择车辆" required>
        <el-select v-model="form.carId" placeholder="请选择车辆">
          <el-option
            v-for="car in cars"
            :key="car.id"
            :label="car.license"
            :value="car.id"
          />
        </el-select>
      </el-form-item>

      <el-form-item label="服务类型" required>
        <el-checkbox-group v-model="form.services">
          <el-checkbox label="保养"></el-checkbox>
          <el-checkbox label="维修"></el-checkbox>
          <el-checkbox label="检测"></el-checkbox>
        </el-checkbox-group>
      </el-form-item>

      <el-form-item label="预约时间" required>
        <el-date-picker
          v-model="form.appointment"
          type="datetime"
          placeholder="选择预约时间"
        />
      </el-form-item>

      <el-form-item label="问题描述">
        <el-input
          v-model="form.description"
          type="textarea"
          :rows="4"
          placeholder="请详细描述车辆问题"
        />
      </el-form-item>

      <el-form-item>
        <el-button type="primary" @click="submitForm">提交订单</el-button>
        <el-button @click="resetForm">重置</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/authStore'

const router = useRouter()
const authStore = useAuthStore()
const cars = ref([])
const form = ref({
  carId: null,
  services: [],
  appointment: null,
  description: ''
})

const fetchCars = async () => {
  try {
    // TODO: 调用API获取用户车辆列表
    cars.value = [
      { id: 1, license: '沪A12345' },
      { id: 2, license: '沪B67890' }
    ]
  } catch (error) {
    console.error('获取车辆列表失败:', error)
  }
}

const submitForm = async () => {
  try {
    // TODO: 调用API创建订单
    console.log('提交订单:', form.value)
    router.push('/dashboard/customer')
  } catch (error) {
    console.error('订单创建失败:', error)
  }
}

const resetForm = () => {
  form.value = {
    carId: null,
    services: [],
    appointment: null,
    description: ''
  }
}

onMounted(() => {
  fetchCars()
})
</script>

<style scoped>
.order-create {
  padding: 20px;
  max-width: 800px;
}
</style>