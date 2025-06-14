<template>
    <div>
      <h2>维修成本分析</h2>
      <el-table :data="costs" style="width: 100%">
        <el-table-column prop="category" label="维修项目"/>
        <el-table-column prop="average_cost" label="平均成本"/>
      </el-table>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted } from 'vue'
  import costAPI from '@/api/adminStats'
  
  const costs = ref([])
  
  onMounted(async () => {
    const res = await costAPI.getCostAnalysis()
    costs.value = res.data || []
  })
  </script>
  
  <style scoped>
  .cost-analysis {
    padding: 20px;
  }
  </style>