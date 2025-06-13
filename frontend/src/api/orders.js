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
  async addFeedback(feedbackData) {
    return axios.post(`${API_BASE}/orders/feedback`, {
      ...feedbackData
    })
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