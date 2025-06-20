<template>
  <div class="earnings-history">
    <h2>收入历史记录</h2>
    
    <!-- 月份选择器 -->
    <div class="filter-container">
      <el-select 
        v-model="monthsBack" 
        placeholder="选择查询月份范围"
        @change="fetchHistory"
        style="width: 200px; margin-bottom: 20px;"
      >
        <el-option
          v-for="item in monthOptions"
          :key="item.value"
          :label="item.label"
          :value="item.value"
        />
      </el-select>
    </div>

    <!-- 数据表格 -->
    <el-table 
      :data="records" 
      style="width: 100%"
      v-loading="loading"
      element-loading-text="数据加载中..."
      stripe
    >
      <el-table-column label="月份" width="120">
        <template #default="{ row }">
          {{ formatPeriod(row.period) }}
        </template>
      </el-table-column>
      
      <el-table-column label="日期范围" width="180">
        <template #default="{ row }">
          {{ formatDate(row.period.start_date) }} 至 {{ formatDate(row.period.end_date) }}
        </template>
      </el-table-column>
      
      <el-table-column prop="work_summary.total_orders" label="订单数量" align="center" />
      
      <el-table-column label="工作时长(h)" align="center">
        <template #default="{ row }">
          {{ row.work_summary.total_hours.toFixed(1) }}
        </template>
      </el-table-column>
      
      <el-table-column label="时薪(¥)" align="center">
        <template #default="{ row }">
          {{ row.work_summary.hourly_rate.toFixed(2) }}
        </template>
      </el-table-column>
      
      <el-table-column label="平均评分" align="center">
        <template #default="{ row }">
          <el-rate 
            v-model="row.work_summary.average_rating" 
            disabled 
            :max="5"
            show-score
            :score-template="`${row.work_summary.average_rating}`"
          />
        </template>
      </el-table-column>
      
      <el-table-column label="基础收入(¥)" align="center">
        <template #default="{ row }">
          {{ row.earnings.base_earnings.toFixed(2) }}
        </template>
      </el-table-column>
      
      <el-table-column label="绩效奖金(¥)" align="center">
        <template #default="{ row }">
          <span style="color: #67C23A;">
            + {{ row.earnings.performance_bonus.toFixed(2) }}
          </span>
        </template>
      </el-table-column>
      
      <el-table-column label="总收入(¥)" align="center" header-align="center">
        <template #default="{ row }">
          <strong style="font-size: 1.1em;">
            {{ row.earnings.total_earnings.toFixed(2) }}
          </strong>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import workerOrdersAPI from '@/api/workerOrders'
import { ElMessage } from 'element-plus'

const records = ref([])
const loading = ref(false)
const monthsBack = ref(12) // 默认查询12个月

// 月份范围选项 - 严格符合接口要求(1-24)
const monthOptions = Array.from({ length: 24 }, (_, i) => {
  const value = i + 1
  return { value, label: `最近${value}个月` }
})

// 格式化日期显示 (YYYY-MM-DD)
const formatDate = (dateStr) => {
  return dateStr ? dateStr.substring(0, 10) : ''
}

// 格式化年月显示
const formatPeriod = (period) => {
  return period ? `${period.year}-${period.month.toString().padStart(2, '0')}` : ''
}

// 获取收入历史
// 修复的核心部分
const fetchHistory = async () => {
  loading.value = true
  records.value = []
  
  try {
    const params = { 
      months_back: Math.min(24, Math.max(1, parseInt(monthsBack.value) || 12))
    }
    
    // 正确获取API响应数据
    const response = await workerOrdersAPI.getEarningsHistory(params)
    
    // 确保处理的是响应数据而不是响应对象
    const data = Array.isArray(response) ? response : response.data
    
    // 安全排序 - 添加空值检查
    records.value = (data || []).sort((a, b) => {
      // 确保period对象存在
      if (!a.period || !b.period) return 0
      
      const dateA = a.period.start_date ? new Date(a.period.start_date) : new Date(0)
      const dateB = b.period.start_date ? new Date(b.period.start_date) : new Date(0)
      
      return dateB - dateA
    })
    console.log(records.value)
    
  } catch (error) {
    handleApiError(error)
  } finally {
    loading.value = false
  }
}

// 处理API错误
const handleApiError = (error) => {
  let errorMessage = '获取收入历史失败'
  
  // 处理422验证错误
  if (error.response?.status === 422) {
    const details = error.response.data.detail
    const firstError = details[0]?.msg || '参数错误'
    errorMessage = `请求参数错误: ${firstError}`
  } 
  // 处理其他HTTP错误
  else if (error.response?.data?.message) {
    errorMessage = error.response.data.message
  }
  // 处理网络错误
  else if (!error.response) {
    errorMessage = '网络连接异常，请检查网络设置'
  }
  
  ElMessage.error(errorMessage)
  
  // 开发环境打印完整错误
  if (process.env.NODE_ENV === 'development') {
    console.error('API Error Details:', error)
  }
}

onMounted(fetchHistory)
</script>

<style scoped>
.earnings-history {
  padding: 20px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.filter-container {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 15px;
}

h2 {
  margin-bottom: 20px;
  color: #303133;
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
}

:deep(.el-table__row) {
  transition: background-color 0.3s;
}

:deep(.el-table__row:hover) {
  background-color: #f5f7fa !important;
}
</style>