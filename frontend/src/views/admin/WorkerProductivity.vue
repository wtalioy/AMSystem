<template>
  <div class="worker-productivity-table">
    <h2>工人生产力分析</h2>

    <!-- 时间范围选择器 -->
    <div class="date-filter">
      <!-- 开始日期选择器 -->
      <el-date-picker
        v-model="startDate"
        type="date"
        value-format="YYYY-MM-DD"
        placeholder="开始日期"
        style="margin-right: 10px"
      />
      <!-- 结束日期选择器 -->
      <el-date-picker
        v-model="endDate"
        type="date"
        value-format="YYYY-MM-DD"
        placeholder="结束日期"
        style="margin-right: 10px"
      />
      <!-- 查询按钮 -->
      <el-button type="primary" @click="fetchData">查询</el-button>
    </div>

    <!-- 工人类型生产力数据表 -->
    <el-table :data="workers" style="width: 100%; margin-top: 20px">
      <el-table-column prop="worker_type" label="工人类型" />
      <el-table-column prop="total_tasks_assigned" label="总任务数" />
      <el-table-column prop="completed_tasks" label="完成任务数" />
      <el-table-column label="完成率">
        <template #default="{ row }">
          <span>{{ row.completion_rate_percentage }}%</span>
        </template>
      </el-table-column>
      <el-table-column prop="average_completion_time_hours" label="平均耗时（小时）" />
      <el-table-column prop="average_customer_rating" label="客户评分" />
      <el-table-column prop="productivity_score" label="生产力得分" />
    </el-table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import productivityAPI from '@/api/adminStats'

// 响应式数据：表格数据
const workers = ref([])

// 响应式数据：开始和结束日期（默认值可选填，也可以为空）
const startDate = ref('')
const endDate = ref('')

// 获取数据函数，根据当前时间范围发送请求
const fetchData = async () => {
  // 校验用户是否已选择时间范围
  if (!startDate.value || !endDate.value) {
    alert('请先选择开始日期和结束日期')
    return
  }

  try {
    // 调用后端 API 获取数据
    const res = await productivityAPI.getWorkerProductivity({
      start_date: startDate.value,
      end_date: endDate.value
    })
    // 将结果赋值给 workers 表格
    workers.value = res.data || []
  } catch (error) {
    console.error('获取工人生产力数据失败：', error)
  }
}

// 页面加载时默认拉取一次数据（可选）
onMounted(() => {
  const today = new Date().toISOString().split('T')[0]
  startDate.value = '2024-01-01' // 示例默认开始时间
  endDate.value = today           // 默认结束为当前日期
  fetchData()
})
</script>

<style scoped>
.worker-productivity-table {
  margin-top: 20px;
}

.date-filter {
  margin-bottom: 20px;
}
</style>
