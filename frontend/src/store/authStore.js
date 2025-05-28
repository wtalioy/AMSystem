import { defineStore } from 'pinia'
import authAPI from '@/api/auth'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || null,
    userType: localStorage.getItem('userType') || null
  }),

  actions: {
    async initialize() {
        const token = localStorage.getItem('token')
        if (token) {
          try {
            const { data } = await authAPI.testToken(token)
            this.userType = data.user_type
          } catch (error) {
            this.logout()
          }
        }
      },
    async login(credentials) {
      try {
        const res = await authAPI.login(credentials)
        localStorage.setItem('token', res.access_token)
        this.token = res.access_token
        
        // 验证令牌获取用户类型
        const { data } = await authAPI.testToken(res.access_token)
        this.userType = data.user_type
        localStorage.setItem('userType', data.user_type)
        
        return true
      } catch (error) {
        this.logout()
        throw error
      }
    },

    async registerCustomer(formData) {
      try {
        await authAPI.registerCustomer({
          user_name: formData.user_name,
          user_pwd: formData.user_pwd,
          user_type: 'customer'
        })
        return { success: true }
      } catch (error) {
        console.error('注册请求失败:', error)
        
        // 改进错误处理逻辑
        let errorMsg = '注册失败，请检查输入信息'
        
        if (error.response?.data?.detail) {
          // 提取后端返回的详细错误信息
          errorMsg = error.response.data.detail
            .map(d => d.msg)
            .join(', ')
        } else if (error.response?.data?.message) {
          errorMsg = error.response.data.message
        }
        
        throw new Error(errorMsg)
      }
    },

    logout() {
      localStorage.removeItem('token')
      localStorage.removeItem('userType')
      this.token = null
      this.userType = null
    }
  },

  getters: {
    isAuthenticated: (state) => !!state.token,
    currentUserType: (state) => state.userType
  }
})