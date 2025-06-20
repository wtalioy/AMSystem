<template>
  <div class="order-management">
    <div class="filter-container">
      <!-- 状态筛选器，改为仅修改filterStatus，不触发fetchOrders -->
      <el-select 
        v-model="filterStatus"
        placeholder="筛选状态"
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

    <!-- 表格：绑定 paginatedOrders（前端分页后的订单） -->
    <el-table 
      :data="paginatedOrders" 
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
      <el-table-column prop="start_time" label="开始时间" width="180">
        <template #default="scope">
          {{ formatTime(scope.row.start_time) }}
        </template>
      </el-table-column>
      <el-table-column prop="end_time" label="结束时间" width="180">
        <template #default="scope">
          {{ scope.row.end_time ? formatTime(scope.row.end_time) : '' }}
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
            v-if="['pending', 'distributed'].includes(scope.row.displayStatus)"
            type="warning"
            size="small"
            @click="handleUrgent(scope.row.order_id)"
          >
            加急
          </el-button>
          <el-button
            v-if="['pending', 'distributed'].includes(scope.row.displayStatus)"
            type="danger"
            size="small"
            @click="handleCancel(scope.row.order_id)"
          >
            取消
          </el-button>
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

    <!-- 分页器：绑定当前页与数据长度 -->
    <el-pagination
      background
      layout="prev, pager, next"
      :total="filteredOrders.length"
      :page-size="pageSize"
      @current-change="handlePageChange"
      style="margin-top: 20px"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import dayjs from 'dayjs'
import ordersAPI from '@/api/orders'
import { useRouter } from 'vue-router'

const router = useRouter()

// 全部订单数据（原始数据）
const allOrders = ref([])

// 当前页和分页配置
const currentPage = ref(1)
const pageSize = ref(10)

// 加载状态
const loading = ref(true)

// 当前筛选的状态
const filterStatus = ref('all')

// 显示用的状态映射
const statusMap = {
  pending: 0,
  distributed: 1,
  processing: 2,
  completed: 3,
  cancelled: 4
}

// 用于显示的状态反向映射
const reverseStatusMap = {
  0: 'pending',
  1: 'distributed',
  2: 'processing',
  3: 'completed',
  4: 'cancelled'
}

// 状态筛选选项
const statusOptions = [
  { value: 'all', label: '全部状态' },
  { value: 'pending', label: '待处理' },
  { value: 'distributed', label: '待接单'},
  { value: 'processing', label: '处理中' },
  { value: 'completed', label: '已完成' },
  { value: 'cancelled', label: '已取消' }
]

// 计算属性：根据筛选状态得到对应订单列表
const filteredOrders = computed(() => {
  if (filterStatus.value === 'all') return allOrders.value
  const targetStatus = statusMap[filterStatus.value]
  return allOrders.value.filter(order => order.status === targetStatus)
})

// 计算属性：分页后的订单数据
const paginatedOrders = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredOrders.value.slice(start, end)
})

// 获取订单数据（只请求一次，取全量数据）
const fetchOrders = async () => {
  try {
    loading.value = true
    const params = {
      page: 1,
      page_size: 100  // 假设最多1000条，确保能一次性拿完
    }

    const response = await ordersAPI.getOrders(params)

    // 添加 displayStatus 字段，便于前端展示
    const ordersWithDisplayStatus = response.data.map(order => ({
      ...order,
      displayStatus: reverseStatusMap[order.status] || 'unknown'
    }))

    allOrders.value = ordersWithDisplayStatus.sort((a, b) => a.status - b.status)
  } catch (error) {
    ElMessage.error('获取订单列表失败')
  } finally {
    loading.value = false
  }
}

// 分页事件：更新页码
const handlePageChange = (page) => {
  currentPage.value = page
}

// 订单操作：加急
const handleUrgent = async (orderId) => {
  try {
    await ElMessageBox.confirm('确认要加急此订单吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await ordersAPI.expediteOrder(orderId)
    ElMessage.success('订单已加急')
    await fetchOrders()  // 重新拉取数据
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('操作失败')
    }
  }
}

// 订单操作：取消
const handleCancel = async (orderId) => {
  try {
    await ElMessageBox.confirm('确认要取消此订单吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await ordersAPI.cancelOrder(orderId)
    ElMessage.success('订单已取消')
    await fetchOrders()  // 重新拉取数据
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('取消失败')
    }
  }
}

// 跳转到反馈页面
const handleFeedback = (orderId) => {
  router.push(`/dashboard/customer/orders/${orderId}/feedback`)
}

// 跳转到查看进度页面
const handleViewProgress = (orderId) => {
  router.push(`/dashboard/customer/orders/${orderId}/procedures`)
}

// 工具函数：格式化时间
const formatTime = (time) => {
  return dayjs(time).format('YYYY-MM-DD HH:mm')
}

// 工具函数：状态颜色标签
const statusTagType = (status) => {
  const types = {
    pending: 'warning',
    distributed: 'primary',
    processing: 'primary',
    completed: 'success',
    cancelled: 'info'
  }
  return types[status] || ''
}

// 页面初始化时获取数据
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
