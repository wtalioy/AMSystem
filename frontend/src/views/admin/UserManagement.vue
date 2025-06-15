<template>
  <div class="user-management">
    <h2>用户管理</h2>
    <el-table :data="users" style="width: 100%">
      <el-table-column prop="user_id" label="用户ID" width="120"/>
      <el-table-column prop="user_name" label="用户名"/>
      <el-table-column prop="user_type" label="用户类型"/>
      <el-table-column prop="worker_type" label="工人类型" v-if="showWorkerColumn"/>
      <el-table-column prop="availability_status" label="状态">
        <template #default="{ row }">
          {{ statusMap[row.availability_status] || '未知' }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="120">
        <template #default="{ row }">
          <el-button 
            type="danger" 
            size="small"
            @click="handleDelete(row.user_id)"
            icon="Delete"
          >删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <!-- 分页控件 -->
    <el-pagination
      v-model:current-page="currentPage"
      :page-size="pageSize"
      layout="total, prev, pager, next, jumper"
      :total="totalUsers"
      @current-change="fetchUsers"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import userAPI from '@/api/adminStats'

const users = ref([])
const currentPage = ref(1)
const pageSize = ref(20)
const totalUsers = ref(0)

// 状态映射
const statusMap = {
  0: '离线',
  1: '在线',
  2: '忙碌'
}

// 检查是否需要显示工人类型列
const showWorkerColumn = computed(() => {
  return users.value.some(user => user.worker_type)
})

// 获取用户数据
const fetchUsers = async () => {
  try {
    const res = await userAPI.getAllUsers({
      page: currentPage.value,
      page_size: pageSize.value
    })
    users.value = res.data || []
    totalUsers.value = res.data?.total || res.data?.length || 0
  } catch (error) {
    ElMessage.error('获取用户数据失败: ' + error.message)
  }
}

// 删除用户
const handleDelete = (userId) => {
  ElMessageBox.confirm(
    `确定要删除用户 ${userId} 吗？此操作不可恢复！`,
    '警告',
    {
      confirmButtonText: '确认',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await userAPI.deleteUser(userId)
      ElMessage.success('用户删除成功')
      // 刷新当前页数据
      fetchUsers()
    } catch (error) {
      ElMessage.error('删除失败: ' + error.message)
    }
  }).catch(() => {
    // 取消操作
  })
}

onMounted(fetchUsers)
</script>

<style scoped>
.user-management {
  padding: 20px;
}

.el-pagination {
  margin-top: 20px;
  justify-content: center;
}
</style>