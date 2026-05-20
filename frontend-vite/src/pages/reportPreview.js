import * as api from '../api.js'
import { formatCurrency, showToast } from '../utils.js'

// Render report preview with calculation results
export async function renderReportPreview(reportId) {
  try {
    const data = await api.getReportPreview(reportId)
    const { report, client, calculations } = data
    const sacs = calculations.sacs
    const tcc = calculations.tcc

    return `
      <div class="page-header">
        <div>
          <h2>Report Preview</h2>
          <p>${client.first_name} ${client.last_name} — ${report.quarter} ${report.year}</p>
        </div>
        <div style="display:flex; gap:0.5rem;">
          <button class="btn btn-outline" onclick="window.app.navigateTo('client-detail/${client.id}')">← Back</button>
          ${report.status === 'draft' 
            ? `<button class="btn btn-success" onclick="window.app.finalizeReport('${reportId}')">Finalize Report</button>`
            : `<div style="display:flex; gap:0.5rem;">
                 <a href="/api/reports/${reportId}/sacs" class="btn btn-primary" target="_blank">Download SACS</a>
                 <a href="/api/reports/${reportId}/tcc" class="btn btn-outline" target="_blank">Download TCC</a>
               </div>`
          }
        </div>
      </div>

      ${sacs && sacs.buffer_warnings && sacs.buffer_warnings.length > 0 ? `
        <div class="card" style="border-left: 4px solid var(--warning); background: #fffbeb;">
          <div class="card-body">
            <h4 style="color: var(--warning); margin-bottom: 0.75rem;">⚠️ Buffer Warnings</h4>
            ${sacs.buffer_warnings.map(w => `<p style="margin: 0.25rem 0;">• ${w}</p>`).join('')}
          </div>
        </div>
      ` : ''}

      <div class="stats-grid" style="grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));">
        <div class="stat-card primary">
          <div class="stat-value">${formatCurrency(sacs.inflow)}</div>
          <div class="stat-label">Inflow (Monthly)</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">${formatCurrency(sacs.outflow)}</div>
          <div class="stat-label">Outflow (Monthly)</div>
        </div>
        <div class="stat-card success">
          <div class="stat-value">${formatCurrency(sacs.excess)}</div>
          <div class="stat-label">Excess / Month</div>
        </div>
        <div class="stat-card info">
          <div class="stat-value">${formatCurrency(sacs.private_reserve_target)}</div>
          <div class="stat-label">Private Reserve Target</div>
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <h3>Total Client Capital (TCC)</h3>
        </div>
        <div class="card-body">
          <div class="stats-grid" style="grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));">
            <div class="stat-card">
              <div class="stat-value" style="font-size: 1.5rem;">${formatCurrency(tcc.total_retirement_client1)}</div>
              <div class="stat-label">Client 1 Retirement</div>
            </div>
            ${client.is_married ? `
              <div class="stat-card">
                <div class="stat-value" style="font-size: 1.5rem;">${formatCurrency(tcc.total_retirement_client2)}</div>
                <div class="stat-label">Client 2 Retirement</div>
              </div>
            ` : ''}
            <div class="stat-card">
              <div class="stat-value" style="font-size: 1.5rem;">${formatCurrency(tcc.total_non_retirement)}</div>
              <div class="stat-label">Non-Retirement</div>
            </div>
            <div class="stat-card">
              <div class="stat-value" style="font-size: 1.5rem;">${formatCurrency(tcc.trust_value)}</div>
              <div class="stat-label">Trust Value</div>
            </div>
            <div class="stat-card" style="border: 2px solid var(--primary); background: #eff6ff;">
              <div class="stat-value" style="font-size: 1.5rem; color: var(--primary);">${formatCurrency(tcc.grand_total)}</div>
              <div class="stat-label">Grand Total</div>
            </div>
            <div class="stat-card">
              <div class="stat-value" style="font-size: 1.5rem;">${formatCurrency(tcc.total_liabilities)}</div>
              <div class="stat-label">Total Liabilities</div>
            </div>
          </div>
        </div>
      </div>
    `
  } catch (err) {
    console.error('Report preview error:', err)
    return `<p class="empty-state">Error loading preview: ${err.message}</p>`
  }
}

// Finalize the report
export function finalizeReport(reportId) {
  api.finalizeReport(reportId)
    .then(() => {
      showToast('Report finalized!', 'success')
      window.app.navigateTo(`report-preview/${reportId}`)
    })
    .catch(err => {
      showToast(err.message, 'error')
    })
}
