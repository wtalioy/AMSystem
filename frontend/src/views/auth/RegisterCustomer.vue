<template>
  <div class="login-container">
    <div class="login-form">
      <h2 class="form-title">用户注册</h2>
      <RoleBasedForm role="customer" @submit="handleRegister"/>
      
      <!-- 显示错误消息 -->
      <div v-if="errorMessage" class="error-message">
        {{ errorMessage }}
      </div>
      
      <p class="auth-link">
        已有账号？<router-link to="/login">立即登录</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import RoleBasedForm from '@/components/auth/RoleBasedForm.vue'
import { useAuthStore } from '@/store/authStore'
import { useRouter } from 'vue-router'
import { ref } from 'vue'

const authStore = useAuthStore()
const router = useRouter()
const errorMessage = ref(null)

const handleRegister = async (formData) => {
  errorMessage.value = null // 重置错误消息
  
  try {
    // 直接传递表单数据，字段映射在authStore中处理
    const result = await authStore.registerCustomer({
      user_name: formData.username,
      user_pwd: formData.password
    })
    
    if (result?.success) {
      router.push('/login')
    }
  } catch (error) {
    console.error('注册失败:', error)
    errorMessage.value = error.message
  }
}
</script>
<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #87CEEB, #E0F6FF);
}

.login-form {
  background: rgba(255, 255, 255, 0.95);
  padding: 2.5rem;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 400px;
}

.form-title {
  text-align: center;
  color: #2c3e50;
  margin-bottom: 2rem;
  font-size: 1.8rem;
}

.auth-link {
  text-align: center;
  margin-top: 1.5rem;
  color: #4a5568;
  
  a {
    color: #4299E1;
    font-weight: 500;
    &:hover {
      text-decoration: underline;
    }
  }
}

/* 添加错误消息样式 */
.error-message {
  color: #e53e3e;
  text-align: center;
  margin-top: 1rem;
  font-size: 0.875rem;
}
</style>