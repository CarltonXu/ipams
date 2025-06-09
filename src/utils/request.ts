import axios from 'axios'
import { handleApiError } from './error'

const request = axios.create({
  baseURL: '/api',
  timeout: 10000
})

// 响应拦截器
request.interceptors.response.use(
  response => response,
  error => {
    handleApiError(error)
    return Promise.reject(error)
  }
)

export default request 