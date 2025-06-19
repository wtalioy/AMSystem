<template>
  <div class="order-management">
    <div class="filter-container">
      <el-select 
        v-model="filterStatus"
        placeholder="筛选状态"
        @change="fetchOrders"
        style="width: 200px; margin-right: 15px"
      >
        <el-option
          v-for="status in statusOptions"
          :key="status.value"
          :label="status.label"
          :value="status.value"
        />
      </el-select>
    </div>

    <el-table 
      :data="orderList" 
      v-loading="loading"
      style="width: 100%; margin-top: 20px"
    >
      <el-table-column prop="order_id" label="订单号" width="180" />
      <el-table-column prop="car_id" label="车牌号" width="150" />
      <el-table-column prop="displayStatus" label="状态" width="120">
        <template #default="scope">
          <el-tag :type="statusTagType(scope.row.displayStatus)">
            {{ scope.row.displayStatus }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="create_time" label="创建时间" width="180">
        <template #default="scope">
          {{ formatTime(scope.row.create_time) }}
        </template>
      </el-table-column>
      <el-table-column label="查看进度" width="120">
        <template #default="scope">
          <el-button
            type="primary"
            size="small"
            @click="handleViewProgress(scope.row.order_id)"
          >
            查看进度
          </el-button>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="220">
        <template #default="scope">
          <el-button
            v-if="scope.row.displayStatus === 'pending'"
            type="warning"
            size="small"
            @click="handleUrgent(scope.row.order_id)"
          >
            加急
          </el-button>
          <el-button
            v-if="['pending', 'processing'].includes(scope.row.displayStatus)"
            type="danger"
            size="small"
            @click="handleCancel(scope.row.order_id)"
          >
            取消
          </el-button>

          <!-- 新增反馈按钮 -->
        <el-button
          v-if="scope.row.displayStatus === 'completed'"
          type="success"
          size="small"
          @click="handleFeedback(scope.row.order_id)"
        >
          我要反馈
        </el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-pagination
      background
      layout="prev, pager, next"
      :total="total"
      :page-size="pageSize"
      @current-change="handlePageChange"
      style="margin-top: 20px"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import dayjs from 'dayjs'
import ordersAPI from '@/api/orders'
import { useRouter } from 'vue-router'

const router = useRouter()
const orderList = ref([])
const loading = ref(true)
const total = ref(0)
const pageSize = ref(10)
const currentPage = ref(1)
const filterStatus = ref('all')

// 添加状态映射关系
const statusMap = {
  pending: 0,
  distributed: 1,
  processing: 2,
  completed: 3,
  cancelled: 4
}

// 反向映射用于显示
const reverseStatusMap = {
  0: 'pending',
  1: 'distributed',
  2: 'processing',
  3: 'completed',
  4: 'cancelled'
}

const statusOptions = [
  { value: 'all', label: '全部状态' },
  { value: 'pending', label: '待处理' },
  { value: 'distributed', label: '已分配'},
  { value: 'processing', label: '处理中' },
  { value: 'completed', label: '已完成' },
  { value: 'cancelled', label: '已取消' }
]

const statusTagType = (status) => {
  const types = {
    pending: 'warning',
    distributed: 'pending',
    processing: 'primary',
    completed: 'success',
    cancelled: 'info'
  }
  return types[status] || ''
}

const formatTime = (time) => {
  return dayjs(time).format('YYYY-MM-DD HH:mm')
}

const fetchOrders = async () => {
  try {
    loading.value = true
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      status_filter: filterStatus.value === 'all' ? undefined : statusMap[filterStatus.value]
    }
    
    const response = await ordersAPI.getOrders(params)
    // 添加状态映射转换
orderList.value = response.data.map(order => ({
  ...order,
  displayStatus: reverseStatusMap[order.status] || 'unknown'
}))
    total.value = response.data.length
  } catch (error) {
    ElMessage.error('获取订单列表失败')
  } finally {
    loading.value = false
  }
}

const handlePageChange = (page) => {
  currentPage.value = page
  fetchOrders()
}

const handleUrgent = async (orderId) => {
  try {
    await ElMessageBox.confirm('确认要加急此订单吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await ordersAPI.expediteOrder(orderId)
    ElMessage.success('订单已加急')
    fetchOrders()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('操作失败')
    }
  }
}

const handleCancel = async (orderId) => {
  try {
    await ElMessageBox.confirm('确认要取消此订单吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await ordersAPI.cancelOrder(orderId)
    ElMessage.success('订单已取消')
    fetchOrders()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('取消失败')
    }
  }
}

// 在脚本中添加handleFeedback方法
const handleFeedback = (orderId) => {
  router.push(`/dashboard/customer/orders/${orderId}/feedback`)
}

const handleViewProgress = (orderId) => {
  router.push(`/dashboard/customer/orders/${orderId}/procedures`)
}
onMounted(() => {
  fetchOrders()
})
</script>

<style scoped>
.order-management {
  padding: 20px;
}
.filter-container {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
}
</style>