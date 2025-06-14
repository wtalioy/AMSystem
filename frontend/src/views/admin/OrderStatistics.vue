<template>
    <div>
      <h2>订单统计</h2>
      <el-table :data="orders" style="width: 100%">
        <el-table-column prop="status" label="订单状态"/>
        <el-table-column prop="count" label="数量"/>
      </el-table>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted } from 'vue'
  import statsAPI from '@/api/adminStats'
  
  const orders = ref([])
  
  onMounted(async () => {
    const res = await statsAPI.getOrderStatistics()
    orders.value = res.data || []
  })
  </script>
  
  <style scoped>
  .order-statistics {
    padding: 20px;
  }
  </style>