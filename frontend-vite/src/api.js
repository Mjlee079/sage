// API base URL (uses Vite proxy in dev, same domain in production)
const API_URL = ''

/**
 * Generic API request wrapper with error handling
 */
async function request(endpoint, options = {}) {
  const url = `${API_URL}${endpoint}`
  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers
    },
    ...options
  }

  if (config.body && typeof config.body === 'object') {
    config.body = JSON.stringify(config.body)
  }

  const response = await fetch(url, config)
  const data = await response.json().catch(() => null)

  if (!response.ok) {
    throw new Error(data?.error || `Request failed: ${response.status}`)
  }

  return data
}

// Dashboard
export const getDashboard = () => request('/api/dashboard')

// Clients
export const getClients = () => request('/api/clients')
export const getClient = (id) => request(`/api/clients/${id}`)
export const createClient = (data) => request('/api/clients', { method: 'POST', body: data })
export const updateClient = (id, data) => request(`/api/clients/${id}`, { method: 'PUT', body: data })
export const deleteClient = (id) => request(`/api/clients/${id}`, { method: 'DELETE' })

// Reports
export const getReports = () => request('/api/reports')
export const getReport = (id) => request(`/api/reports/${id}`)
export const getClientReports = (clientId) => request(`/api/clients/${clientId}/reports`)
export const createReport = (clientId, data) => request(`/api/clients/${clientId}/reports`, { method: 'POST', body: data })
export const updateReportBalances = (id, data) => request(`/api/reports/${id}/balances`, { method: 'PUT', body: data })
export const finalizeReport = (id) => request(`/api/reports/${id}/finalize`, { method: 'POST' })
export const getReportPreview = (id) => request(`/api/reports/${id}/preview`)

// History
export const getHistory = () => request('/api/history')

// PDFs
export const downloadSaCS = (id) => `/api/reports/${id}/sacs`
export const downloadTCC = (id) => `/api/reports/${id}/tcc`

// Canva
export const exportToCanva = (id) => request(`/api/canva/${id}/export`)
