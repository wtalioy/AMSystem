<template>
    <div>
      <h2>未完成订单分析</h2>
      <el-table :data="orders" style="width: 100%">
        <el-table-column prop="order_id" label="订单号"/>
        <el-table-column prop="customer_name" label="客户"/>
        <el-table-column prop="status" label="状态"/>
        <el-table-column prop="created_at" label="创建时间"/>
      </el-table>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted } from 'vue'
  import orderAPI from '@/api/orders'
  
  const orders = ref([])
  
  onMounted(async () => {
    const res = await orderAPI.getOrders({ status: 'incomplete' })
    orders.value = res.data.results || []
  })
  </script>
  <style scoped>
  .incomplete-orders-table {
    margin-top: 20px;
  }
  </style>