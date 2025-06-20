// src/api/logs.js
import axios from 'axios'

const API_BASE = 'http://localhost:8000/api/v1'

export default {
  // 创建维修日志
  async createMaintenanceLog(logData) {
    return axios.post(`${API_BASE}/logs/`, logData)
  },

  // 获取工人日志（带分页）
  async getWorkerLogs(page = 1, pageSize = 20) {
    return axios.get(`${API_BASE}/logs/`, {
      params: {
        page,
        page_size: pageSize
      }
    })
  }
}