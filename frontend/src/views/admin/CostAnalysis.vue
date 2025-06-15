<template>
  <div class="cost-analysis">
    <h2>维修成本分析</h2>
    
    <!-- 总体成本统计 -->
    <div class="overview">
      <el-card shadow="hover">
        <div class="overview-item">
          <div class="overview-label">分析时段</div>
          <div class="overview-value">{{ summary.period_start }} 至 {{ summary.period_end }}</div>
        </div>
        
        <el-row :gutter="20">
          <el-col :span="8">
            <div class="overview-item">
              <div class="overview-label">总材料成本</div>
              <div class="overview-value">{{ formatCost(summary.total_material_cost) }}</div>
            </div>
          </el-col>
          
          <el-col :span="8">
            <div class="overview-item">
              <div class="overview-label">总人工成本</div>
              <div class="overview-value">{{ formatCost(summary.total_labor_cost) }}</div>
            </div>
          </el-col>
          
          <el-col :span="8">
            <div class="overview-item">
              <div class="overview-label">总成本</div>
              <div class="overview-value">{{ formatCost(summary.total_cost) }}</div>
            </div>
          </el-col>
        </el-row>
        
        <div class="overview-item">
          <div class="overview-label">人工材料比</div>
          <div class="overview-value">{{ (summary.labor_material_ratio * 100).toFixed(2) }}%</div>
        </div>
      </el-card>
    </div>
    
    <!-- 按时间段分解的成本详情 -->
    <h3>按{{ periodTypeLabel }}分解</h3>
    <el-table :data="costs" style="width: 100%" v-loading="loading">
      <el-table-column prop="period" label="时间段" />
      <el-table-column label="材料成本">
        <template #default="{ row }">
          {{ formatCost(row.material_cost) }}
        </template>
      </el-table-column>
      <el-table-column label="人工成本">
        <template #default="{ row }">
          {{ formatCost(row.labor_cost) }}
        </template>
      </el-table-column>
      <el-table-column label="总成本">
        <template #default="{ row }">
          {{ formatCost(row.total_cost) }}
        </template>
      </el-table-column>
      <el-table-column label="人工材料比">
        <template #default="{ row }">
          {{ (row.labor_material_ratio * 100).toFixed(2) }}%
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import costAPI from '@/api/adminStats'

// 数据状态
const summary = ref({
  period_start: '',
  period_end: '',
  total_material_cost: '0',
  total_labor_cost: '0',
  total_cost: '0',
  labor_material_ratio: 0
})
const costs = ref([])
const loading = ref(false)
const periodTypeLabel = ref('月') // 默认按月分解

// 货币格式化函数
const formatCost = (cost) => {
  if (!cost) return '¥0.00'
  if (cost.startsWith('¥')) return cost
  const number = parseFloat(cost)
  return isNaN(number) ? cost : `¥${number.toFixed(2)}`
}

// 获取成本分析数据
const fetchCostAnalysis = async () => {
  try {
    loading.value = true
    
    // 设置时间范围 - 这里使用最近一年的数据
    const today = new Date()
    const endDate = today.toISOString().split('T')[0]
    
    const oneYearAgo = new Date()
    oneYearAgo.setFullYear(today.getFullYear() - 1)
    const startDate = oneYearAgo.toISOString().split('T')[0]
    
    const res = await costAPI.getCostAnalysis({
      start_date: startDate,
      end_date: endDate,
      period_type: 'month' // 按月分解
    })
    
    // 更新数据
    if (res.data) {
      summary.value = {
        period_start: res.data.period_start,
        period_end: res.data.period_end,
        total_material_cost: res.data.total_material_cost,
        total_labor_cost: res.data.total_labor_cost,
        total_cost: res.data.total_cost,
        labor_material_ratio: res.data.labor_material_ratio
      }
      
      costs.value = res.data.period_breakdown || []
      
      // 根据周期类型设置标签
      periodTypeLabel.value = res.config.params.period_type === 'quarter' ? '季度' : '月'
    }
    
    console.log('成本分析数据:', res.data)
  } catch (error) {
    console.error('获取成本分析失败:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchCostAnalysis()
})
</script>

<style scoped>
.cost-analysis {
  padding: 20px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.overview {
  margin-bottom: 24px;
}

.overview-item {
  margin-bottom: 16px;
}

.overview-label {
  font-size: 14px;
  color: #606266;
  margin-bottom: 4px;
}

.overview-value {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

h2, h3 {
  margin-bottom: 20px;
  color: #333;
  font-weight: 600;
}

h3 {
  margin-top: 24px;
  margin-bottom: 16px;
}
</style>