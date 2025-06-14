<template>
  <div class="car-management">
    <div class="header-with-actions">
      <h2>我的车辆</h2>
      <el-button 
        type="primary" 
        icon="el-icon-plus" 
        @click="navigateTo('/dashboard/customer/cars/add')"
      >
        添加新车
      </el-button>
    </div>
    
    <el-table 
      :data="carList" 
      style="width: 100%" 
      v-loading="loading"
      empty-text="暂无车辆数据，点击按钮添加新车"
    >
      <el-table-column prop="car_id" label="车牌号" width="150" />
      <el-table-column prop="car_type" label="车辆类型" />
      <el-table-column label="操作" width="180">
        <template #default="scope">
          <el-button 
            size="small" 
            @click="navigateTo(`/dashboard/customer/cars/${scope.row.car_id}`)"
          >
            详情
          </el-button>
          <el-button 
            size="small" 
            type="danger" 
            @click="handleDelete(scope.row.car_id)"
          >
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import carAPI from '@/api/cars'

const router = useRouter()
const carList = ref([])
const loading = ref(true)

const navigateTo = (path) => {
  router.push(path)
}

const fetchCars = async () => {
  try {
    loading.value = true
    const { data } = await carAPI.getCars()
    carList.value = data
  } catch (error) {
    ElMessage.error({
      message: '加载车辆失败: ' + error.response?.data?.detail || error.message,
      duration: 3000
    })
  } finally {
    loading.value = false
  }
}

const handleDelete = async (carId) => {
  try {
    await ElMessageBox.confirm('此操作将永久删除该车辆，是否继续？', '警告', {
      confirmButtonText: '确认',
      cancelButtonText: '取消',
      type: 'warning',
      distinguishCancelAndClose: true
    })

    await carAPI.deleteCar(carId)
    ElMessage.success('车辆删除成功')
    await fetchCars()
  } catch (error) {
    if (error === 'cancel') {
      ElMessage.info('已取消删除')
    } else {
      ElMessage.error(`删除失败: ${error.message}`)
    }
  }
}

onMounted(() => {
  fetchCars()
})
</script>

<style scoped>
.car-management {
  padding: 20px;
}

.header-with-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
</style>