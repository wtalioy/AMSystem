<template>
    <div class="pending-orders">
      <h2>待处理订单</h2>
      <el-table :data="orders" style="width: 100%">
        <el-table-column prop="order_id" label="订单号" />
        <el-table-column prop="description" label="描述" />
        <el-table-column label="操作">
          <template #default="{ row }">
            <el-button type="primary" @click="acceptOrder(row.order_id)">接受</el-button>
            <el-button type="danger" @click="rejectOrder(row.order_id)">拒绝</el-button>
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
      const res = await workerOrdersAPI.getAllOrders({
        page: 1,
        page_size: 100
      })
      orders.value = res.data.filter(item => item.status === 1)
    } catch (err) {
      ElMessage.error('获取待处理订单失败')
    }
  }
  
  const acceptOrder = async (orderId) => {
    try {
      await workerOrdersAPI.acceptOrder(orderId)
      ElMessage.success('已接受订单')
      fetchOrders()
    } catch {
      ElMessage.error('接受失败')
    }
  }
  
  const rejectOrder = async (orderId) => {
    try {
      await workerOrdersAPI.rejectOrder(orderId)
      ElMessage.success('已拒绝订单')
      fetchOrders()
    } catch {
      ElMessage.error('拒绝失败')
    }
  }
  
  onMounted(fetchOrders)
  </script>
  