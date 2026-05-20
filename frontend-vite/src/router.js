import { showLoading } from './utils.js'
import { renderDashboard } from './pages/dashboard.js'
import { renderClientsPage } from './pages/clients.js'
import { renderClientDetail } from './pages/clientDetail.js'
import { renderReportEntry } from './pages/reports.js'
import { renderReportPreview } from './pages/reportPreview.js'
import { renderHistoryPage } from './pages/history.js'

const app = document.getElementById('app')

// Route configuration
const routes = {
  dashboard: { page: 'dashboard', render: renderDashboard },
  clients: { page: 'clients', render: renderClientsPage },
  'client-detail': { page: 'clients', render: (params) => renderClientDetail(params.id) },
  'report-entry': { page: 'clients', render: (params) => renderReportEntry(params.clientId, params.reportId) },
  'report-preview': { page: 'clients', render: (params) => renderReportPreview(params.reportId) },
  'report-finalize': { page: 'clients', render: (params) => renderReportPreview(params.reportId) },
  history: { page: 'history', render: renderHistoryPage }
}

// Parse query parameters from a URL hash string
export function getParams(hash) {
  const [route, paramString] = hash.split('?')
  if (!paramString) return { route }
  
  const params = {}
  const searchParams = new URLSearchParams(paramString)
  for (const [key, value] of searchParams) {
    params[key] = value
  }
  return { route, params }
}

// Main router
export function router(hash) {
  // Default to dashboard
  if (!hash || hash === '#' || hash === '') {
    hash = '#dashboard'
  }
  
  // Remove the # prefix
  const path = hash.slice(1)
  const parts = path.split('/')
  const routeKey = parts[0]
  
  // Default route
  if (!routes[routeKey]) {
    navigateTo('dashboard')
    return
  }
  
  // Extract parameters from URL pattern
  const params = {}
  if (parts.length > 1) {
    params.id = parts[1]
    if (parts.length > 2) {
      params.reportId = parts[2]
    }
  }
  
  // Also parse query string params
  const url = new URL(window.location)
  for (const [key, value] of url.searchParams) {
    params[key] = value
  }
  
  // Update active nav link
  document.querySelectorAll('.nav-link').forEach(link => {
    link.classList.toggle('active', link.dataset.page === routes[routeKey].page)
  })
  
  // Render the page
  showLoading(true)
  const container = document.getElementById('app')
  container.innerHTML = ''
  
  routes[routeKey].render(params).then(html => {
    if (html) {
      container.innerHTML = html
    }
    showLoading(false)
  }).catch(err => {
    console.error('Route error:', err)
    showLoading(false)
  })
}

// Navigate to a different route
export function navigateTo(hash, query = '') {
  const fullHash = query ? `${hash}?${query}` : hash
  window.location.hash = fullHash
}

// Initialize the router
export function initRouter() {
  // Handle hash change
  window.addEventListener('hashchange', () => {
    router(window.location.hash)
  })
  
  // Initial route
  router(window.location.hash)
}

// Setup navigation click handlers
document.querySelectorAll('.nav-link').forEach(link => {
  link.addEventListener('click', (e) => {
    e.preventDefault()
    const page = link.dataset.page
    if (page) navigateTo(page)
  })
})
