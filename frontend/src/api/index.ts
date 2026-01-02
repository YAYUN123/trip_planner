import axios from 'axios'
import type { TripRequest, TripPlan } from '@/types'

const api = axios.create({
  baseURL: '/api',
  timeout: 600000, // 10分钟超时，因为后端处理时间较长
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    const message = error.response?.data?.detail || error.message || '请求失败'
    return Promise.reject(new Error(message))
  }
)

/**
 * 创建旅行计划
 */
export const createTripPlan = async (request: TripRequest): Promise<TripPlan> => {
  return api.post<TripPlan>('/trip', request) as unknown as Promise<TripPlan>
}

