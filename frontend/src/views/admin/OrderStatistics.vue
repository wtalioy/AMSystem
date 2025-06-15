<template>
  <div class="order-statistics">
    <h2>订单管理</h2>
    
    <!-- 添加分页控件 -->
    <div class="pagination">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="totalOrders"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="fetchOrders"
        @current-change="fetchOrders"
      />
    </div>
    
    <el-table :data="orders" style="width: 100%" v-loading="loading">
      <!-- 订单基本信息 -->
      <el-table-column prop="order_id" label="订单ID" width="200" />
      <el-table-column prop="description" label="描述" />
      
      <!-- 时间信息 -->
      <el-table-column label="开始时间" width="180">
        <template #default="{ row }">
          {{ formatDateTime(row.start_time) }}
        </template>
      </el-table-column>
      
      <el-table-column label="结束时间" width="180">
        <template #default="{ row }">
          {{ formatDateTime(row.end_time) }}
        </template>
      </el-table-column>
      
      <!-- 状态信息 -->
      <el-table-column prop="status" label="状态">
        <template #default="{ row }">
          <el-tag :type="getStatusType(row.status)">
            {{ getStatusText(row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      
      <!-- 客户和工人信息 -->
      <el-table-column prop="customer_id" label="客户ID" width="120" />
      <el-table-column prop="worker_id" label="工人ID" width="120" />
      
      <!-- 财务信息 -->
      <el-table-column label="总成本" align="right" width="120">
        <template #default="{ row }">
          {{ formatCost(row.total_cost) }}
        </template>
      </el-table-column>
      
      <!-- 其他信息 -->
      <el-table-column label="加急" width="80">
        <template #default="{ row }">
          <el-icon v-if="row.expedite_flag" color="red">
            <Check />
          </el-icon>
          <span v-else>-</span>
        </template>
      </el-table-column>
      
      <el-table-column prop="assignment_attempts" label="分配尝试" width="100" align="center" />
      
      <el-table-column label="最后分配时间" width="180">
        <template #default="{ row }">
          {{ formatDateTime(row.last_assignment_at) }}
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Check } from '@element-plus/icons-vue'
import statsAPI from '@/api/adminStats'

const orders = ref([])
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(20)
const totalOrders = ref(0)

// 货币格式化函数
const formatCost = (cost) => {
  if (!cost) return '¥0.00'
  if (cost.startsWith('¥')) return cost
  const number = parseFloat(cost)
  return isNaN(number) ? cost : `¥${number.toFixed(2)}`
}

// 日期时间格式化
const formatDateTime = (dateString) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleString()
}

// 状态码转文本
const getStatusText = (statusCode) => {
  const statusMap = {
    0: '待处理',
    1: '进行中',
    2: '已完成',
    3: '已取消'
    // 添加更多状态映射
  }
  return statusMap[statusCode] || `状态${statusCode}`
}

// 状态标签类型
const getStatusType = (status) => {
  const typeMap = {
    0: 'warning',   // 待处理 - 黄色
    1: 'primary',   // 进行中 - 蓝色
    2: 'success',   // 已完成 - 绿色
    3: 'danger'     // 已取消 - 红色
  }
  return typeMap[status] || 'info'
}

// 获取订单数据
const fetchOrders = async () => {
  try {
    loading.value = true
    const res = await statsAPI.getOrderStatistics({
      page: currentPage.value,
      page_size: pageSize.value
    })
    
    // 更新订单数据和总数
    orders.value = res.data || []
    
    // 如果后端返回了总数，可以设置 totalOrders.value = res.total
    // 否则可以设置为 orders.value.length
    totalOrders.value = orders.value.length
    
    console.log('获取到的订单数据:', orders.value)
  } catch (error) {
    console.error('获取订单失败:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchOrders()
})
</script>

<style scoped>
.order-statistics {
  padding: 20px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

h2 {
  margin-bottom: 20px;
  color: #333;
  font-weight: 600;
}

.pagination {
  margin-bottom: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>