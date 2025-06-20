import axios from 'axios'

const API_BASE = 'http://localhost:8000/api/v1'

export default {
  // 1. 获取订单列表（带分页与状态过滤）
  async getOrderStatistics({ page = 1, page_size = 20, status_filter = null } = {}) {
    return axios.get(`${API_BASE}/admin/orders`, {
      params: { page, page_size, status_filter }
    })
  },

  // 2. 获取车辆统计信息
  async getCarStatistics() {
    return axios.get(`${API_BASE}/admin/car-statistics`)
  },

  // 3. 获取常见故障模式分析 // 已经被删除
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
},

  // 以下是工资管理相关接口

  // ================== 工资管理相关接口 ==================
  
  // 1. 获取单个工人月度收入
  /**
   * 获取指定工人的月度收入详情
   * @param {string} worker_id 工人ID
   * @param {number} year 年份
   * @param {number} month 月份 (1-12)
   * @returns {Promise} Axios响应对象
   */
  async getWorkerMonthlyEarnings(worker_id, year, month) {
    return axios.get(`${API_BASE}/earnings/individual/${worker_id}/monthly`, {
      params: { year, month }
    })
  },

  // 2. 获取工人收入历史
  /**
   * 获取指定工人的收入历史记录
   * @param {string} worker_id 工人ID
   * @param {number} [months_back=12] 回溯月份数 (1-24，默认12)
   * @returns {Promise} Axios响应对象
   */
  async getWorkerEarningsHistory(worker_id, months_back = 12) {
    return axios.get(`${API_BASE}/earnings/individual/${worker_id}/history`, {
      params: { months_back }
    })
  },

  // 3. 获取所有工人月度收入
  /**
   * 获取所有工人的月度收入数据
   * @param {number} year 年份
   * @param {number} month 月份 (1-12)
   * @returns {Promise} Axios响应对象
   */
  async getAllWorkersMonthlyEarnings(year, month) {
    return axios.get(`${API_BASE}/earnings/all`, {
      params: { year, month }
    })
  },

  // 4. 获取收入汇总报告
  /**
   * 获取月度收入汇总报告
   * @param {number} year 年份
   * @param {number} month 月份 (1-12)
   * @returns {Promise} Axios响应对象
   */
  async getEarningsSummaryReport(year, month) {
    return axios.get(`${API_BASE}/earnings/summary`, {
      params: { year, month }
    })
  },

  // 5. 执行月度工资发放
  /**
   * 手动触发月度工资发放
   * @param {number} year 年份
   * @param {number} month 月份 (1-12)
   * @returns {Promise} Axios响应对象
   */
  async runMonthlyDistribution(year, month) {
    return axios.post(`${API_BASE}/earnings/distribute`, null, {
      params: { year, month }
    })
  },

  // 6. 获取调度器状态
  /**
   * 获取工资发放调度器状态
   * @returns {Promise} Axios响应对象
   */
  async getSchedulerStatus() {
    return axios.get(`${API_BASE}/earnings/scheduler/status`)
  },

  // 7. 启动调度器
  /**
   * 启动工资发放调度器
   * @returns {Promise} Axios响应对象
   */
  async startScheduler() {
    return axios.post(`${API_BASE}/earnings/scheduler/start`)
  },

  // 8. 停止调度器
  /**
   * 停止工资发放调度器
   * @returns {Promise} Axios响应对象
   */
  async stopScheduler() {
    return axios.post(`${API_BASE}/earnings/scheduler/stop`)
  }


}
