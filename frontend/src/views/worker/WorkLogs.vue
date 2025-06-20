<!-- 
维修记录查看组件
功能：显示维修工单的耗材、成本、耗时等记录
注意：现在已经用不上它了
-->

<template>
  <div class="work-logs">
    <h2>维修记录</h2>
    <el-table :data="logs" style="width: 100%; margin-top: 20px">
      <el-table-column prop="order_id" label="工单号" width="180" />
      <el-table-column prop="consumption" label="耗材使用" />
      <el-table-column prop="cost" label="成本（元）" />
      <el-table-column prop="duration" label="维修时长（小时）" />
      <el-table-column prop="log_time" label="记录时间" :formatter="formatDate" />
    </el-table>
    
    <el-pagination
      layout="prev, pager, next"
      :total="total"
      :page-size="pageSize"
      @current-change="handlePageChange"
      style="margin-top: 20px"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import logsAPI from '@/api/logs'

const logs = ref([])
const total = ref(0)
const pageSize = ref(20)
const currentPage = ref(1)

const fetchData = async () => {
  try {
    const res = await logsAPI.getWorkerLogs(currentPage.value, pageSize.value)
    logs.value = res.data || []
    total.value = res.headers['x-total-count'] || 0
  } catch (error) {
    console.error('获取日志失败:', error)
  }
}

const handlePageChange = (newPage) => {
  currentPage.value = newPage
  fetchData()
}

const formatDate = (row) => {
  return new Date(row.log_time).toLocaleString()
}

onMounted(fetchData)
</script>

<style scoped>
.work-logs {
  padding: 20px;
}
</style>