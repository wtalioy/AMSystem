<template>
    <div class="my-orders">
      <h2>我的订单</h2>
      <el-table :data="orders" style="width: 100%">
        <el-table-column prop="order_id" label="订单号" />
        <el-table-column prop="description" label="描述" />
        <el-table-column prop="status" label="状态" :formatter="formatStatus" />
        <el-table-column label="操作">
          <template #default="{ row }">
            <el-button type="success" @click="completeOrder(row.order_id)" v-if="row.status === 1">完成订单</el-button>
            <router-link :to="`/worker/orders/${row.order_id}/logs`">
              <el-button type="info">维护日志</el-button>
            </router-link>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted } from 'vue'
  import workerOrdersAPI from '@/api/workerOrders'
  import { ElMessage } from 'element-plus'
  
  const orders = ref([])
  
  const fetchOrders = async () => {
    try {
      const res = await workerOrdersAPI.getAssignedOrders()
      orders.value = res
    } catch (err) {
      ElMessage.error('获取订单失败')
    }
  }
  
  const completeOrder = async (orderId) => {
    try {
      await workerOrdersAPI.completeOrder(orderId)
      ElMessage.success('订单已完成')
      fetchOrders()
    } catch {
      ElMessage.error('完成订单失败')
    }
  }
  
  const formatStatus = (row, column, value) => {
    return ['待处理', '进行中', '已完成'][value] || '未知'
  }
  
  onMounted(fetchOrders)
  </script>