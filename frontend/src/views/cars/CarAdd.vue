<template>
    <div class="car-add">
      <h2>添加新车</h2>
      
      <el-form 
        :model="form" 
        :rules="rules" 
        ref="carForm"
        label-width="120px" 
        label-position="left"
        v-loading="loading"
      >
        <el-form-item label="车牌号" prop="car_id">
          <el-input v-model="form.car_id" placeholder="请输入车牌号" />
        </el-form-item>
        
        <el-form-item label="车辆类型" prop="car_type">
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
        
        <el-form-item>
          <el-button type="primary" @click="submitForm">保存</el-button>
          <el-button @click="navigateTo('/dashboard/customer/cars')">取消</el-button>
        </el-form-item>
      </el-form>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted } from 'vue'
  import { useRouter } from 'vue-router'
  import { ElMessage } from 'element-plus'
  import { getCarTypes, createCar } from '@/api/cars'
  
  const router = useRouter()
  const carForm = ref(null)
  const form = ref({
    car_id: '',
    car_type: ''
  })
  const carTypes = ref([])
  const loading = ref(false)
  
  const rules = ref({
    car_id: [
      { required: true, message: '请输入车牌号', trigger: 'blur' },
      { min: 3, max: 15, message: '长度在 3 到 15 个字符', trigger: 'blur' }
    ],
    car_type: [
      { required: true, message: '请选择车辆类型', trigger: 'change' }
    ]
  })
  
  const navigateTo = (path) => {
    router.push(path)
  }
  
  // 获取车辆类型列表
  const fetchCarTypes = async () => {
    try {
      const response = await getCarTypes()
      carTypes.value = response.data
    } catch (error) {
      ElMessage.error('获取车辆类型失败: ' + error.message)
    }
  }
  
  // 提交表单
  const submitForm = async () => {
    try {
      await carForm.value.validate()
      loading.value = true
      
      // 调用API创建新车
      await createCar(form.value)
      ElMessage.success('车辆添加成功')
      navigateTo('/dashboard/customer/cars')
    } catch (error) {
      if (error !== 'cancel') {
        ElMessage.error('添加失败: ' + error.message)
      }
    } finally {
      loading.value = false
    }
  }
  
  onMounted(() => {
    fetchCarTypes()
  })
  </script>
  
  <style scoped>
  .car-add {
    padding: 20px;
    max-width: 600px;
  }
  </style>