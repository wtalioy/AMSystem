<template>
  <div class="order-create">
    <h2>新建维修订单</h2>
    <el-form :model="form" label-width="120px" ref="formRef">
      <el-form-item label="选择车辆" required>
        <el-select v-model="form.car_id" placeholder="请选择车辆">
          <el-option
            v-for="car in cars"
            :key="car.id"
            :label="car.license"
            :value="car.id"
          />
        </el-select>
      </el-form-item>

      <el-form-item label="预约时间" required>
        <el-date-picker
          v-model="form.appointment"
          type="datetime"
          placeholder="填写预约时间"
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
import ordersApi from '@/api/orders'  // 新增API导入
import { ElMessage } from 'element-plus'  // 新增消息提示
import carsAPI from '@/api/cars'  // 新增导入

// ... 已有代码保持不变 ...

const router = useRouter()
const loading = ref(true)
const authStore = useAuthStore()
const cars = ref([])
const form = ref({
  car_id: null,
  appointment: null,
  description: ''
})


const submitForm = async () => {
  try {
    const payload = {
      car_id: form.value.car_id,
      description: form.value.description,
      start_time: form.value.appointment
    }

    await ordersApi.createOrder(payload)
    ElMessage.success('订单创建成功')
    router.push('/dashboard/customer/orders') // 或你跳转的目标页
  } catch (error) {
    console.error('订单创建失败:', error)
    ElMessage.error('订单创建失败，请检查输入信息')
  }
}

//获取车辆信息
const fetchCars = async () => {
  try {
    loading.value = true
    // 更规范的响应解构（假设接口返回分页数据）
    const response = await carsAPI.getCars()
    
    // 根据接口实际返回结构调整（假设返回 data.data）
    cars.value = response.data.data || []
  } catch (error) {
    ElMessage.error({
      message: '加载失败: ' + (error.response?.data?.detail || error.message),
      duration: 3000
    })
  } finally {
    loading.value = false
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