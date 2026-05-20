// Utility functions for the app

// Show a toast notification
export function showToast(message, type = 'info') {
  const container = document.getElementById('toast-container')
  const toast = document.createElement('div')
  toast.className = `toast toast-${type}`
  toast.textContent = message
  container.appendChild(toast)
  
  setTimeout(() => {
    toast.style.opacity = '0'
    toast.style.transition = 'opacity 0.3s'
    setTimeout(() => toast.remove(), 300)
  }, 3000)
}

// Show/hide loading spinner
export function showLoading(show = true) {
  const loading = document.getElementById('loading')
  if (show) loading.classList.remove('hidden')
  else loading.classList.add('hidden')
}

// Format currency
export function formatCurrency(value) {
  const num = parseFloat(value) || 0
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2
  }).format(num)
}

// Format date from ISO string
export function formatDate(dateStr) {
  if (!dateStr) return 'N/A'
  return new Date(dateStr).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

// Safe JSON parse
export function safeJson(str, defaultValue = null) {
  try {
    return JSON.parse(str)
  } catch {
    return defaultValue
  }
}

// Form data to object helper
export function formDataToObject(form) {
  const data = {}
  const formData = new FormData(form)
  for (const [key, value] of formData) {
    if (data[key]) {
      if (Array.isArray(data[key])) data[key].push(value)
      else data[key] = [data[key], value]
    } else {
      data[key] = value
    }
  }
  return data
}

// Show modal by ID
export function showModal(modalId) {
  document.getElementById(modalId).classList.add('active')
}

// Hide modal by ID
export function hideModal(modalId) {
  document.getElementById(modalId).classList.remove('active')
}

// Current quarter and year for report creation
export function getCurrentQuarter() {
  const now = new Date()
  const month = now.getMonth() + 1
  const quarter = Math.ceil(month / 3)
  return { quarter: `Q${quarter}`, year: now.getFullYear() }
}
