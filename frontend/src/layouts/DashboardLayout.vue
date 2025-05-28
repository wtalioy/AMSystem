<template>
    <div class="dashboard-layout">
      <!-- 集成导航栏 -->
      <AppNavbar />
  
      <!-- 主内容区域 -->
      <main class="content-wrapper">
        <!-- 添加面包屑导航 -->
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
  import { useRoute } from 'vue-router'
  import AppNavbar from '@/components/shared/AppNavbar.vue'
  
  const route = useRoute()
  
  const breadcrumbs = computed(() => {
    return route.matched
      .filter(record => record.meta?.breadcrumb)
      .map(record => ({
        path: record.path,
        name: record.meta.breadcrumb
      }))
  })
  </script>
  
  <style scoped lang="scss">
  @import "@/assets/styles/variables";
  
  .dashboard-layout {
    display: grid;
    grid-template-rows: auto 1fr;
    min-height: 100vh;
    background: $color-background;
  
    .content-wrapper {
      padding: 1.5rem 2rem;
      overflow-y: auto;
    }
  
    .breadcrumb {
      margin-bottom: 1.5rem;
      
      &-item {
        color: $color-text-secondary;
        font-size: 0.9rem;
        
        &:not(:last-child)::after {
          content: "›";
          margin: 0 0.5rem;
        }
        
        &:last-child {
          color: $color-primary;
          font-weight: 500;
        }
      }
    }
  
    .content-container {
      background: white;
      border-radius: 8px;
      padding: 2rem;
      box-shadow: $shadow-sm;
    }
  }
  
  .slide-fade-enter-active {
    transition: all 0.3s ease-out;
  }
  
  .slide-fade-leave-active {
    transition: all 0.2s cubic-bezier(1, 0.5, 0.8, 1);
  }
  
  .slide-fade-enter-from,
  .slide-fade-leave-to {
    transform: translateX(20px);
    opacity: 0;
  }
  </style>