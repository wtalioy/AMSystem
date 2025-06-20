<template>
  <div class="dashboard-layout">
    <!-- 顶部用户信息栏 -->
    <header class="user-header">
      <div class="header-left" @click="goToDashboard">
        <h1 class="system-title">汽车维修管理系统</h1>
      </div>
      
      <div class="user-info">
        <span class="user-type" @click="goToProfile">
          <i class="user-icon"></i>
          {{ userTypeDisplay }}
        </span>
        <button @click="handleLogout" class="logout-btn">
          <i class="logout-icon"></i>
          退出登录
        </button>
      </div>
    </header>

    <!-- 主内容区域 -->
    <main class="content-wrapper">
      <!-- 面包屑导航 -->
      <div class="breadcrumb">
        <router-link 
          v-for="(crumb, index) in breadcrumbs" 
          :key="index"
          :to="crumb.path"
          class="breadcrumb-item"
        >
          {{ crumb.name }}
        </router-link>
      </div>

      <!-- 内容容器 -->
      <div class="content-container">
        <router-view v-slot="{ Component }">
          <transition name="slide-fade">
            <component :is="Component" />
          </transition>
        </router-view>
      </div>
    </main>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/store/authStore'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

// 计算面包屑
const breadcrumbs = computed(() => {
  return route.matched
    .filter(record => record.meta?.breadcrumb)
    .map(record => ({
      path: record.path,
      name: record.meta.breadcrumb
    }))
})

// 计算用户类型显示文本
const userTypeDisplay = computed(() => {
  switch(authStore.userType) {
    case 'customer': return '客户'
    case 'worker': return '维修技师'
    case 'administrator': return '系统管理员'
    default: return '未知用户'
  }
})

// 新增返回主面板方法
const getMainDashboardPath = () => {
  switch(authStore.userType) {
    case 'customer':
      return '/dashboard/customer'
    case 'worker':
      return '/dashboard/worker' // 对应 WorkerDashboard 名称的路由
    case 'administrator':
      return '/dashboard/admin'
    default:
      return '/dashboard'
  }
}

const goToDashboard = () => {
  router.push(getMainDashboardPath())
}

// 新增跳转方法
const goToProfile = () => {
  const basePath = getMainDashboardPath() // 复用已有的路径获取方法
  router.push(`${basePath}/myinfo`)
}

// 退出登录处理
const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}
</script>

<style scoped lang="scss">
@use "@/assets/styles/_variables";

.dashboard-layout {
  display: grid;
  grid-template-rows: auto 1fr;
  min-height: 100vh;
  background: $color-background;

  .user-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 2rem;
    height: 60px;
    background: white;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);

    .header-left {
      cursor: pointer;
    }
    
    .system-title {
      font-size: 1.2rem;
      color: $color-primary;
    }
    
    .user-info {
      display: flex;
      align-items: center;
      gap: 1.5rem;
      
      .user-type {
        display: flex;
        align-items: center;
        font-size: 0.9rem;
        color: $color-text-secondary;
        cursor: pointer;
        
        .user-icon {
          display: inline-block;
          width: 18px;
          height: 18px;
          margin-right: 0.5rem;
          background-color: #4299E1;
          border-radius: 50%;
        }
      }
      
      .logout-btn {
        display: flex;
        align-items: center;
        padding: 0.5rem 1rem;
        background: #f8f9fa;
        border: 1px solid #e2e8f0;
        border-radius: 6px;
        color: $color-text-secondary;
        cursor: pointer;
        transition: all 0.2s;
        
        &:hover {
          background: #e53e3e;
          color: white;
          border-color: #e53e3e;
        }
        
        .logout-icon {
          display: inline-block;
          width: 16px;
          height: 16px;
          margin-right: 0.5rem;
          background-color: currentColor;
          mask: url('@/assets/icons/logout.svg') no-repeat center;
        }
      }
    }
  }
  
  .content-wrapper {
    padding: 1.5rem 2rem;
    overflow-y: auto;
  }
  
  /* 其他原有样式保持不变... */
}
</style>