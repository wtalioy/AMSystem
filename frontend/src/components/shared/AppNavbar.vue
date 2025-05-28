<template>
    <nav class="app-navbar">
      <router-link to="/dashboard">仪表盘</router-link>
      <button @click="logout">退出登录</button>
    </nav>
  </template>
  
  <script setup>
  import { useAuthStore } from '@/store/authStore'
  
  const authStore = useAuthStore()
  const logout = () => authStore.logout()
  </script>