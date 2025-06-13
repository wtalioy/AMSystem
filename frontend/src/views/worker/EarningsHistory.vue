<template>
    <div class="earnings-history">
      <h2>收入历史记录</h2>
      <el-table :data="records" style="width: 100%">
        <el-table-column prop="month" label="月份" />
        <el-table-column prop="total_earnings" label="总收入 (¥)" />
        <el-table-column prop="base_earnings" label="基础收入 (¥)" />
        <el-table-column prop="performance_bonus" label="绩效奖金 (¥)" />
      </el-table>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted } from 'vue'
  import workerOrdersAPI from '@/api/workerOrders'
  import { ElMessage } from 'element-plus'
  
  const records = ref([])
  
  const fetchHistory = async () => {
    try {
      records.value = await workerOrdersAPI.getEarningsHistory()
    } catch {
      ElMessage.error('获取收入历史失败')
    }
  }
  
  onMounted(fetchHistory)
  </script>
  