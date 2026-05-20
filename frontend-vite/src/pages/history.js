import * as api from '../api.js'
import { formatCurrency } from '../utils.js'

// Render the history page
export async function renderHistoryPage() {
  try {
    const data = await api.getHistory()
    const reports = data.reports || []

    return `
      <div class="page-header">
        <div>
          <h2>Report History</h2>
          <p>All generated reports across all clients</p>
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <h3>All Reports</h3>
        </div>
        <div class="card-body">
          ${reports.length === 0 
            ? '<p class="empty-state">No reports generated yet.</p>'
            : renderReportsTable(reports)
          }
        </div>
      </div>
    `
  } catch (err) {
    console.error('History error:', err)
    return `<p class="empty-state">Error loading history: ${err.message}</p>`
  }
}

function renderReportsTable(reports) {
  return `
    <div class="table-container">
      <table>
        <thead>
          <tr>
            <th>Client</th>
            <th>Quarter</th>
            <th>Year</th>
            <th>Status</th>
            <th>Created</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          ${reports.map(r => `
            <tr>
              <td>${r.client_name || 'Unknown'}</td>
              <td>${r.quarter}</td>
              <td>${r.year}</td>
              <td><span class="badge badge-${r.status}">${r.status}</span></td>
              <td>${r.created_at}</td>
              <td>
                <div style="display:flex; gap:0.5rem;">
                  ${r.status === 'finalized' 
                    ? `
                      <a href="/api/reports/${r.id}/sacs" class="btn btn-sm btn-outline" target="_blank">SACS</a>
                      <a href="/api/reports/${r.id}/tcc" class="btn btn-sm btn-outline" target="_blank">TCC</a>
                    `
                    : `<button class="btn btn-sm btn-primary" onclick="window.app.navigateTo('report-entry/${r.client_id}/${r.id}')">Continue</button>`
                  }
                </div>
              </td>
            </tr>
          `).join('')}
        </tbody>
      </table>
    </div>
  `
}
