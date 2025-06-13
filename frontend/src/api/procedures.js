// src/api/procedures.js
import axios from 'axios'

const API_BASE = 'http://localhost:8000/api/v1'

export default {
  // 获取某订单的所有维修流程
  async getProcedures(order_id) {
    return axios.get(`${API_BASE}/procedures/`, {
      params: { order_id }
    })
  },

  // 创建多个流程（POST 接收数组）
  async createProcedures(procedureList) {
    return axios.post(`${API_BASE}/procedures/`, procedureList)
  },

  // 批量更新流程状态（PATCH 接收数组）
  async updateProcedureStatuses(procedureList) {
    return axios.patch(`${API_BASE}/procedures/`, procedureList)
  },

  // 工人记录工作内容（比如为某个流程添加记录备注）
  async recordProcedureNote(order_id, procedure_id, note) {
    return axios.post(`${API_BASE}/procedures/record`, {
      order_id,
      procedure_id,
      note
    })
  }
}
