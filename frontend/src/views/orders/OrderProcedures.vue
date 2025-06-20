<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import procedureAPI from '@/api/procedures'
import { useAuthStore } from '@/store/authStore'
// 新增导入
import logsAPI from '@/api/logs'
import authAPI from '@/api/auth'
import { ElMessage, ElNotification, ElDialog, ElInput } from 'element-plus'

const route = useRoute()
const orderId = ref(route.params.order_id || '')
const procedures = ref([])
const newProcedureDialog = ref(false)
const newProcedureText = ref('')

const userStore = useAuthStore()
const isWorker = ref(localStorage.getItem('userType')  === 'worker')
// 检查 localStorage 中 userType 的实际值
//console.log('当前存储的用户类型:', localStorage.getItem('userType'))
//console.log('当前用户类型:', userStore.usertype)

// 状态映射表
const statusMap = {
  0: { text: '未开始', color: 'info' },
  1: { text: '进行中', color: 'processing' },
  2: { text: '已完成', color: 'success' }
}

// 新增响应式变量
const logDialogVisible = ref(false)
const logForm = ref({
  consumption: '',
  cost: 0,
  duration: 0
})
const currentWorkerId = ref('')
// 新增响应式变量
const logs = ref([])

// 获取当前工人ID
const getWorkerId = async () => {
  try {
    const token = localStorage.getItem('token') || sessionStorage.getItem('token')
    console.log('getWorkerId 中 token:', token)
    if (token) {
      const userInfo = await authAPI.getCurrentUser(token)
      console.log('userInfo 返回值：', userInfo)
      console.log('返回的 userInfo 键：', Object.keys(userInfo))
      currentWorkerId.value = userInfo.user_id
      console.log('当前 worker ID:', currentWorkerId.value)
    }
  } catch (error) {
    console.error('getWorkerId 捕获到错误:', error)
    ElMessage.error(`获取用户信息失败: ${error?.response?.data?.detail || error.message}`)
  }
}

// 显示日志对话框
const showLogDialog = async () => {
  await getWorkerId()
  logDialogVisible.value = true
}

// 加载日志方法
const loadLogs = async () => {
  try {
    const res = await logsAPI.getWorkerLogs(1, 100) // 获取第一页，每页100条
    // 过滤当前订单的日志
    logs.value = res.data.filter(log => log.order_id === orderId.value)
  } catch (error) {
    ElMessage.error(`获取日志失败: ${error.message}`)
  }
}

// 提交日志
const submitLog = async () => {
  try {
    await logsAPI.createMaintenanceLog({
      order_id: orderId.value,
      worker_id: currentWorkerId.value,
      ...logForm.value
    })
    
    ElMessage.success('日志记录成功')
    logDialogVisible.value = false
    logForm.value = { consumption: '', cost: 0, duration: 0 }
  } catch (error) {
    ElMessage.error(`日志提交失败: ${error.response?.data?.detail || error.message}`)
  }
}
onMounted(async () => {
  if (!orderId.value) {
    ElNotification.error('缺少订单ID参数')
    return
  }
  
  try {
    await loadProcedures()
    if (isWorker.value) {
      await loadLogs() // 仅工人才加载日志
    }
  } catch (error) {
    ElMessage.error(`获取流程失败: ${error.message}`)
  }
})

// 加载维修流程
async function loadProcedures() {
  try {
    // 添加加载状态
    const res = await procedureAPI.getProcedures(orderId.value)
    
    // 响应数据校验
    if (!res?.data || !Array.isArray(res.data)) {
      throw new Error('无效的接口响应格式')
    }
    
    procedures.value = res.data
  } catch (error) {
    ElMessage.error(`加载失败: ${error.message}`)
    console.error('加载流程错误:', error)
    procedures.value = [] // 清空数据防止信息泄露
  }
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
    <!-- 添加用户身份标识 -->
    <div class="user-identity">
      <el-tag :type="isWorker ? 'primary' : 'success'" effect="dark">
        {{ isWorker ? '维修工人' : '客户' }}
      </el-tag>
      <h3 class="user-id">当前订单号：{{ orderId }}</h3>
    </div>
  </div>
  <div class="procedures-container">
    <!-- 添加新流程按钮 -->
    <div class="action-bar">
      <el-button 
        type="primary" 
        @click="newProcedureDialog = true"
        v-if="isWorker">
        添加维修流程
      </el-button>
       <!-- 新增日志按钮 -->
       <el-button 
        type="warning" 
        @click="showLogDialog"
        v-if="isWorker">
        记录日志
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
    <!-- 在现有流程表格下方添加日志表格 -->
  <div class="log-section" v-if="isWorker">
    <h3>维护日志记录</h3>
    <el-table :data="logs" style="width: 100%" border>
      <el-table-column prop="consumption" label="消耗材料" />
      <el-table-column label="费用(元)" width="120">
        <template #default="{ row }">¥{{ row.cost }}</template>
      </el-table-column>
      <el-table-column prop="duration" label="耗时(小时)" width="120" />
      <el-table-column label="记录时间" width="180">
        <template #default="{ row }">
          {{ new Date(row.log_time).toLocaleString() }}
        </template>
      </el-table-column>
    </el-table>
  </div>
    
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

     <!-- 新增日志对话框 -->
     <el-dialog v-model="logDialogVisible" title="填写维护日志">
      <el-form :model="logForm" label-width="100px">
        <el-form-item label="消耗材料" required>
          <el-input v-model="logForm.consumption" placeholder="例如：机油1L" />
        </el-form-item>
        <el-form-item label="费用(元)" required>
          <el-input-number v-model="logForm.cost" :min="0" :precision="2" />
        </el-form-item>
        <el-form-item label="耗时(小时)" required>
          <el-input-number v-model="logForm.duration" :min="0" :precision="1" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="logDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitLog">提交</el-button>
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