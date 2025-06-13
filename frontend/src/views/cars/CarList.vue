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
    
    <el-table :data="carList" style="width: 100%" v-loading="loading">
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

    <!-- ✅ 添加 router-view 用于加载 add / :id 页面 -->
    <router-view></router-view>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import carAPI from '@/api/cars' // 假设有封装好的axios实例

const router = useRouter()
const carList = ref([])
const loading = ref(true)

const navigateTo = (path) => {
  router.push(path)
}

const fetchCars = async () => {
  try {
    loading.value = true
    // 调用API获取车辆列表
    const response = await carAPI.getCars()
    carList.value = response.data
  } catch (error) {
    ElMessage.error('获取车辆列表失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

const handleDelete = async (carId) => {
  try {
    await ElMessageBox.confirm('确定要删除这辆车吗？', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    // 调用API删除车辆
    await carAPI.deleteCar(carId)
    ElMessage.success('车辆删除成功')
    await fetchCars() // 重新加载列表
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败: ' + error.message)
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