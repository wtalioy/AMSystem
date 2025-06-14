<template>
    <div>
      <h2>工资管理</h2>
      <el-table :data="wages" style="width: 100%">
        <el-table-column prop="worker_id" label="工人ID"/>
        <el-table-column prop="worker_name" label="姓名"/>
        <el-table-column prop="month" label="月份"/>
        <el-table-column prop="amount" label="工资"/>
      </el-table>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted } from 'vue'
  import wageAPI from '@/api/adminStats'
  
  const wages = ref([])
  
  onMounted(async () => {
    const res = await wageAPI.getAllWages()
    wages.value = res.data.results || []
  })
  </script>
  
  <style scoped>
  .wage-management {
    padding: 20px;
  }
  </style>