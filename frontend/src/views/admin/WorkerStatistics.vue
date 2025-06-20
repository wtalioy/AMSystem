<template>
  <div class="worker-stats-table">
    <h2>工人统计</h2>

    <!-- 时间筛选器和查询按钮 -->
    <div class="date-filter">
      <!-- 开始时间选择器 -->
      <el-date-picker
        v-model="startTime"
        type="date"
        value-format="YYYY-MM-DD"
        placeholder="开始日期"
        style="margin-right: 10px"
      />
      <!-- 结束时间选择器 -->
      <el-date-picker
        v-model="endTime"
        type="date"
        value-format="YYYY-MM-DD"
        placeholder="结束日期"
        style="margin-right: 10px"
      />
      <!-- 查询按钮 -->
      <el-button type="primary" @click="fetchStats">查询</el-button>
    </div>

    <!-- 表格展示所有工人类型的统计信息 -->
    <el-table :data="workers" style="width: 100%; margin-top: 20px">
      <el-table-column prop="worker_type" label="工人类型" />
      <el-table-column prop="worker_count" label="工人数" />
      <el-table-column prop="task_count" label="任务总数" />
      <el-table-column prop="total_work_hours" label="总工时（小时）" />
      <el-table-column prop="average_hours_per_task" label="平均每单耗时（小时）" />
      <el-table-column prop="hourly_wage" label="小时工资" />
    </el-table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import statsAPI from '@/api/adminStats'

// 响应式数据：用于存储工人统计数据
const workers = ref([])

// 响应式数据：开始和结束时间（用户选择或默认）
const startTime = ref('')
const endTime = ref('')

// 查询工人统计信息的方法
const fetchStats = async () => {
  // 校验是否选择了完整时间范围
  if (!startTime.value || !endTime.value) {
    alert('请先选择开始日期和结束日期')
    return
  }

  try {
    // 调用后端接口获取统计数据
    const res = await statsAPI.getWorkerStatistics({
      start_time: startTime.value,
      end_time: endTime.value
    })
    // 将返回结果赋值给表格
    workers.value = res.data || []
  } catch (error) {
    console.error('获取工人统计数据失败：', error)
  }
}

// 页面加载时默认拉取一次数据（可选）
onMounted(() => {
  const today = new Date().toISOString().split('T')[0]
  startTime.value = '2024-01-01' // 示例默认起始时间
  endTime.value = today           // 默认结束为当前日期
  fetchStats()
})
</script>

<style scoped>
.worker-stats-table {
  margin-top: 20px;
}

.date-filter {
  margin-bottom: 20px;
}
</style>
