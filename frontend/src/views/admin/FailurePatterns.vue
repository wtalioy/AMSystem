<template>
    <div>
      <h2>常见故障模式</h2>
      <el-table :data="patterns" style="width: 100%">
        <el-table-column prop="issue" label="故障描述"/>
        <el-table-column prop="frequency" label="出现次数"/>
      </el-table>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted } from 'vue'
  import failureAPI from '@/api/adminStats'
  
  const patterns = ref([])
  
  onMounted(async () => {
    const res = await failureAPI.getFailurePatterns()
    patterns.value = res.data || []
  })
  </script>
  
  <style scoped>
  .failure-patterns {
    padding: 20px;
  }
  </style>