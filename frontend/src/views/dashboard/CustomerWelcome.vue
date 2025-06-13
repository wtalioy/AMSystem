<!-- CustomerWelcome.vue -->
<template>
    <div class="customer-welcome">
      <!-- 欢迎信息和仪表盘导航 -->
      <div class="dashboard-header">
        <h1>欢迎回来，{{ userName }}</h1>
        <p>您有 {{ carCount }} 辆注册车辆，最近有 {{ pendingOrders }} 个待处理订单</p>
      </div>
  
      <!-- 快捷操作卡片 -->
      <div class="quick-actions">
        <el-card class="action-card" @click="navigateTo('/dashboard/customer/cars')">
          <i class="el-icon-truck"></i>
          <h3>我的车辆</h3>
          <p>查看和管理您的车辆</p>
        </el-card>
  
        <el-card class="action-card" @click="navigateTo('/dashboard/customer/orders/create')">
          <i class="el-icon-document-add"></i>
          <h3>创建新订单</h3>
          <p>提交新的维修服务请求</p>
        </el-card>
  
        <el-card class="action-card" @click="navigateTo('/dashboard/customer/orders')">
          <i class="el-icon-notebook-2"></i>
          <h3>历史订单</h3>
          <p>查看您的维修历史记录</p>
        </el-card>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted } from 'vue'
  import { useRouter } from 'vue-router'
  import { useAuthStore } from '@/store/authStore'
  import carApi from '@/api/cars'
  
  const router = useRouter()
  const authStore = useAuthStore()
  
  const userName = ref('客户')
  const carCount = ref(0)
  const pendingOrders = ref(0)
  
  const navigateTo = (path) => {
    router.push(path)
  }
  
  onMounted(async () => {
    userName.value = authStore.user?.name || '客户'
    try {
      const res = await carApi.getCars()
      carCount.value = res.data?.results?.length || 0
      pendingOrders.value = 2
    } catch (error) {
      console.error('获取仪表盘数据失败:', error)
    }
  })
  </script>
  
  <style scoped lang="scss">
  .customer-welcome {
    padding: 20px;
  
    .dashboard-header {
      margin-bottom: 30px;
  
      h1 {
        font-size: 1.8rem;
        color: #333;
        margin-bottom: 10px;
      }
  
      p {
        color: #666;
        font-size: 1rem;
      }
    }
  
    .quick-actions {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 20px;
      margin-bottom: 30px;
  
      .action-card {
        cursor: pointer;
        transition: transform 0.3s, box-shadow 0.3s;
        text-align: center;
        padding: 20px;
  
        &:hover {
          transform: translateY(-5px);
          box-shadow: 0 6px 18px rgba(0, 0, 0, 0.1);
        }
  
        i {
          font-size: 2.5rem;
          color: #409EFF;
          margin-bottom: 15px;
        }
  
        h3 {
          margin: 10px 0;
          color: #333;
        }
  
        p {
          color: #888;
          font-size: 0.9rem;
        }
      }
    }
  }
  </style>
  