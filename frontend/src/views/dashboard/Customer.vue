<!-- Customer.vue -->
<template>
    <div class="customer-dashboard">
      <router-view></router-view> <!-- 只作为子页面容器 -->
    </div>
  </template>
  
  <script setup>
  // 无需任何逻辑
  </script>
  
  <style scoped>
  .customer-dashboard {
    padding: 20px;
  }
  </style>
  