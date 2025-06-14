<template>
    <div class="maintenance-history">
      <div class="header-with-back">
        <el-button icon="el-icon-arrow-left" @click="goBack">返回</el-button>
        <h2>维护历史 - {{ carId }}</h2>
      </div>
      
      <el-table :data="history" style="width: 100%" v-loading="loading">
        <el-table-column prop="date" label="日期" width="120" />
        <el-table-column prop="service_type" label="服务类型" />
        <el-table-column prop="description" label="描述" />
        <el-table-column prop="cost" label="费用" width="100" align="right" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="statusTagType(scope.row.status)">
              {{ scope.row.status }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
      
      <el-pagination
        background
        layout="prev, pager, next"
        :total="totalItems"
        :page-size="pageSize"
        :current-page="currentPage"
        @current-change="handlePageChange"
        class="pagination"
      />
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted, computed } from 'vue'
  import { useRoute, useRouter } from 'vue-router'
  import { ElMessage } from 'element-plus'
  import carsAPI from '@/api/cars'
  
  const route = useRoute()
  const router = useRouter()
  const history = ref([])
  const loading = ref(true)
  const currentPage = ref(1)
  const pageSize = ref(10)
  const totalItems = ref(0)
  
  const carId = computed(() => route.params.id)
  
  const goBack = () => {
    router.go(-1)
  }
  
  const statusTagType = (status) => {
    switch (status) {
      case '已完成': return 'success'
      case '进行中': return 'primary'
      case '待处理': return 'warning'
      default: return 'info'
    }
  }
  
  const fetchMaintenanceHistory = async () => {
    try {
      loading.value = true
      const params = {
        page: currentPage.value,
        page_size: pageSize.value
      }
      
      // 调用API获取维护历史
      const response = await carsAPI.getMaintenanceHistory(carId.value, params)
      history.value = response.data.items || []
      totalItems.value = response.data.total || 0
    } catch (error) {
      ElMessage.error('获取维护历史失败: ' + error.message)
    } finally {
      loading.value = false
    }
  }
  
  const handlePageChange = (page) => {
    currentPage.value = page
    fetchMaintenanceHistory()
  }
  
  onMounted(() => {
    fetchMaintenanceHistory()
  })
  </script>
  
  <style scoped>
  .maintenance-history {
    padding: 20px;
  }
  
  .header-with-back {
    display: flex;
    align-items: center;
    margin-bottom: 20px;
    
    .el-button {
      margin-right: 15px;
    }
    
    h2 {
      margin: 0;
    }
  }
  
  .pagination {
    margin-top: 20px;
    justify-content: flex-end;
  }
  </style>