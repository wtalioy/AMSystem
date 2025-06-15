<template>
    <div class="error-page">
      <el-result
        icon="error"
        title="404 页面不存在"
        sub-title="您访问的页面可能已丢失或不存在"
      >
        <template #extra>
          <el-button type="primary" @click="$router.go(-1)">返回上一页</el-button>
        </template>
      </el-result>
    </div>
  </template>
  
  <script setup>
  import { ElResult, ElButton } from 'element-plus'
  </script>
  
  <style scoped>
  .error-page {
    height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  </style>