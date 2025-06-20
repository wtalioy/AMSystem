<!-- WorkerWelcome.vue -->
<template>
  <div class="worker-welcome">
    <div class="dashboard-header">
      <h1>欢迎回来，{{ userName }}</h1>
      <p>您有 {{ pendingOrders }} 个待处理订单</p>
    </div>

    <div class="quick-actions">
      <el-card class="action-card" @click="navigateTo('/dashboard/worker/orders')">
        <i class="el-icon-notebook-2"></i>
        <h3>我的工单</h3>
        <p>查看当前分配订单</p>
      </el-card>

      <el-card class="action-card" @click="navigateTo('/dashboard/worker/orders/pending')">
        <i class="el-icon-alarm-clock"></i>
        <h3>待处理工单</h3>
        <p>处理新分配订单</p>
      </el-card>

      <el-card class="action-card" @click="navigateTo('/dashboard/worker/earnings')">
        <i class="el-icon-money"></i>
        <h3>收入统计</h3>
        <p>查看收入明细</p>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/authStore'
import workerOrdersAPI from '@/api/workerOrders'

const router = useRouter()
const authStore = useAuthStore()

const userName = ref('技师')
const pendingOrders = ref(0)

const navigateTo = (path) => {
  router.push(path)
}

// 获取待处理订单数量
const fetchPendingOrders = async () => {
  try {
    // 获取所有已分配订单
    const response = await workerOrdersAPI.getAllOrders({ 
      page: 1, 
      page_size: 100 // 假设待处理订单不会超过1000条
    })
    
    // 过滤出待处理订单（状态1为待处理）
    const pending = response.data.filter(order => order.status === 1)
    
    pendingOrders.value = pending.length
  } catch (error) {
    console.error('获取待处理订单失败:', error)
    // 在实际应用中，这里可以添加用户通知
    pendingOrders.value = 0
  }
}

onMounted(async () => {
  userName.value = authStore.user?.name || '技师'
  await fetchPendingOrders()
})
</script>

<style scoped lang="scss">
.worker-welcome {
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