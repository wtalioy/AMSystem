<template>
  <div class="failure-patterns">
    <h2>常见故障模式</h2>

    <!-- 故障模式表格 -->
    <el-table :data="patterns" style="width: 100%">
      <!-- 车型 -->
      <el-table-column prop="car_type" label="车型" />

      <!-- 总维修次数 -->
      <el-table-column prop="total_repairs" label="总维修次数" />

      <!-- 常见故障：将数组通过 join 方式展示为逗号分隔的字符串 -->
      <el-table-column label="常见故障">
        <template #default="{ row }">
          <span>{{ row.common_issues?.join('，') }}</span>
        </template>
      </el-table-column>

      <!-- 维修频率 -->
      <el-table-column prop="repair_frequency" label="维修频率" />
    </el-table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import failureAPI from '@/api/adminStats'

// 使用 ref 声明响应式数组用于存放接口数据
const patterns = ref([])

// 在组件挂载时调用接口获取数据
onMounted(async () => {
  try {
    // 调用后台接口获取故障模式分析数据
    const res = await failureAPI.getFailurePatterns()

    // 如果接口返回成功，则将数据赋值给 patterns
    patterns.value = res.data || []
  } catch (error) {
    console.error('获取故障模式数据失败：', error)
  }
})
</script>

<style scoped>
.failure-patterns {
  padding: 20px;
}
</style>
