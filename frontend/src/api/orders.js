import axios from 'axios'

const API_BASE = 'http://localhost:8000/api/v1'

export default {
  // 创建订单
  async createOrder(orderData) {
    return axios.post(`${API_BASE}/orders/`, {
      ...orderData
    })
  },

  // 获取用户订单
  async getOrders({ page = 1, page_size = 20, status } = {}) {
    return axios.get(`${API_BASE}/orders/`, {
      params: {
        page,
        page_size,
        status_filter: status
      }
    })
  },

  // 添加订单反馈
  // 添加订单反馈 (优化版)
  async addFeedback(feedbackData) {
    try {
      const response = await axios.post(`${API_BASE}/orders/feedback`, feedbackData)
      return response.data
    } catch (error) {
      // 统一处理422验证错误
      if (error.response && error.response.status === 422) {
        const errors = error.response.data.detail.map(e => e.msg).join(', ')
        throw new Error(`验证失败: ${errors}`)
      }
      throw new Error('提交反馈失败，请稍后重试')
    }
  },

  // 加急订单
  async expediteOrder(orderId) {
    return axios.post(`${API_BASE}/orders/${orderId}/expedite`)
  },

  // 取消订单
  async cancelOrder(orderId) {
    return axios.delete(`${API_BASE}/orders/${orderId}`)
  }
}