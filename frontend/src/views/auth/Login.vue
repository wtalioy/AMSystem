<template>
  <div class="login-container">
    <form @submit.prevent="handleLogin" class="login-form">
      <h2 class="form-title">用户登录</h2>
      
      <div class="form-group">
        <label>用户ID</label>
        <input 
          v-model="credentials.username" 
          type="text" 
          required
          class="form-input">
      </div>
      
      <div class="form-group">
        <label>密码</label>
        <input 
          v-model="credentials.password" 
          type="password" 
          required
          class="form-input">
      </div>
  
      <button type="submit" class="submit-btn">登录</button>
      <p class="auth-link">
        没有账号？<router-link to="/register/customer">立即注册</router-link>
      </p>
      <p v-if="error" class="error-message">{{ error }}</p>
    </form>
  </div>
</template>

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

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: #4a5568;
  font-weight: 500;
}

.form-input {
  width: 100%;
  padding: 12px 16px;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  font-size: 1rem;
  transition: border-color 0.3s ease;
}

.form-input:focus {
  outline: none;
  border-color: #63B3ED;
}

.submit-btn {
  width: 100%;
  padding: 12px;
  background-color: #4299E1;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.submit-btn:hover {
  background-color: #3182CE;
}

.error-message {
  color: #E53E3E;
  margin-top: 1rem;
  text-align: center;
  font-weight: 500;
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

@media (max-width: 480px) {
  .login-form {
    padding: 1.5rem;
    margin: 0 1rem;
  }
}
</style>

  <script setup>
  import { ref } from 'vue'
  import { useAuthStore } from '@/store/authStore'
  import { useRouter } from 'vue-router'
  
  const authStore = useAuthStore()
  const router = useRouter()
  const error = ref(null)
  
  const credentials = ref({
    username: '',
    password: ''
  })
  
  const handleLogin = async () => {
    try {
      await authStore.login(credentials.value)
      router.push('/dashboard')
    } catch (err) {
      error.value = err.message
    }
  }
  </script>