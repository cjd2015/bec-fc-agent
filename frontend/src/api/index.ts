import axios, { AxiosError, AxiosRequestConfig } from 'axios'
import { clearAuthSession, getAuthSession } from '@/utils/auth'

export const api = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

api.interceptors.request.use(
  (config) => {
    const session = getAuthSession()
    if (session?.token) {
      config.headers.Authorization = `Bearer ${session.token}`
      config.headers['X-BEC-Authorization'] = `Bearer ${session.token}`
    }
    if (session?.username) {
      config.headers['X-BEC-Username'] = session.username
    }
    return config
  },
  (error) => Promise.reject(error),
)

api.interceptors.response.use(
  (response) => response.data,
  (error: AxiosError) => {
    const message = (error.response?.data as any)?.detail || '请求失败'
    if (error.response?.status === 401) {
      clearAuthSession()
      window.location.href = '/login'
    }
    return Promise.reject(new Error(message))
  },
)

export function request<T>(config: AxiosRequestConfig): Promise<T> {
  return api.request(config) as Promise<T>
}

export default api
