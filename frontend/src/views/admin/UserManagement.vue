<template>
    <div>
      <h2>用户管理</h2>
      <el-table :data="users" style="width: 100%">
        <el-table-column prop="id" label="用户ID" width="80"/>
        <el-table-column prop="name" label="姓名"/>
        <el-table-column prop="type" label="用户类型"/>
        <el-table-column prop="email" label="邮箱"/>
      </el-table>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted } from 'vue'
  import userAPI from '@/api/adminStats'
  
  const users = ref([])
  
  onMounted(async () => {
    const res = await userAPI.getAllUsers()
    users.value = res.data.results || []
  })
  </script>
  
  <style scoped>
  .user-management {
    padding: 20px;
  }
  </style>