<script setup>
import { ref } from 'vue'
import { useAuthStore } from '@/store/authStore'
import { onMounted } from 'vue'

const authStore = useAuthStore()
onMounted(async () => {
  await authStore.fetchWorkerTypes()
})

defineProps({
  role: {
    type: String,
    required: true
  }
})

// 只保留API需要的字段
const formData = ref({
  username: '',
  password: '',
  workerType: ''
})
</script>


<template>
  <form @submit.prevent="$emit('register', formData)">
    <!-- 所有角色通用字段 -->
    <div class="form-group">
      <label>用户名</label>
      <input v-model="formData.username" required>
    </div>

    <div class="form-group">
      <label>密码</label>
      <input v-model="formData.password" type="password" required>
    </div>

    <!-- 工人特有字段 -->
    
<template v-if="role === 'worker'">
  <div class="form-group">
    <label>工种类型</label>
    <select v-model="formData.workerType" required>
      <option 
        v-for="(type) in authStore.workerTypes" 
        :key="type" 
        :value="type"
      >
        {{ type }}
      </option>
    </select>
  </div>
</template>

    <button type="submit" class="submit-btn">注册</button>
  </form>
</template>



<style scoped>
.form-group {
  margin-bottom: 1.5rem;
}

label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #4a5568;
}

input {
  box-sizing: border-box;
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #cbd5e0;
  border-radius: 0.375rem;
  font-size: 1rem;
}

.submit-btn {
  width: 100%;
  padding: 0.75rem;
  background-color: #4299E1;
  color: white;
  border: none;
  border-radius: 0.375rem;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
}

.submit-btn:hover {
  background-color: #3182ce;
}
</style>