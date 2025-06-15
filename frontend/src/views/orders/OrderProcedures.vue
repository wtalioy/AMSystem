<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import procedureAPI from '@/api/procedures'
import { useAuthStore } from '@/store/authStore'
import { ElMessage, ElNotification } from 'element-plus' // 引入通知组件

const route = useRoute()
// 更安全的参数获取方式（带默认值）
const orderId = ref(route.params.order_id || '')
const procedures = ref([])

const userStore = useAuthStore()
const isWorker = userStore.usertype === 'worker'

// 状态映射表
const statusMap = {
  0: { text: '未开始', color: 'info' },
  1: { text: '进行中', color: 'primary' },
  2: { text: '已完成', color: 'success' }
}

onMounted(async () => {
  if (!orderId.value) {
    ElNotification.error('缺少订单ID参数')
    return
  }
  
  try {
    const res = await procedureAPI.getProcedures(orderId.value)
    procedures.value = res.data
  } catch (error) {
    ElMessage.error(`获取流程失败: ${error.message}`)
  }
})

async function recordNote(procedure) {
  const note = prompt('请输入工作记录：')
  if (!note) return
  
  try {
    // 注意：这里使用实际存在的更新接口
    await procedureAPI.updateProcedureStatuses([{
      order_id: orderId.value,
      procedure_id: procedure.procedure_id,
      note_content: note,  // 假设后端支持备注字段
      current_status: 1    // 标记为进行中
    }])
    
    // 更新本地数据
    procedure.note_content = note
    procedure.current_status = 1
    ElMessage.success('记录成功')
  } catch (error) {
    ElMessage.error(`记录失败: ${error.message}`)
  }
}
</script>

<template>
  <el-table :data="procedures" style="width: 100%">
    <el-table-column prop="procedure_text" label="维修步骤" width="180" />
    
    <el-table-column label="状态">
      <template #default="{ row }">
        <el-tag :type="statusMap[row.current_status]?.color || ''">
          {{ statusMap[row.current_status]?.text || row.current_status }}
        </el-tag>
      </template>
    </el-table-column>
    
    <el-table-column label="备注">
      <template #default="{ row }">
        {{ row.note_content || '--' }}
      </template>
    </el-table-column>
    
    <el-table-column v-if="isWorker" label="操作" width="120">
      <template #default="{ row }">
        <el-button 
          type="primary" 
          size="small" 
          @click="recordNote(row)"
          :disabled="row.current_status === 2">
          记录
        </el-button>
      </template>
    </el-table-column>
  </el-table>
</template>