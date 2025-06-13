// 登录/注册接口封装

import axios from 'axios'

const API_BASE = 'http://localhost:8000/api/v1'

export default {
  // 登录接口
  async login(credentials) {
    const response = await axios.post(`${API_BASE}/auth/login`, {
      user_name: credentials.username,
      user_pwd: credentials.password
    })
    return response.data
  },

  // 客户注册接口
  async registerCustomer(data) {
    return axios.post(`${API_BASE}/users/register`, {
      user_name: data.user_name,  // 使用后端要求的字段名
      user_pwd: data.user_pwd,    // 使用后端要求的字段名
      user_type: 'customer' ,      // 使用后端要求的字段名
      worker_type: null         //工人特定字段, 客户没有这个字段
    })
  },
  // 管理员注册接口
  async registerAdmin(data) {
    return axios.post(`${API_BASE}/users/register`, {
      user_name: data.user_name,
      user_pwd: data.user_pwd,
      user_type: 'administrator',
      worker_type: null      // 管理员没有工人类型字段
    })
  },

   // 新增获取工人类型接口
   async getWorkerTypes() {
    return axios.get(`${API_BASE}/users/worker-types`)
   },

  // 工人注册接口
  async registerWorker(data) {
    return axios.post(`${API_BASE}/users/register`, {
      user_name: data.user_name,
      user_pwd: data.user_pwd,
      user_type: 'worker',
      worker_type: data.worker_type  // 工人特有字段
    })
  },

  // 测试令牌接口
  async testToken(token) {
    return axios.get(`${API_BASE}/auth/verify`, null, {
      headers: { Authorization: `Bearer ${token}` }
    })
  }
}