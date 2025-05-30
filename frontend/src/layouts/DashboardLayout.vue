<template>
  <div class="dashboard-layout">
    <!-- 顶部导航栏 -->
    <header class="dashboard-header">
      <div class="branding">
        <h1>汽车维修管理系统</h1>
      </div>
      
      <!-- 用户信息及操作区 -->
      <div class="user-actions">
        <!-- 用户身份展示 -->
        <span class="user-type" v-if="userTypeDisplay">
          <i class="user-icon" :class="userIconClass"></i>
          {{ userTypeDisplay }}
        </span>
        
        <!-- 退出登录按钮 -->
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
        <!-- ... 面包屑内容保持不变 ... -->
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

const authStore = useAuthStore()
const router = useRouter()

// 计算用户类型显示文本
const userTypeDisplay = computed(() => {
  switch(authStore.userType) {
    case 'customer': return '客户'
    case 'worker': return '维修技师'
    case 'admin': return '系统管理员'
    default: return null
  }
})

// 计算用户图标类名
const userIconClass = computed(() => {
  switch(authStore.userType) {
    case 'customer': return 'icon-customer'
    case 'worker': return 'icon-worker'
    case 'admin': return 'icon-admin'
    default: return ''
  }
})

// 退出登录处理
const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}
</script>

<style scoped lang="scss">
.dashboard-layout {
  display: grid;
  grid-template-rows: auto 1fr;
  min-height: 100vh;
  background: var(--color-background);

  .dashboard-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 2rem;
    height: 60px;
    background: white;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    
    .branding h1 {
      font-size: 1.2rem;
      color: var(--color-primary);
    }
    
    .user-actions {
      display: flex;
      align-items: center;
      gap: 1.5rem;
      
      .user-type {
        display: flex;
        align-items: center;
        font-size: 0.9rem;
        color: var(--color-text-secondary);
        
        .user-icon {
          display: inline-block;
          width: 18px;
          height: 18px;
          margin-right: 0.5rem;
          background-size: contain;
          
          &.icon-customer {
            background-image: url('@/assets/icons/user-customer.svg');
          }
          &.icon-worker {
            background-image: url('@/assets/icons/user-worker.svg');
          }
          &.icon-admin {
            background-image: url('@/assets/icons/user-admin.svg');
          }
        }
      }
      
      .logout-btn {
        display: flex;
        align-items: center;
        padding: 0.5rem 1rem;
        background: #f8f9fa;
        border: 1px solid #e2e8f0;
        border-radius: 6px;
        color: var(--color-text-secondary);
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
          background-image: url('@/assets/icons/logout.svg');
          background-size: contain;
        }
      }
    }
  }
  
  .content-wrapper {
    padding: 1.5rem 2rem;
    overflow-y: auto;
  }
  
  /* 其他样式保持不变... */
}
</style>