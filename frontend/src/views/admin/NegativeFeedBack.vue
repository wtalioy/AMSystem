<template>
  <div class="feedback-table">
    <h2>客户负面反馈</h2>

    <!-- 显示低评分订单 -->
    <el-table :data="feedbacks" style="width: 100%">
      <!-- 订单 ID -->
      <el-table-column prop="order_id" label="订单ID" />

      <!-- 评分 -->
      <el-table-column prop="rating" label="评分" />

      <!-- 反馈内容 -->
      <el-table-column prop="comment" label="反馈内容" />

      <!-- 工人 ID -->
      <el-table-column prop="worker_id" label="工人ID" />

      <!-- 工人类型 -->
      <el-table-column prop="worker_type" label="工人类型" />

      <!-- 完成时间（格式化日期） -->
      <el-table-column label="完成时间">
        <template #default="{ row }">
          <span>{{ formatDate(row.completion_date) }}</span>
        </template>
      </el-table-column>

      <!-- 总花费 -->
      <el-table-column prop="total_cost" label="总花费" />
    </el-table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import feedbackAPI from '@/api/adminStats'

// 用于表格数据
const feedbacks = ref([])

// 工具函数：格式化 ISO 日期为 yyyy-mm-dd
const formatDate = (isoStr) => {
  const d = new Date(isoStr)
  return d.toLocaleDateString()
}

onMounted(async () => {
  try {
    // 获取低评分订单（默认评分阈值为 3）
    const res = await feedbackAPI.getNegativeFeedback(3)
    // 只取低评分订单部分
    feedbacks.value = res.data?.low_rated_orders || []
  } catch (error) {
    console.error('获取负面反馈失败：', error)
  }
})
</script>

<style scoped>
.feedback-table {
  margin-top: 20px;
}
</style>
