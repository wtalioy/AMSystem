<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import procedureAPI from '@/api/procedures'
import { useAuthStore } from '@/store/authStore'
import { ElMessage, ElNotification, ElDialog, ElInput } from 'element-plus'

const route = useRoute()
const orderId = ref(route.params.order_id || '')
const procedures = ref([])
const newProcedureDialog = ref(false)
const newProcedureText = ref('')

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
    await loadProcedures()
  } catch (error) {
    ElMessage.error(`获取流程失败: ${error.message}`)
  }
})

// 加载维修流程
async function loadProcedures() {
  const res = await procedureAPI.getProcedures(orderId.value)
  procedures.value = res.data
}

// 添加新维修流程
async function addNewProcedure() {
  if (!newProcedureText.value.trim()) {
    ElMessage.warning('请输入维修流程描述')
    return
  }
  
  try {
    // 创建新流程
    await procedureAPI.createProcedures([{
      order_id: orderId.value,
      procedure_text: newProcedureText.value
    }])
    
    // 刷新列表
    await loadProcedures()
    
    ElMessage.success('维修流程添加成功')
    newProcedureText.value = ''
    newProcedureDialog.value = false
  } catch (error) {
    ElMessage.error(`添加失败: ${error.message}`)
  }
}

// 更新流程状态
async function updateProcedureStatus(procedure, newStatus) {
  try {
    await procedureAPI.updateProcedureStatuses([{
      order_id: orderId.value,
      procedure_id: procedure.procedure_id,
      current_status: newStatus
    }])
    
    // 更新本地状态
    procedure.current_status = newStatus
    ElMessage.success('状态更新成功')
  } catch (error) {
    ElMessage.error(`更新失败: ${error.message}`)
  }
}
</script>

<template>
  <div class="procedures-container">
    <!-- 添加新流程按钮 -->
    <div class="action-bar">
      <el-button 
        type="primary" 
        @click="newProcedureDialog = true"
        v-if="isWorker">
        添加维修流程
      </el-button>
    </div>
    
    <!-- 维修流程表格 -->
    <el-table :data="procedures" style="width: 100%">
      <el-table-column prop="procedure_text" label="维修步骤" />
      
      <el-table-column label="状态" width="120">
        <template #default="{ row }">
          <el-tag :type="statusMap[row.current_status]?.color || ''">
            {{ statusMap[row.current_status]?.text || row.current_status }}
          </el-tag>
        </template>
      </el-table-column>
      
      <el-table-column label="操作" width="200" v-if="isWorker">
        <template #default="{ row }">
          <el-button 
            size="small" 
            :type="row.current_status === 0 ? 'primary' : 'info'"
            @click="updateProcedureStatus(row, row.current_status === 0 ? 1 : 0)"
            :disabled="row.current_status === 2">
            {{ row.current_status === 0 ? '开始' : '暂停' }}
          </el-button>
          
          <el-button 
            type="success" 
            size="small" 
            @click="updateProcedureStatus(row, 2)"
            :disabled="row.current_status === 2">
            完成
          </el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <!-- 添加新流程对话框 -->
    <el-dialog v-model="newProcedureDialog" title="添加维修流程">
      <el-input 
        v-model="newProcedureText" 
        placeholder="请输入维修流程描述"
        type="textarea"
        :rows="4"
      />
      <template #footer>
        <el-button @click="newProcedureDialog = false">取消</el-button>
        <el-button type="primary" @click="addNewProcedure">添加</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.action-bar {
  margin-bottom: 20px;
  text-align: right;
}
</style>