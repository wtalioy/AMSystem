import axios from 'axios'

const API_BASE = 'http://localhost:8000/api/v1'

export default {
  // 获取车辆类型
  async getCarTypes() {
    return axios.get(`${API_BASE}/cars/types`)
  },

  // 创建车辆类型
  async createCarType(typeData) {
    return axios.post(`${API_BASE}/cars/types`, {
      car_type: typeData.carType
    })
  },

  // 创建车辆
  async createCar(carData) {
    return axios.post(`${API_BASE}/cars/`, {
      car_type: carData.car_type,
      car_id: carData.car_id
    })
  },

  // 获取车辆列表
  async getCars(pagination = { page: 1, page_size: 20 }) {
    return axios.get(`${API_BASE}/cars/`, {
      params: {
        page: pagination.page,
        page_size: pagination.page_size
      }
    })
  },

  // 获取单个车辆详情
  async getCarDetail(carId) {
    return axios.get(`${API_BASE}/cars/${carId}`)
  },

  // 更新车辆信息
  async updateCar(carId, updateData) {
    return axios.put(`${API_BASE}/cars/${carId}`, {
      car_type: updateData.carType
    })
  },

  // 删除车辆
  async deleteCar(carId) {
    return axios.delete(`${API_BASE}/cars/${carId}`)
  },

  // 获取维护历史记录
  async getMaintenanceHistory(carId, pagination = { page: 1, page_size: 20 }) {
    return axios.get(`${API_BASE}/cars/${carId}/maintenance-history`, {
      params: {
        page: pagination.page,
        page_size: pagination.page_size
      }
    })
  }
}