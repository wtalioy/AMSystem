import axios from 'axios'

const API_BASE = 'http://localhost:8000/api/v1'

export default {
  // 1. 获取当前工人已分配订单
  async getAssignedOrders({ page = 1, page_size = 20, status_filter = null }) {
    return axios.get(`${API_BASE}/workers/orders/assigned`, {
      params: { page, page_size, status_filter }
    })
  },

  // 2. 接受订单
  async acceptOrder(order_id) {
    return axios.post(`${API_BASE}/workers/orders/${order_id}/accept`)
  },

  // 3. 拒绝订单
  async rejectOrder(order_id) {
    return axios.post(`${API_BASE}/workers/orders/${order_id}/reject`)
  },

  // 4. 完成订单
  async completeOrder(order_id) {
    return axios.post(`${API_BASE}/workers/orders/${order_id}/complete`)
  },

  // 5. 获取本月收入
  async getMonthlyEarnings({ year, month }) {
    return axios.get(`${API_BASE}/workers/my-earnings/monthly`, {
      params: { year, month }
    })
  },

  // 6. 获取收入历史
  async getEarningsHistory({ months_back = 12 }) {
    return axios.get(`${API_BASE}/workers/my-earnings/history`, {
      params: { months_back }
    })
  }
}