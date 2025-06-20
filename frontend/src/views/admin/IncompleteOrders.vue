<template>
  <div>
    <h2>未完成订单分析</h2>
    <el-table :data="orders" style="width: 100%" class="incomplete-orders-table">
      <el-table-column prop="order_id" label="订单号" width="180" />
      <el-table-column prop="car_id" label="车辆ID" />
      <el-table-column prop="car_type" label="车辆类型" />
      <el-table-column prop="description" label="订单描述" />
      <el-table-column label="开始时间">
        <template #default="scope">
          {{ formatDate(scope.row.start_time) }}
        </template>
      </el-table-column>
      <el-table-column label="订单进度" width="150">
        <template #default="scope">
          <el-progress 
            :percentage="calculateProgress(scope.row)" 
            :status="getProgressStatus(scope.row)"
            :show-text="false"
          />
          <span style="font-size: 12px">
            {{ scope.row.completed_procedures }}/{{ scope.row.procedures_count }}
          </span>
        </template>
      </el-table-column>
      <el-table-column label="状态">
        <template #default="scope">
          <el-tag :type="getStatusType(scope.row.status)">
            {{ getStatusText(scope.row.status) }}
          </el-tag>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import orderAPI from '@/api/adminStats'
import dayjs from 'dayjs' // 使用dayjs进行日期格式化

const orders = ref([])

onMounted(async () => {
  try {
    const res = await orderAPI.getIncompleteOrders()
    orders.value = res.data || []
  } catch (error) {
    console.error('获取未完成订单失败:', error)
    ElMessage.error('获取未完成订单数据失败')
  }
})

// 格式化日期
const formatDate = (dateString) => {
  return dayjs(dateString).format('YYYY-MM-DD HH:mm')
}

// 计算进度百分比
const calculateProgress = (order) => {
  if (order.procedures_count === 0) return 0
  return Math.round((order.completed_procedures / order.procedures_count) * 100)
}

// 获取进度条状态
const getProgressStatus = (order) => {
  const progress = calculateProgress(order)
  if (progress === 0) return 'exception'
  if (progress < 50) return 'warning'
  if (progress < 100) return ''
  return 'success'
}

// 状态文本映射
const getStatusText = (statusCode) => {
  const statusMap = {
    1: '待接单',
    2: '进行中'
  }
  return statusMap[statusCode] || `未知状态 (${statusCode})`
}

// 状态标签类型映射
const getStatusType = (statusCode) => {
  const typeMap = {
    0: 'info',
    1: 'primary',
    2: 'warning',
    3: 'success',
  }
  return typeMap[statusCode] || 'danger'
}
</script>

<style scoped>
.incomplete-orders-table {
  margin-top: 20px;
}

.el-progress {
  margin-bottom: 5px;
}
</style>