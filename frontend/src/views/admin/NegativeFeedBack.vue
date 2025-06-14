<template>
    <div>
      <h2>客户负面反馈</h2>
      <el-table :data="feedbacks" style="width: 100%">
        <el-table-column prop="customer" label="客户"/>
        <el-table-column prop="comment" label="反馈内容"/>
        <el-table-column prop="date" label="日期"/>
      </el-table>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted } from 'vue'
  import feedbackAPI from '@/api/adminStats'
  
  const feedbacks = ref([])
  
  onMounted(async () => {
    const res = await feedbackAPI.getNegativeFeedback()
    feedbacks.value = res.data || []
  })
  </script>
  
  <style scoped>
  .feedback-table {
    margin-top: 20px;
  }
  </style>