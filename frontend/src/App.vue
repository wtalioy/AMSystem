<script setup>
import { RouterView } from 'vue-router'

import { useAuthStore } from '@/store/authStore'

const authStore = useAuthStore()
</script>

<template>
  <!-- 认证相关页面使用独立布局 -->
  <RouterView v-slot="{ Component }">
    <template v-if="$route.meta.requiresAuth">
      <DashboardLayout>
          <!-- 集成导航栏 -->
        <component :is="Component" />
      </DashboardLayout>
    </template>
    
    <!-- 登录/注册页面使用干净布局 -->
    <template v-else>
      <AuthLayout>
        <component :is="Component" />
      </AuthLayout>
    </template>
  </RouterView>
</template>

<style>
/* 全局基础样式 */
@import '@/assets/styles/main.scss';

#app {
  margin: 0 auto;
  font-weight: normal;
}
</style>