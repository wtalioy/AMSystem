<template>
  <div class="worker-productivity-table">
    <h2>工人生产力分析</h2>

    <!-- 工人类型生产力数据表 -->
    <el-table :data="workers" style="width: 100%">
      <!-- 工人类型 -->
      <el-table-column prop="worker_type" label="工人类型" />

      <!-- 总任务数 -->
      <el-table-column prop="total_tasks_assigned" label="总任务数" />

      <!-- 完成任务数 -->
      <el-table-column prop="completed_tasks" label="完成任务数" />

      <!-- 完成率（格式化为百分号） -->
      <el-table-column label="完成率">
        <template #default="{ row }">
          <span>{{ row.completion_rate_percentage }}%</span>
        </template>
      </el-table-column>

      <!-- 平均完成时间（小时） -->
      <el-table-column prop="average_completion_time_hours" label="平均耗时（小时）" />

      <!-- 平均客户评分 -->
      <el-table-column prop="average_customer_rating" label="客户评分" />

      <!-- 生产力得分 -->
      <el-table-column prop="productivity_score" label="生产力得分" />
    </el-table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import productivityAPI from '@/api/adminStats'

const workers = ref([])

// 示例日期（可替换为实际日期选择器）
const startDate = '2024-01-01'
const endDate = '2025-01-01'

// 组件挂载时获取生产力数据
onMounted(async () => {
  try {
    const res = await productivityAPI.getWorkerProductivity({
      start_date: startDate,
      end_date: endDate
    })
    workers.value = res.data || []
  } catch (error) {
    console.error('获取工人生产力数据失败：', error)
  }
})
</script>

<style scoped>
.worker-productivity-table {
  margin-top: 20px;
}
</style>
