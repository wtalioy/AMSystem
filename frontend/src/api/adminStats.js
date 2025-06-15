import axios from 'axios'

const API_BASE = 'http://localhost:8000/api/v1'

export default {
  // 1. 获取订单列表（带分页与状态过滤）
  async getOrders({ page = 1, page_size = 20, status_filter = null } = {}) {
    return axios.get(`${API_BASE}/admin/orders`, {
      params: { page, page_size, status_filter }
    })
  },

  // 2. 获取车辆统计信息
  async getCarStatistics() {
    return axios.get(`${API_BASE}/admin/cars`)
  },

  // 3. 获取常见故障模式分析
  async getFailurePatterns() {
    return axios.get(`${API_BASE}/admin/vehicles/failure-patterns`)
  },

  // 4. 获取成本分析（按月或季度）
  async getCostAnalysis({ start_date, end_date, period_type = 'month' }) {
    return axios.get(`${API_BASE}/admin/costs/analysis`, {
      params: { start_date, end_date, period_type }
    })
  },

  // 5. 获取负面反馈（低评分订单与工人）
  async getNegativeFeedback(rating_threshold = 3) {
    return axios.get(`${API_BASE}/admin/feedback/negative`, {
      params: { rating_threshold }
    })
  },

  // 6. 获取工人生产力数据（按时间范围）
  async getWorkerProductivity({ start_date, end_date }) {
    return axios.get(`${API_BASE}/admin/workers/productivity`, {
      params: { start_date, end_date }
    })
  },

  // 7. 获取工人统计信息（人数、任务数、时长等）
  async getWorkerStatistics({ start_time, end_time }) {
    return axios.get(`${API_BASE}/admin/workers`, {
      params: { start_time, end_time }
    })
  },

  // 8. 获取未完成订单统计
  async getIncompleteOrders() {
    return axios.get(`${API_BASE}/admin/incomplete-orders`)
  },

  // 9. 新增用户管理相关接口
  // 新增用户管理接口
async getAllUsers({ page = 1, page_size = 20 } = {}) {
  return axios.get(`${API_BASE}/users/`, {
    params: { page, page_size }
  })
},

async deleteUser(user_id) {
  return axios.delete(`${API_BASE}/users/${user_id}`)
}
}
