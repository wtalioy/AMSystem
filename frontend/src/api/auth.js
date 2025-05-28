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
    return axios.post(`${API_BASE}/users/customers`, {
      user_name: data.user_name,  // 使用后端要求的字段名
      user_pwd: data.user_pwd,    // 使用后端要求的字段名
      user_type: 'customer'       // 使用后端要求的字段名
    })
  },

  // 测试令牌接口
  async testToken(token) {
    return axios.get(`${API_BASE}/auth/verify`, null, {
      headers: { Authorization: `Bearer ${token}` }
    })
  }
}