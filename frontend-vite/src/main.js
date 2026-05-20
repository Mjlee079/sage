import './style.css'
import { initRouter, navigateTo } from './router.js'
import { showToast, showLoading, hideModal } from './utils.js'

// Make utilities available globally for inline onclick handlers
window.app = {
  navigateTo,
  showToast,
  showLoading,
  showModal: (id) => document.getElementById(id).classList.add('active'),
  hideModal: (id) => document.getElementById(id).classList.remove('active'),
  handleAddClient: (form) => {
    // Import dynamically to avoid circular dependencies
    import('./pages/clients.js').then(m => m.handleAddClient(form))
  },
  handleGenerateReport: (form) => {
    import('./pages/clientDetail.js').then(m => m.handleGenerateReport(form))
  },
  handleReportEntry: (form) => {
    import('./pages/reports.js').then(m => m.handleReportEntry(form))
  },
  finalizeReport: (id) => {
    import('./pages/reportPreview.js').then(m => m.finalizeReport(id))
  }
}

// Initialize the app
initRouter()
