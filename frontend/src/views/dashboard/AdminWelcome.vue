<template>
    <div class="admin-welcome">
      <div class="dashboard-header">
        <h1>欢迎回来，{{ userName }}</h1>
        <p>您可以通过以下快捷入口快速访问统计与管理功能</p>
      </div>
  
      <div class="quick-actions">
        <el-card class="action-card" @click="navigateTo('/dashboard/admin/users')">
          <i class="el-icon-user"></i>
          <h3>用户管理</h3>
          <p>查看并管理用户账户</p>
        </el-card>
  
        <el-card class="action-card" @click="navigateTo('/dashboard/admin/wages')">
          <i class="el-icon-money"></i>
          <h3>工资管理</h3>
          <p>查看工人工资明细</p>
        </el-card>
  
        <el-card class="action-card" @click="navigateTo('/dashboard/admin/stats/orders')">
          <i class="el-icon-document"></i>
          <h3>订单统计</h3>
          <p>查看各类订单数量和状态</p>
        </el-card>
  
        <el-card class="action-card" @click="navigateTo('/dashboard/admin/stats/cars')">
          <i class="el-icon-truck"></i>
          <h3>车辆统计</h3>
          <p>车辆品牌与类型分布</p>
        </el-card>
  
        <el-card class="action-card" @click="navigateTo('/dashboard/admin/stats/costs')">
          <i class="el-icon-s-data"></i>
          <h3>成本分析</h3>
          <p>分时间段查看各项成本</p>
        </el-card>
  
        <el-card class="action-card" @click="navigateTo('/dashboard/admin/stats/feedback')">
          <i class="el-icon-message-solid"></i>
          <h3>差评反馈</h3>
          <p>查看客户负面评价与建议</p>
        </el-card>
  
        <el-card class="action-card" @click="navigateTo('/dashboard/admin/stats/productivity')">
          <i class="el-icon-s-custom"></i>
          <h3>工人生产力</h3>
          <p>分析工人接单完成效率</p>
        </el-card>
  
        <el-card class="action-card" @click="navigateTo('/dashboard/admin/stats/workers')">
          <i class="el-icon-s-operation"></i>
          <h3>工人统计</h3>
          <p>查看工人注册与活跃状态</p>
        </el-card>
  
        <el-card class="action-card" @click="navigateTo('/dashboard/admin/stats/incomplete-orders')">
          <i class="el-icon-time"></i>
          <h3>未完成订单</h3>
          <p>查看长时间未完成的订单</p>
        </el-card>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted } from 'vue'
  import { useRouter } from 'vue-router'
  import { useAuthStore } from '@/store/authStore'
  
  const router = useRouter()
  const authStore = useAuthStore()
  
  const userName = ref('管理员')
  
  const navigateTo = (path) => {
    router.push(path)
  }
  
  onMounted(() => {
    userName.value = authStore.user?.name || '管理员'
  })
  </script>
  
  <style scoped lang="scss">
  .admin-welcome {
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
  