<template>
    <div>
      <h2>工人生产力分析</h2>
      <el-table :data="workers" style="width: 100%">
        <el-table-column prop="name" label="姓名"/>
        <el-table-column prop="orders_completed" label="完成订单数"/>
        <el-table-column prop="avg_time" label="平均耗时（小时）"/>
      </el-table>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted } from 'vue'
  import productivityAPI from '@/api/adminStats'
  
  const workers = ref([])
  
  onMounted(async () => {
    const res = await productivityAPI.getWorkerProductivity()
    workers.value = res.data || []
  })
  </script>
  
  <style scoped>
  .worker-productivity-table {
    margin-top: 20px;
  }
  </style>