<template>
  <div class="wage-management">
    <h2>工资管理面板</h2>

    <!-- 调度器状态控制按钮（右上角） -->
<div class="scheduler-controls">
  <span style="margin-right: 10px">
    调度器状态：
    <el-tag :type="isSchedulerRunning ? 'success' : 'info'">
      {{ isSchedulerRunning ? '已启动' : '已停止' }}
    </el-tag>
  </span>

  <el-button 
    type="success" 
    :disabled="isSchedulerRunning" 
    @click="startScheduler"
  >
    启动
  </el-button>
  
  <el-button 
    type="danger" 
    :disabled="!isSchedulerRunning" 
    @click="stopScheduler"
  >
    暂停
  </el-button>
</div>

    <el-tabs v-model="activeTab">
      <!-- 单个工人月度收入 -->
      <el-tab-pane label="工人月度收入" name="monthly">
        <el-form :inline="true" @submit.prevent="fetchWorkerMonthly">
          <el-form-item label="工人ID">
            <el-input v-model="filters.worker_id" />
          </el-form-item>
          <el-form-item label="年份">
            <el-input-number v-model="filters.year" :min="2000" />
          </el-form-item>
          <el-form-item label="月份">
            <el-input-number v-model="filters.month" :min="1" :max="12" />
          </el-form-item>
          <el-button type="primary" @click="fetchWorkerMonthly">查询</el-button>
        </el-form>

        <el-card v-if="workerMonthlyData">
          <pre>{{ workerMonthlyData }}</pre>
        </el-card>
      </el-tab-pane>

      <!-- 工人收入历史 -->
      <el-tab-pane label="工人收入历史" name="history">
        <el-form :inline="true" @submit.prevent="fetchWorkerHistory">
          <el-form-item label="工人ID">
            <el-input v-model="filters.worker_id" />
          </el-form-item>
          <el-form-item label="回溯月数">
            <el-input-number v-model="filters.months_back" :min="1" :max="24" />
          </el-form-item>
          <el-button type="primary" @click="fetchWorkerHistory">查询</el-button>
        </el-form>

        <el-table :data="historyData" v-if="historyData.length">
          <el-table-column label="年份" prop="period.year" />
          <el-table-column label="月份" prop="period.month" />
          <el-table-column label="总收入" prop="earnings.total_earnings" />
          <el-table-column label="基础收入" prop="earnings.base_earnings" />
          <el-table-column label="绩效奖金" prop="earnings.performance_bonus" />
        </el-table>
      </el-tab-pane>

      <!-- 所有工人月度收入 -->
      <el-tab-pane label="所有工人收入" name="all">
        <el-form :inline="true" @submit.prevent="fetchAllWorkers">
          <el-form-item label="年份">
            <el-input-number v-model="filters.year" :min="2000" />
          </el-form-item>
          <el-form-item label="月份">
            <el-input-number v-model="filters.month" :min="1" :max="12" />
          </el-form-item>
          <el-button type="primary" @click="fetchAllWorkers">查询</el-button>
        </el-form>

        <el-table :data="allWorkersData" v-if="allWorkersData.length">
          <el-table-column label="工人ID" prop="worker_id" />
          <el-table-column label="总收入" prop="earnings.total_earnings" />
          <el-table-column label="工时" prop="work_summary.total_hours" />
          <el-table-column label="订单数" prop="work_summary.total_orders" />
        </el-table>
      </el-tab-pane>

      <!-- 汇总报告 -->
    <el-tab-pane label="收入汇总" name="summary">
      <el-form :inline="true">
        <el-form-item label="年份">
          <el-input-number v-model="filters.year" :min="2000" />
        </el-form-item>
        <el-form-item label="月份">
          <el-input-number v-model="filters.month" :min="1" :max="12" />
        </el-form-item>
        <el-button type="primary" @click="fetchSummary">查看汇总</el-button>
      </el-form>

      <el-card v-if="summaryData" class="summary-card">
        <div class="summary-header">
          <h3>{{ summaryData.period }} 收入汇总报告</h3>
          <el-tag type="info">总工人数: {{ summaryData.total_workers }}</el-tag>
        </div>
        
        <el-divider />
        
        <div class="summary-section">
          <h4>总体统计</h4>
          <el-row :gutter="20">
            <el-col :span="6">
              <el-statistic title="总工时" :value="summaryData.summary.total_hours_worked" />
            </el-col>
            <el-col :span="6">
              <el-statistic title="总收入(元)" :value="summaryData.summary.total_earnings" :precision="2" />
            </el-col>
            <el-col :span="6">
              <el-statistic title="总订单数" :value="summaryData.summary.total_orders_completed" />
            </el-col>
            <el-col :span="6">
              <el-statistic title="人均收入(元)" :value="summaryData.summary.average_earnings_per_worker" :precision="2" />
            </el-col>
          </el-row>
        </div>
        
        <el-divider />
        
        <div class="summary-section">
          <h4>按工人类型统计</h4>
          <el-table :data="workerTypeData" border style="width: 100%">
            <el-table-column prop="type" label="工人类型" width="180" />
            <el-table-column prop="count" label="人数" align="center" />
            <el-table-column prop="total_hours" label="总工时" align="center" />
            <el-table-column prop="total_earnings" label="总收入(元)" align="right">
              <template #default="{row}">
                {{ row.total_earnings.toFixed(2) }}
              </template>
            </el-table-column>
            <el-table-column prop="total_orders" label="总订单" align="center" />
          </el-table>
        </div>
      </el-card>
    </el-tab-pane>

    <!-- 手动发放工资 -->
    <el-tab-pane label="发放工资" name="distribute">
      <el-form :inline="true">
        <el-form-item label="年份">
          <el-input-number v-model="filters.year" :min="2000" />
        </el-form-item>
        <el-form-item label="月份">
          <el-input-number v-model="filters.month" :min="1" :max="12" />
        </el-form-item>
        <el-button 
          type="success" 
          @click="runDistribution"
          :loading="distributing"
        >
          手动发放工资
        </el-button>
      </el-form>

      <el-card v-if="distributionResult" class="distribution-card">
        <div class="distribution-header">
          <h3>{{ distributionResult.period }} 工资发放结果</h3>
          <div class="stats">
            <el-tag type="success">成功: {{ distributionResult.successful_distributions }}</el-tag>
            <el-tag type="danger">失败: {{ distributionResult.failed_distributions }}</el-tag>
            <el-tag type="warning">总发放金额: {{ distributionResult.total_amount_distributed.toFixed(2) }}元</el-tag>
          </div>
        </div>
        
        <el-divider />
        
        <div v-if="distributionResult.distribution_details.length" class="distribution-section">
          <h4>发放详情</h4>
          <el-table :data="distributionResult.distribution_details" border height="250">
            <el-table-column prop="worker_id" label="工人ID" width="120" />
            <el-table-column prop="amount" label="金额(元)" align="right" width="120">
              <template #default="{row}">
                {{ row.amount.toFixed(2) }}
              </template>
            </el-table-column>
            <el-table-column prop="hours_worked" label="工时" align="center" width="100" />
            <el-table-column prop="orders_completed" label="订单数" align="center" width="100" />
            <el-table-column prop="note" label="备注" />
          </el-table>
        </div>
        
        <el-divider v-if="distributionResult.errors.length" />
        
        <div v-if="distributionResult.errors.length" class="error-section">
          <h4>发放失败记录</h4>
          <el-table :data="distributionResult.errors" border style="width: 100%">
            <el-table-column prop="worker_id" label="工人ID" width="120" />
            <el-table-column prop="error" label="错误信息" />
            <el-table-column prop="type" label="错误类型" width="150" />
          </el-table>
        </div>
      </el-card>
    </el-tab-pane>

  </el-tabs>
  </div>
</template>

<script setup>
import { ref , computed , onMounted} from 'vue'
import { ElMessage } from 'element-plus'
import wageAPI from '@/api/adminStats'

const activeTab = ref('monthly')
const filters = ref({
  worker_id: '',
  year: new Date().getFullYear(),
  month: new Date().getMonth() + 1,
  months_back: 12
})

const workerMonthlyData = ref(null)
const historyData = ref([])
const allWorkersData = ref([])
const summaryData = ref(null)
const distributionResult = ref(null)
const isSchedulerRunning = ref(false) // 当前是否运行中

// 请求函数
const fetchWorkerMonthly = async () => {
  try {
    const res = await wageAPI.getWorkerMonthlyEarnings(
      filters.value.worker_id, filters.value.year, filters.value.month
    )
    workerMonthlyData.value = res.data
  } catch (err) {
    ElMessage.error('查询失败')
  }
}

const fetchWorkerHistory = async () => {
  try {
    const res = await wageAPI.getWorkerEarningsHistory(
      filters.value.worker_id, filters.value.months_back
    )
    historyData.value = res.data
  } catch (err) {
    ElMessage.error('获取历史失败')
  }
}

const fetchAllWorkers = async () => {
  try {
    const res = await wageAPI.getAllWorkersMonthlyEarnings(
      filters.value.year, filters.value.month
    )
    allWorkersData.value = res.data
  } catch (err) {
    ElMessage.error('获取失败')
  }
}

const fetchSummary = async () => {
  try {
    const res = await wageAPI.getEarningsSummaryReport(filters.value.year, filters.value.month)
    summaryData.value = res.data
  } catch (err) {
    ElMessage.error('汇总失败')
  }
}

// 计算属性处理工人类型数据
const workerTypeData = computed(() => {
  if (!summaryData.value || !summaryData.value.worker_type_breakdown) return []
  
  return Object.entries(summaryData.value.worker_type_breakdown).map(([type, data]) => ({
    type,
    ...data
  }))
})

// 添加加载状态
const distributing = ref(false)

const runDistribution = async () => {
  distributing.value = true
  try {
    const res = await wageAPI.runMonthlyDistribution(filters.value.year, filters.value.month)
    distributionResult.value = res.data
    ElMessage.success('工资发放操作完成')
  } catch (err) {
    ElMessage.error('工资发放失败')
  } finally {
    distributing.value = false
  }
}

const getSchedulerStatus = async () => {
  try {
    const res = await wageAPI.getSchedulerStatus()
    // 假设返回结果格式为 { running: true/false }
    isSchedulerRunning.value = res.data.running ?? false
  } catch (err) {
    ElMessage.error('获取调度器状态失败')
  }
}

const startScheduler = async () => {
  try {
    await wageAPI.startScheduler()
    ElMessage.success('调度器已启动')
    getSchedulerStatus()
  } catch (err) {
    ElMessage.error('启动失败')
  }
}

const stopScheduler = async () => {
  try {
    await wageAPI.stopScheduler()
    ElMessage.success('调度器已停止')
    getSchedulerStatus()
  } catch (err) {
    ElMessage.error('停止失败')
  }
}

// 添加挂载时获取状态
onMounted(() => {
  getSchedulerStatus()
})

</script>

<style scoped>
.wage-management {
  padding: 20px;
}

.header-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.scheduler-controls {
  display: flex;
  align-items: center;
  gap: 10px;
}

/* 新增样式 */
.summary-card, .distribution-card {
  margin-top: 20px;
}

.summary-header, .distribution-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.stats {
  display: flex;
  gap: 10px;
}

.summary-section {
  margin-bottom: 20px;
}

.summary-section h4, .distribution-section h4, .error-section h4 {
  margin-bottom: 15px;
  color: #409eff;
}

.el-divider {
  margin: 20px 0;
}

/* 调整统计卡片样式 */
.el-statistic {
  text-align: center;
  padding: 10px;
  background-color: #f5f7fa;
  border-radius: 4px;
}
</style>
