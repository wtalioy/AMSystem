<template>
  <div class="wage-management">
    <!-- 顶部控制栏 -->
    <div class="control-bar">
      <el-date-picker
        v-model="selectedPeriod"
        type="month"
        placeholder="选择月份"
        format="YYYY年MM月"
        value-format="YYYY-MM"
      />
      <el-button type="primary" @click="loadData">加载数据</el-button>
      <el-button type="success" @click="runDistribution">执行工资发放</el-button>
      <el-button-group class="scheduler-controls">
        <el-button :type="schedulerStatus ? 'danger' : 'success'" @click="toggleScheduler">
          {{ schedulerStatus ? '停止调度器' : '启动调度器' }}
        </el-button>
        <el-button @click="checkSchedulerStatus">检查状态</el-button>
      </el-button-group>
    </div>

    <!-- 标签页导航 -->
    <el-tabs v-model="activeTab" type="border-card">
      <!-- 月度工资总览 -->
      <el-tab-pane label="月度工资总览" name="monthly">
        <el-table :data="monthlyEarnings" style="width: 100%" v-loading="loading.monthly">
          <el-table-column prop="worker_id" label="工人ID" width="120" fixed />
          <el-table-column label="工人类型" width="120">
            <template #default="{ row }">
              {{ workerTypeMap[row.worker_type] || row.worker_type }}
            </template>
          </el-table-column>
          <el-table-column label="工作摘要" width="250">
            <template #default="{ row }">
              <div class="work-summary">
                <div>总工时: {{ row.work_summary.total_hours }} 小时</div>
                <div>订单数: {{ row.work_summary.total_orders }} 单</div>
                <div>时薪: ¥{{ row.work_summary.hourly_rate.toFixed(2) }}</div>
                <div>平均评分: {{ row.work_summary.average_rating.toFixed(1) }}</div>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="收入明细" width="250">
            <template #default="{ row }">
              <div class="earnings-detail">
                <div>基础收入: ¥{{ row.earnings.base_earnings.toFixed(2) }}</div>
                <div>绩效奖金: ¥{{ row.earnings.performance_bonus.toFixed(2) }}</div>
                <div class="total-earnings">总收入: ¥{{ row.earnings.total_earnings.toFixed(2) }}</div>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="操作">
            <template #default="{ row }">
              <el-button size="small" @click="viewWorkerDetails(row.worker_id)">查看详情</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <!-- 工人详情视图 -->
      <el-tab-pane label="工人详情" name="workerDetail" v-if="selectedWorker">
        <div class="worker-detail-header">
          <h3>{{ selectedWorker.worker_id }} - {{ workerTypeMap[selectedWorker.worker_type] || selectedWorker.worker_type }}</h3>
          <div class="worker-stats">
            <el-statistic title="总工时" :value="selectedWorker.work_summary.total_hours" suffix="小时" />
            <el-statistic title="总订单" :value="selectedWorker.work_summary.total_orders" suffix="单" />
            <el-statistic title="总收入" :value="selectedWorker.earnings.total_earnings" prefix="¥" :precision="2" />
          </div>
        </div>

        <!-- 收入历史图表 -->
        <div class="chart-container">
          <h4>收入历史 (最近12个月)</h4>
          <el-divider />
          <div ref="earningsChart" style="height: 300px;"></div>
        </div>

        <!-- 订单详情 -->
        <div class="order-details">
          <h4>订单明细</h4>
          <el-table :data="selectedWorker.order_details" height="250">
            <el-table-column prop="order_id" label="订单ID" width="180" />
            <el-table-column prop="completion_date" label="完成日期" width="180">
              <template #default="{ row }">
                {{ formatDate(row.completion_date) }}
              </template>
            </el-table-column>
            <el-table-column prop="hours_worked" label="工时" width="100" align="center" />
            <el-table-column prop="description" label="工作描述" />
          </el-table>
        </div>
      </el-tab-pane>

      <!-- 汇总报告 -->
      <el-tab-pane label="汇总报告" name="summaryReport">
        <div v-if="summaryReport" class="summary-report">
          <div class="report-header">
            <h3>{{ summaryReport.period }} 工资汇总报告</h3>
            <div class="overview-stats">
              <el-statistic title="工人总数" :value="summaryReport.total_workers" />
              <el-statistic title="总工时" :value="summaryReport.summary.total_hours_worked" suffix="小时" />
              <el-statistic title="总工资" :value="summaryReport.summary.total_earnings" prefix="¥" :precision="2" />
              <el-statistic title="人均收入" :value="summaryReport.summary.average_earnings_per_worker" prefix="¥" :precision="2" />
            </div>
          </div>

          <el-divider />

          <!-- 工人类型分析 -->
          <div class="type-analysis">
            <h4>工人类型分析</h4>
            <el-table :data="Object.entries(summaryReport.worker_type_breakdown)" style="width: 100%">
              <el-table-column prop="[0]" label="工人类型">
                <template #default="{ row }">
                  {{ workerTypeMap[row[0]] || row[0] }}
                </template>
              </el-table-column>
              <el-table-column prop="[1].count" label="人数" align="center" />
              <el-table-column prop="[1].total_hours" label="总工时" align="center" />
              <el-table-column prop="[1].total_earnings" label="总收入" align="center">
                <template #default="{ row }">
                  ¥{{ row[1].total_earnings.toFixed(2) }}
                </template>
              </el-table-column>
              <el-table-column prop="[1].total_orders" label="订单数" align="center" />
            </el-table>
          </div>
        </div>
        <div v-else class="empty-report">
          <el-empty description="请选择月份并加载数据" />
        </div>
      </el-tab-pane>

      <!-- 工资发放记录 -->
      <el-tab-pane label="工资发放" name="distribution">
        <div class="distribution-controls">
          <el-button type="primary" @click="runDistribution" :loading="distributing">
            {{ distributing ? '发放中...' : '执行月度工资发放' }}
          </el-button>
          <el-tag v-if="lastDistribution" type="info">
            最近发放: {{ lastDistribution.period }} ({{ lastDistribution.successful_distributions }}人成功)
          </el-tag>
        </div>

        <div v-if="distributionResult" class="distribution-result">
          <el-alert :title="`工资发放完成: ${distributionResult.successful_distributions}人成功, ${distributionResult.failed_distributions}人失败`" 
                   :type="distributionResult.failed_distributions > 0 ? 'warning' : 'success'"
                   show-icon>
          </el-alert>
          
          <div class="distribution-stats">
            <el-statistic title="发放总额" :value="distributionResult.total_amount_distributed" prefix="¥" :precision="2" />
            <el-statistic title="发放人数" :value="distributionResult.successful_distributions" />
            <el-statistic title="失败人数" :value="distributionResult.failed_distributions" />
          </div>

          <!-- 发放详情 -->
          <el-collapse v-model="activeDistributionCollapse">
            <el-collapse-item title="发放详情" name="details">
              <el-table :data="distributionResult.distribution_details" height="250">
                <el-table-column prop="worker_id" label="工人ID" width="120" />
                <el-table-column prop="amount" label="金额" width="120" align="right">
                  <template #default="{ row }">
                    ¥{{ row.amount.toFixed(2) }}
                  </template>
                </el-table-column>
                <el-table-column prop="hours_worked" label="工时" width="100" align="center" />
                <el-table-column prop="orders_completed" label="订单数" width="100" align="center" />
                <el-table-column prop="note" label="备注" />
              </el-table>
            </el-collapse-item>
            
            <el-collapse-item title="失败记录" name="errors" v-if="distributionResult.errors && distributionResult.errors.length > 0">
              <el-table :data="distributionResult.errors">
                <el-table-column prop="worker_id" label="工人ID" width="120" />
                <el-table-column prop="error" label="错误信息" />
                <el-table-column prop="type" label="错误类型" width="150" />
              </el-table>
            </el-collapse-item>
          </el-collapse>
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import wageAPI from '@/api/adminStats'
import { ElMessage, ElLoading } from 'element-plus'

// 当前选中的月份 (YYYY-MM格式)
const selectedPeriod = ref('')
// 活动标签页
const activeTab = ref('monthly')
// 月度收入数据
const monthlyEarnings = ref([])
// 汇总报告数据
const summaryReport = ref(null)
// 工资发放结果
const distributionResult = ref(null)
// 最后一次发放记录
const lastDistribution = ref(null)
// 调度器状态
const schedulerStatus = ref(false)
// 选中的工人详情
const selectedWorker = ref(null)
// 收入历史数据
const earningsHistory = ref([])
// 加载状态
const loading = reactive({
  monthly: false,
  summary: false
})
// 工资发放中状态
const distributing = ref(false)
// 活跃的折叠面板
const activeDistributionCollapse = ref(['details'])
// 图表实例
let earningsChart = null

// 工人类型映射
const workerTypeMap = {
  1: '初级工人',
  2: '中级工人',
  3: '高级工人',
  4: '管理岗'
}

// 初始化当前月份
onMounted(() => {
  const now = new Date()
  selectedPeriod.value = `${now.getFullYear()}-${(now.getMonth() + 1).toString().padStart(2, '0')}`
  checkSchedulerStatus()
})

// 加载数据
const loadData = async () => {
  if (!selectedPeriod.value) {
    ElMessage.warning('请先选择月份')
    return
  }
  
  const [year, month] = selectedPeriod.value.split('-').map(Number)
  
  try {
    // 加载月度工资数据
    loading.monthly = true
    const monthlyRes = await wageAPI.getAllWorkersMonthlyEarnings(year, month)
    monthlyEarnings.value = monthlyRes.data || []
    
    // 加载汇总报告
    loading.summary = true
    const summaryRes = await wageAPI.getEarningsSummaryReport(year, month)
    summaryReport.value = summaryRes.data
  } catch (error) {
    ElMessage.error('数据加载失败: ' + error.message)
  } finally {
    loading.monthly = false
    loading.summary = false
  }
}

// 查看工人详情
const viewWorkerDetails = async (worker_id) => {
  const [year, month] = selectedPeriod.value.split('-').map(Number)
  
  try {
    // 加载工人月度详情
    const res = await wageAPI.getWorkerMonthlyEarnings(worker_id, year, month)
    selectedWorker.value = res.data
    
    // 加载工人历史收入
    const historyRes = await wageAPI.getWorkerEarningsHistory(worker_id, 12)
    earningsHistory.value = historyRes.data || []
    
    // 切换到详情标签页
    activeTab.value = 'workerDetail'
    
    // 渲染图表
    nextTick(() => {
      renderEarningsChart()
    })
  } catch (error) {
    ElMessage.error('加载工人详情失败: ' + error.message)
  }
}

// 渲染收入历史图表
const renderEarningsChart = () => {
  if (!earningsChart) {
    earningsChart = echarts.init(document.querySelector('.chart-container .el-divider').nextElementSibling)
  }
  
  const option = {
    tooltip: {
      trigger: 'axis',
      formatter: '{b}<br/>¥{c}'
    },
    xAxis: {
      type: 'category',
      data: earningsHistory.value.map(item => 
        `${item.period.year}-${item.period.month.toString().padStart(2, '0')}`
      ).reverse()
    },
    yAxis: {
      type: 'value',
      name: '收入 (¥)'
    },
    series: [{
      name: '月收入',
      type: 'bar',
      data: earningsHistory.value.map(item => item.earnings.total_earnings).reverse(),
      itemStyle: {
        color: '#409EFF'
      }
    }],
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    }
  }
  
  earningsChart.setOption(option)
  window.addEventListener('resize', () => earningsChart.resize())
}

// 执行工资发放
const runDistribution = async () => {
  if (!selectedPeriod.value) {
    ElMessage.warning('请先选择月份')
    return
  }
  
  const [year, month] = selectedPeriod.value.split('-').map(Number)
  
  try {
    distributing.value = true
    const res = await wageAPI.runMonthlyDistribution(year, month)
    distributionResult.value = res.data
    lastDistribution.value = {
      period: `${year}年${month}月`,
      successful_distributions: res.data.successful_distributions
    }
    ElMessage.success('工资发放操作已执行')
    activeTab.value = 'distribution'
  } catch (error) {
    ElMessage.error('工资发放失败: ' + error.message)
  } finally {
    distributing.value = false
  }
}

// 检查调度器状态
const checkSchedulerStatus = async () => {
  try {
    const res = await wageAPI.getSchedulerStatus()
    schedulerStatus.value = res.data.running || false
    ElMessage.info(`调度器状态: ${schedulerStatus.value ? '运行中' : '已停止'}`)
  } catch (error) {
    ElMessage.error('获取调度器状态失败: ' + error.message)
  }
}

// 切换调度器状态
const toggleScheduler = async () => {
  try {
    if (schedulerStatus.value) {
      await wageAPI.stopScheduler()
      ElMessage.success('调度器已停止')
    } else {
      await wageAPI.startScheduler()
      ElMessage.success('调度器已启动')
    }
    schedulerStatus.value = !schedulerStatus.value
  } catch (error) {
    ElMessage.error('操作失败: ' + error.message)
  }
}

// 日期格式化
const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  }).replace(/\//g, '-')
}
</script>

<style scoped>
.wage-management {
  padding: 20px;
}

.control-bar {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 20px;
  padding: 15px;
  background: #f5f7fa;
  border-radius: 4px;
}

.scheduler-controls {
  margin-left: auto;
}

.worker-detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #ebeef5;
}

.worker-stats {
  display: flex;
  gap: 30px;
}

.chart-container {
  margin: 30px 0;
  padding: 20px;
  border: 1px solid #ebeef5;
  border-radius: 4px;
}

.order-details {
  margin-top: 30px;
}

.work-summary, .earnings-detail {
  line-height: 1.8;
}

.total-earnings {
  font-weight: bold;
  color: #e6a23c;
}

.report-header {
  margin-bottom: 20px;
}

.overview-stats {
  display: flex;
  justify-content: space-around;
  margin: 20px 0;
}

.type-analysis {
  margin-top: 30px;
}

.distribution-controls {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 20px;
}

.distribution-stats {
  display: flex;
  justify-content: space-around;
  margin: 20px 0;
}

:deep(.el-collapse-item__header) {
  font-weight: bold;
}

:deep(.el-tabs__content) {
  padding: 20px;
  background: #fff;
}
</style>