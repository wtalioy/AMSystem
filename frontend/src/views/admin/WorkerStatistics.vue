<template>
  <div class="worker-stats-table">
    <h2>工人统计</h2>

    <!-- 表格展示所有工人类型的统计信息 -->
    <el-table :data="workers" style="width: 100%">
      <!-- 工人类型 -->
      <el-table-column prop="worker_type" label="工人类型" />

      <!-- 工人数 -->
      <el-table-column prop="worker_count" label="工人数" />

      <!-- 任务总数 -->
      <el-table-column prop="task_count" label="任务总数" />

      <!-- 总工时 -->
      <el-table-column prop="total_work_hours" label="总工时（小时）" />

      <!-- 平均每单耗时 -->
      <el-table-column prop="average_hours_per_task" label="平均每单耗时（小时）" />

      <!-- 小时工资 -->
      <el-table-column prop="hourly_wage" label="小时工资" />
    </el-table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import statsAPI from '@/api/adminStats'

// 用于存储工人统计数据
const workers = ref([])

// 模拟时间参数（后续可以加日期筛选组件）
const startTime = '2024-01-01'
const endTime = '2025-01-01'

onMounted(async () => {
  try {
    // 调用接口时传入起止时间
    const res = await statsAPI.getWorkerStatistics({
      start_time: startTime,
      end_time: endTime
    })
    workers.value = res.data || []
  } catch (error) {
    console.error('获取工人统计数据失败：', error)
  }
})
</script>

<style scoped>
.worker-stats-table {
  margin-top: 20px;
}
</style>
