import * as api from '../api.js'
import { formatCurrency } from '../utils.js'

// Render the dashboard page
export async function renderDashboard() {
  try {
    const data = await api.getDashboard()
    
    return `
      <div class="page-header">
        <div>
          <h2>Dashboard</h2>
          <p>Overview of your wealth management practice</p>
        </div>
        <button class="btn btn-primary" onclick="window.app.navigateTo('clients?add=true')">
          + Add Client
        </button>
      </div>
      
      <div class="stats-grid">
        <div class="stat-card primary">
          <div class="stat-value">${data.client_count || 0}</div>
          <div class="stat-label">Total Clients</div>
        </div>
        <div class="stat-card success">
          <div class="stat-value">${data.report_count || 0}</div>
          <div class="stat-label">Reports Generated</div>
        </div>
      </div>
      
      <div class="card">
        <div class="card-header">
          <h3>Recent Reports</h3>
          <a href="#history" class="btn btn-sm btn-outline" onclick="window.app.navigateTo('history')">View All</a>
        </div>
        <div class="card-body">
          ${renderRecentReports(data.recent_reports || [])}
        </div>
      </div>
      
      <div class="card">
        <div class="card-header">
          <h3>Clients</h3>
          <a href="#clients" class="btn btn-sm btn-outline" onclick="window.app.navigateTo('clients')">View All</a>
        </div>
        <div class="card-body">
          ${renderClientList(data.clients || [])}
        </div>
      </div>
    `
  } catch (err) {
    console.error('Dashboard error:', err)
    return `<p class="empty-state">Error loading dashboard: ${err.message}</p>`
  }
}

function renderRecentReports(reports) {
  if (reports.length === 0) {
    return '<p class="empty-state">No reports yet. Generate your first report!</p>'
  }
  
  return `
    <div class="table-container">
      <table>
        <thead>
          <tr>
            <th>Client</th>
            <th>Quarter</th>
            <th>Year</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          ${reports.map(r => `
            <tr>
              <td>${r.client_name || 'Unknown'}</td>
              <td>${r.quarter}</td>
              <td>${r.year}</td>
              <td><span class="badge badge-${r.status}">${r.status}</span></td>
            </tr>
          `).join('')}
        </tbody>
      </table>
    </div>
  `
}

function renderClientList(clients) {
  if (clients.length === 0) {
    return '<p class="empty-state">No clients yet. Add your first client!</p>'
  }
  
  return `
    <div class="table-container">
      <table>
        <thead>
          <tr>
            <th>Name</th>
            <th>DOB</th>
            <th>Monthly Salary</th>
            <th>Last Report</th>
          </tr>
        </thead>
        <tbody>
          ${clients.map(c => `
            <tr>
              <td>
                <a href="#client-detail/${c.id}" 
                   onclick="window.app.navigateTo('client-detail/${c.id}')" 
                   style="color: var(--primary); font-weight: 500; text-decoration: none;">
                  ${c.first_name} ${c.last_name}
                </a>
              </td>
              <td>${c.date_of_birth}</td>
              <td>${formatCurrency(c.monthly_salary)}</td>
              <td>${c.last_report || 'N/A'}</td>
            </tr>
          `).join('')}
        </tbody>
      </table>
    </div>
  `
}
