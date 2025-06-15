<template>
  <div class="car-statistics">
    <h2>车辆统计</h2>
    <el-table :data="cars" style="width: 100%">
      <el-table-column prop="car_type" label="车型" />
      <el-table-column prop="car_count" label="车辆数量" align="right" />
      <el-table-column prop="repair_count" label="维修次数" align="right" />
      <el-table-column label="平均维修成本" align="right">
        <template #default="{ row }">
          {{ formatCost(row.average_repair_cost) }}
        </template>
      </el-table-column>
      <el-table-column label="维修频率" align="center">
        <template #default="{ row }">
          <el-tag :type="getFrequencyType(row.repair_frequency)">
            {{ row.repair_frequency.toFixed(2) }}次/年
          </el-tag>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus' // 添加这行
import statsAPI from '@/api/adminStats'

const cars = ref([])

// 货币格式化函数
const formatCost = (cost) => {
  if (!cost) return '¥0.00'
  // 如果已经是¥符号开头，直接返回
  if (cost.startsWith('¥')) return cost
  // 如果是数字字符串，转换为货币格式
  const number = parseFloat(cost)
  return isNaN(number) ? cost : `¥${number.toFixed(2)}`
}

// 维修频率标签类型
const getFrequencyType = (frequency) => {
  if (frequency > 3) return 'danger'
  if (frequency > 1.5) return 'warning'
  return 'success'
}

onMounted(async () => {
  try {
    const res = await statsAPI.getCarStatistics()
    
    // 更健壮的数据处理
    cars.value = Array.isArray(res?.data?.data) 
      ? res.data.data 
      : []
    
    // 调试输出
    console.log('车辆统计数据:', cars.value)
  } catch (error) {
    console.error('获取车辆统计失败:', error)
    ElMessage.error('数据加载失败')
  }
})
</script>

<style scoped>
.car-statistics {
  padding: 20px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

h2 {
  margin-bottom: 20px;
  color: #333;
  font-weight: 600;
}
</style>