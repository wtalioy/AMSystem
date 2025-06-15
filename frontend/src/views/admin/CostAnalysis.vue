<template>
  <div class="wage-management">
    <h2>工资管理</h2>
    
    <!-- 查询条件区域 -->
    <el-card shadow="hover" class="query-card">
      <div class="query-form">
        <div class="form-item">
          <span class="label">开始日期：</span>
          <el-date-picker
            v-model="queryParams.start_date"
            type="date"
            placeholder="选择开始日期"
            value-format="YYYY-MM-DD"
            :clearable="true"
          />
        </div>
        
        <div class="form-item">
          <span class="label">结束日期：</span>
          <el-date-picker
            v-model="queryParams.end_date"
            type="date"
            placeholder="选择结束日期"
            value-format="YYYY-MM-DD"
            :clearable="true"
          />
        </div>
        
        <div class="form-item">
  <span class="label">统计周期：</span>
  <el-select 
    v-model="queryParams.period_type" 
    placeholder="选择周期类型"
    style="width: 150px" 
  >
    <el-option 
      v-for="option in periodOptions"
      :key="option.value"
      :label="option.label"
      :value="option.value"
    >
      {{ option.label }} <!-- 这里确保显示文本 -->
    </el-option>
  </el-select>
</div>
        
        <el-button 
          type="primary" 
          @click="fetchData"
          :loading="loading"
        >
          查询
        </el-button>
        <el-button @click="resetQuery">
          重置
        </el-button>
      </div>
    </el-card>
    
    <!-- 数据表格区域 -->
    <el-card shadow="hover" class="data-card">
      <el-table :data="wages" v-loading="loading" style="width: 100%">
        <el-table-column prop="worker_id" label="工人ID" width="120" />
        <el-table-column prop="worker_name" label="姓名" width="150" />
        <el-table-column prop="period" label="统计周期" />
        <el-table-column prop="amount" label="工资" width="120">
          <template #default="{ row }">
            ¥{{ formatAmount(row.amount) }}
          </template>
        </el-table-column>
        <el-table-column prop="labor_cost" label="人工成本" width="150">
          <template #default="{ row }">
            ¥{{ formatAmount(row.labor_cost) }}
          </template>
        </el-table-column>
        <el-table-column prop="material_cost" label="材料成本" width="150">
          <template #default="{ row }">
            ¥{{ formatAmount(row.material_cost) }}
          </template>
        </el-table-column>
        <el-table-column prop="labor_material_ratio" label="人工材料比" width="150">
          <template #default="{ row }">
            {{ (row.labor_material_ratio * 100).toFixed(2) }}%
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 统计摘要 -->
      <div class="summary" v-if="wages.length > 0">
        <div class="summary-item">
          <span class="label">总成本：</span>
          <span class="value">¥{{ formatAmount(summary.total_cost) }}</span>
        </div>
        <div class="summary-item">
          <span class="label">人工成本：</span>
          <span class="value">¥{{ formatAmount(summary.total_labor_cost) }}</span>
        </div>
        <div class="summary-item">
          <span class="label">材料成本：</span>
          <span class="value">¥{{ formatAmount(summary.total_material_cost) }}</span>
        </div>
        <div class="summary-item">
          <span class="label">人工材料比：</span>
          <span class="value">{{ (summary.labor_material_ratio * 100).toFixed(2) }}%</span>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import wageAPI from '@/api/adminStats'
import { ElMessage } from 'element-plus'

// 查询参数
const queryParams = ref({
  start_date: null,
  end_date: null,
  period_type: 'month'
})

// 工资数据
const wages = ref([])

// 汇总数据
const summary = ref({
  total_cost: 0,
  total_labor_cost: 0,
  total_material_cost: 0,
  labor_material_ratio: 0
})

// 加载状态
const loading = ref(false)

// 获取默认日期范围（上个月）
const getDefaultDateRange = () => {
  const now = new Date()
  const lastMonth = new Date(now.getFullYear(), now.getMonth() - 1, 1)
  const end = new Date(now.getFullYear(), now.getMonth(), 0)
  
  return {
    start: formatDate(lastMonth),
    end: formatDate(end)
  }
}

// 日期格式化
const formatDate = (date) => {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

// 金额格式化
const formatAmount = (amount) => {
  return parseFloat(amount).toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',')
}

// 添加在 script setup 中
const periodOptions = ref([
  { label: '按月统计', value: 'month' },
  { label: '按季度统计', value: 'quarter' }
])

// 获取数据
const fetchData = async () => {
  try {
    loading.value = true
    
    const params = { 
      period_type: queryParams.value.period_type 
    }
    
    // 添加日期参数（如果存在）
    if (queryParams.value.start_date) {
      params.start_date = queryParams.value.start_date
    }
    
    if (queryParams.value.end_date) {
      params.end_date = queryParams.value.end_date
    }
    
    const res = await wageAPI.getCostAnalysis(params)
    
    // 处理返回数据
    wages.value = res.data.period_breakdown.map(item => ({
      period: item.period,
      amount: item.total_cost,
      labor_cost: item.labor_cost,
      material_cost: item.material_cost,
      labor_material_ratio: item.labor_material_ratio
    }))
    
    // 设置摘要数据
    summary.value = {
      total_cost: res.data.total_cost,
      total_labor_cost: res.data.total_labor_cost,
      total_material_cost: res.data.total_material_cost,
      labor_material_ratio: res.data.labor_material_ratio
    }
    
  } catch (error) {
    console.error('获取工资数据失败:', error)
    ElMessage.error('获取工资数据失败，请重试')
  } finally {
    loading.value = false
  }
}

// 重置查询条件
const resetQuery = () => {
  const defaultRange = getDefaultDateRange()
  queryParams.value = {
    start_date: defaultRange.start,
    end_date: defaultRange.end,
    period_type: 'month'
  }
  fetchData()
}

// 初始化时获取数据
onMounted(() => {
  // 设置默认查询范围为上个月
  const defaultRange = getDefaultDateRange()
  queryParams.value.start_date = defaultRange.start
  queryParams.value.end_date = defaultRange.end
  
  fetchData()
})
</script>

<style scoped>
.wage-management {
  padding: 20px;
}

.query-card {
  margin-bottom: 20px;
}

.query-form {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  align-items: center;
}

.form-item {
  display: flex;
  align-items: center;
}

.label {
  min-width: 80px;
  font-weight: bold;
}

.data-card {
  margin-top: 20px;
}

.summary {
  margin-top: 20px;
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 4px;
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
}

.summary-item {
  display: flex;
  align-items: center;
}

.summary-item .label {
  font-weight: bold;
  color: #606266;
}

.summary-item .value {
  font-weight: bold;
  color: #409EFF;
  font-size: 16px;
}
</style>