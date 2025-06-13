<template>
  <div class="error-page">
    <el-result
      icon="warning"
      title="403 未授权"
      sub-title="抱歉，您无权访问此页面"
    >
      <template #extra>
        <el-button type="primary" @click="$router.push('/')">返回首页</el-button>
      </template>
    </el-result>
  </div>
</template>

<script setup>
import { ElResult, ElButton } from 'element-plus'
</script>

<style scoped>
.error-page {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>