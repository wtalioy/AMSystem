<template>
    <div>
      <h2>工人统计</h2>
      <el-table :data="workers" style="width: 100%">
        <el-table-column prop="id" label="工人ID"/>
        <el-table-column prop="name" label="姓名"/>
        <el-table-column prop="total_orders" label="接单总数"/>
      </el-table>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted } from 'vue'
  import statsAPI from '@/api/adminStats'
  
  const workers = ref([])
  
  onMounted(async () => {
    const res = await statsAPI.getWorkerStatistics()
    workers.value = res.data || []
  })
  </script>
  
  <style scoped>
  .worker-stats-table {
    margin-top: 20px;
  }
  </style>