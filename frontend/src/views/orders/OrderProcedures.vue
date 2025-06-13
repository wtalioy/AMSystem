<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import procedureAPI from '@/api/procedures'
import { useAuthStore } from '@/store/authStore' // 假设你用 Pinia 或 Vuex 管理用户登录信息

const route = useRoute()
const orderId = route.params.order_id
const procedures = ref([])

const userStore = useAuthStore()
const isWorker = userStore.usertype === 'worker'

onMounted(async () => {
  const res = await procedureAPI.getProcedures(orderId)
  procedures.value = res.data
})

function recordNote(procedure) {
  const note = prompt('请输入工作记录：')
  if (note) {
    procedureAPI.recordProcedureNote(orderId, procedure.procedure_id, note)
      .then(() => ElMessage.success('记录成功'))
  }
}
</script>

<template>
  <el-table :data="procedures">
    <el-table-column prop="procedure_text" label="步骤" />
    <el-table-column prop="current_status" label="状态" />
    <!-- 工人额外操作按钮 -->
    <el-table-column v-if="isWorker" label="操作">
      <template #default="{ row }">
        <el-button type="primary" size="small" @click="recordNote(row)">
          记录
        </el-button>
      </template>
    </el-table-column>
  </el-table>
</template>
