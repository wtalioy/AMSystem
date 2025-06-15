<template>
    <div class="work-logs">
      <h2>本月收入</h2>
      <el-date-picker
        v-model="selectedDate"
        type="month"
        format="YYYY-MM"
        placeholder="选择月份"
        @change="fetchEarnings"
      />
      <el-card v-if="earnings">
        <p>基础收入：¥{{ earnings.earnings.base_earnings }}</p>
        <p>绩效奖金：¥{{ earnings.earnings.performance_bonus }}</p>
        <p><strong>总收入：¥{{ earnings.earnings.total_earnings }}</strong></p>
        <p>本月工时：{{ earnings.work_summary.total_hours }} 小时</p>
        <p>完成订单数：{{ earnings.work_summary.total_orders }} 单</p>
      </el-card>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted } from 'vue'
  import workerOrdersAPI from '@/api/workerOrders'
  import dayjs from 'dayjs'
  import { ElMessage } from 'element-plus'
  
  const selectedDate = ref(dayjs())
  const earnings = ref(null)
  
  const fetchEarnings = async () => {
    try {
      const year = selectedDate.value.year()
      const month = selectedDate.value.month() + 1
      earnings.value = await workerOrdersAPI.getMonthlyEarnings(year, month)
    } catch {
      ElMessage.error('获取收入失败')
    }
  }
  
  onMounted(fetchEarnings)
  </script>
  