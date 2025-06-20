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
        <el-button type="primary" @click="fetchSummary">查看汇总</el-button>
        <el-card v-if="summaryData">
          <pre>{{ summaryData }}</pre>
        </el-card>
      </el-tab-pane>

      <!-- 手动发放工资 -->
      <el-tab-pane label="发放工资" name="distribute">
        <el-button type="success" @click="runDistribution">手动发放当前月工资</el-button>
        <el-card v-if="distributionResult">
          <pre>{{ distributionResult }}</pre>
        </el-card>
      </el-tab-pane>

    </el-tabs>
  </div>
</template>

<script setup>
import { ref } from 'vue'
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

const runDistribution = async () => {
  try {
    const res = await wageAPI.runMonthlyDistribution(filters.value.year, filters.value.month)
    distributionResult.value = res.data
  } catch (err) {
    ElMessage.error('工资发放失败')
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
</style>
