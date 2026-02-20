import axios from 'axios'
import camelcaseKeys from 'camelcase-keys'
import { ACCESS_TOKEN } from './index'

const businessClient = axios.create({
  baseURL: 'http://62.234.131.204:30031',
  timeout: 15_000,
  headers: { 'Content-Type': 'application/json' },
  transformResponse: [(data: string) => {
    try { return camelcaseKeys(JSON.parse(data), { deep: true }) }
    catch { return data }
  }],
})

businessClient.interceptors.request.use((config) => {
  if (ACCESS_TOKEN.value) {
    config.headers.Authorization = `Bearer ${ACCESS_TOKEN.value}`
  }
  return config
})

// ── 积分 ──

export function getCredits(): Promise<{
  available: number
  total: number
  used: number
}> {
  return businessClient.get('/api/quota/credits').then(r => r.data)
}

export function redeemCode(code: string): Promise<{ success: boolean, message: string }> {
  return businessClient.post('/api/quota/redeem', { code }).then(r => r.data)
}

export function getCreditsLogs(page = 1, perPage = 20): Promise<{
  logs: Array<{ id: string, amount: number, reason: string, createdAt: string }>
  total: number
}> {
  return businessClient.get('/api/quota/credits/logs', { params: { page, per_page: perPage } }).then(r => r.data)
}

// ── 好感度 ──

export function getAffinity(): Promise<{
  level: number
  currentExp: number
  nextLevelExp: number
  totalExp: number
  title: string
  consecutiveDays: number
}> {
  return businessClient.get('/api/affinity/me').then(r => r.data)
}

export function checkIn(): Promise<{
  success: boolean
  reward: { exp: number, bonus?: string }
  message: string
}> {
  return businessClient.post('/api/affinity/check-in').then(r => r.data)
}

export function getCheckInStatus(): Promise<{
  checkedInToday: boolean
  consecutiveDays: number
}> {
  return businessClient.get('/api/affinity/check-in/status').then(r => r.data)
}

export function getAffinityTasks(): Promise<{
  tasks: Array<{ id: string, title: string, reward: number, completed: boolean }>
}> {
  return businessClient.get('/api/affinity/tasks').then(r => r.data)
}

export function completeTask(taskId: string): Promise<{ success: boolean, message: string }> {
  return businessClient.post(`/api/affinity/tasks/${taskId}/complete`).then(r => r.data)
}
