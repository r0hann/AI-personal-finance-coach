import axios from 'axios'

const BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
export const api = axios.create({ baseURL: BASE })

// Transactions
export const importCSV = (file: File) => {
  const form = new FormData()
  form.append('file', file)
  return api.post('/transactions/import/csv', form)
}
export const listTransactions = (monthYear?: string) =>
  api.get('/transactions/', { params: { month_year: monthYear } })
export const updateCategory = (id: string, categoryId: string) =>
  api.patch(`/transactions/${id}`, { category_id: categoryId })
export const monthlySummary = (monthYear: string) =>
  api.get('/transactions/summary/monthly', { params: { month_year: monthYear } })

// Insights
export const monthlyInsights = (monthYear: string) =>
  api.get('/insights/monthly', { params: { month_year: monthYear } })

// Budget
export const getForecast = () => api.get('/budget/forecast')
export const listBudgets = (monthYear?: string) =>
  api.get('/budget/', { params: { month_year: monthYear } })
export const createBudget = (body: { category_id: string; monthly_limit: number; month_year: string }) =>
  api.post('/budget/', body)

// Error Logs
export const listErrorLogs = (limit = 50) => api.get('/error-logs/', { params: { limit } })
export const clearErrorLogs = () => api.delete('/error-logs/')
