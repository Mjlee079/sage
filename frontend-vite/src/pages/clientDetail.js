import * as api from '../api.js'
import { formatCurrency, showToast, getCurrentQuarter } from '../utils.js'
import { hideModal } from '../utils.js'

// Render client detail page
export async function renderClientDetail(clientId) {
  try {
    const [clientData, reportsData] = await Promise.all([
      api.getClient(clientId),
      api.getClientReports(clientId)
    ])

    const client = clientData.client
    const reports = reportsData.reports || []

    return `
      <div class="page-header">
        <div>
          <h2>${client.first_name} ${client.last_name}</h2>
          <p>${client.is_married ? 'Married' : 'Single'} | DOB: ${client.date_of_birth}</p>
        </div>
        <div style="display:flex; gap:0.5rem;">
          <button class="btn btn-outline" onclick="window.app.navigateTo('clients')">← Back</button>
          <button class="btn btn-primary" onclick="window.app.showModal('generate-report-modal')">+ Generate Report</button>
        </div>
      </div>

      <div class="stats-grid">
        <div class="stat-card primary">
          <div class="stat-value">${formatCurrency(client.monthly_salary)}</div>
          <div class="stat-label">Monthly Salary</div>
        </div>
        <div class="stat-card success">
          <div class="stat-value">${formatCurrency(client.agreed_expense_budget)}</div>
          <div class="stat-label">Expense Budget</div>
        </div>
        <div class="stat-card info">
          <div class="stat-value">${reports.length}</div>
          <div class="stat-label">Reports</div>
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <h3>Client Profile</h3>
          <button class="btn btn-outline btn-sm" onclick="window.app.showModal('edit-client-modal')">Edit</button>
        </div>
        <div class="card-body">
          ${renderClientProfile(client)}
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <h3>Report History</h3>
        </div>
        <div class="card-body">
          ${reports.length === 0 
            ? '<p class="empty-state">No reports yet for this client.</p>'
            : renderReportsTable(reports)
          }
        </div>
      </div>

      ${renderGenerateReportModal()}
      ${renderEditClientModal(client)}
    `
  } catch (err) {
    console.error('Client detail error:', err)
    return `<p class="empty-state">Error loading client: ${err.message}</p>`
  }
}

function renderClientProfile(client) {
  return `
    <div class="form-row">
      <div><strong>Full Name:</strong> ${client.first_name} ${client.last_name}</div>
      <div><strong>DOB:</strong> ${client.date_of_birth}</div>
      <div><strong>SSN (Last 4):</strong> ***-${client.ssn_last_four}</div>
      <div><strong>Status:</strong> ${client.is_married ? 'Married' : 'Single'}</div>
    </div>

    ${client.is_married ? `
      <h4 style="margin-top:1.5rem; margin-bottom:0.75rem;">Spouse Information</h4>
      <div class="form-row">
        <div><strong>Name:</strong> ${client.spouse_first_name || 'N/A'} ${client.spouse_last_name || ''}</div>
        <div><strong>DOB:</strong> ${client.spouse_dob || 'N/A'}</div>
        <div><strong>SSN (Last 4):</strong> ${client.spouse_ssn_last_four ? '***-' + client.spouse_ssn_last_four : 'N/A'}</div>
      </div>
    ` : ''}

    <h4 style="margin-top:1.5rem; margin-bottom:0.75rem;">Financial Information</h4>
    <div class="form-row">
      <div><strong>Monthly Salary:</strong> ${formatCurrency(client.monthly_salary)}</div>
      <div><strong>Expense Budget:</strong> ${formatCurrency(client.agreed_expense_budget)}</div>
      <div><strong>Private Reserve Target:</strong> ${formatCurrency(client.private_reserve_target)}</div>
    </div>

    ${client.notes ? `
      <h4 style="margin-top:1.5rem; margin-bottom:0.75rem;">Notes</h4>
      <p style="color:var(--gray-600)">${client.notes}</p>
    ` : ''}
  `
}

function renderReportsTable(reports) {
  return `
    <div class="table-container">
      <table>
        <thead>
          <tr>
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
              <td>${r.quarter}</td>
              <td>${r.year}</td>
              <td><span class="badge badge-${r.status}">${r.status}</span></td>
              <td>${r.created_at}</td>
              <td>
                ${r.status === 'draft' 
                  ? `<button class="btn btn-sm btn-primary" onclick="window.app.navigateTo('report-entry?clientId=${r.client_id}&reportId=${r.id}')">Continue</button>`
                  : `<button class="btn btn-sm btn-outline" onclick="window.app.navigateTo('report-preview?reportId=${r.id}')">View</button>`
                }
              </td>
            </tr>
          `).join('')}
        </tbody>
      </table>
    </div>
  `
}

function renderGenerateReportModal() {
  const { quarter, year } = getCurrentQuarter()
  return `
    <div id="generate-report-modal" class="modal">
      <div class="modal-content" style="max-width: 500px;">
        <div class="modal-header">
          <h3>Generate New Report</h3>
          <button class="modal-close" onclick="window.app.hideModal('generate-report-modal')">&times;</button>
        </div>
        <form id="generate-report-form" onsubmit="event.preventDefault(); window.app.handleGenerateReport(this);">
          <div class="modal-body">
            <div class="form-group">
              <label>Quarter</label>
              <select name="quarter">
                <option value="Q1">Q1</option>
                <option value="Q2">Q2</option>
                <option value="Q3">Q3</option>
                <option value="Q4">Q4</option>
              </select>
            </div>
            <div class="form-group">
              <label>Year</label>
              <input type="number" name="year" value="${year}" min="2000" max="2100" />
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-outline" onclick="window.app.hideModal('generate-report-modal')">Cancel</button>
            <button type="submit" class="btn btn-primary">Create Report</button>
          </div>
        </form>
      </div>
    </div>
  `
}

function renderEditClientModal(client) {
  return `
    <div id="edit-client-modal" class="modal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>Edit Client</h3>
          <button class="modal-close" onclick="window.app.hideModal('edit-client-modal')">&times;</button>
        </div>
        <form id="edit-client-form" onsubmit="event.preventDefault(); window.app.handleUpdateClient(this);">
          <div class="modal-body">
            ${renderClientEditForm(client)}
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-outline" onclick="window.app.hideModal('edit-client-modal')">Cancel</button>
            <button type="submit" class="btn btn-primary">Save Changes</button>
          </div>
        </form>
      </div>
    </div>
  `
}

function renderClientEditForm(client) {
  return `
    <div class="form-row">
      <div class="form-group">
        <label>First Name *</label>
        <input type="text" name="first_name" value="${client.first_name || ''}" required />
      </div>
      <div class="form-group">
        <label>Last Name *</label>
        <input type="text" name="last_name" value="${client.last_name || ''}" required />
      </div>
    </div>
    <div class="form-row">
      <div class="form-group">
        <label>Date of Birth *</label>
        <input type="date" name="date_of_birth" value="${client.date_of_birth || ''}" required />
      </div>
      <div class="form-group">
        <label>SSN (Last Four) *</label>
        <input type="text" name="ssn_last_four" value="${client.ssn_last_four || ''}" required maxlength="4" />
      </div>
    </div>
    <div class="form-row">
      <div class="form-group">
        <label>Monthly Salary</label>
        <input type="number" step="0.01" name="monthly_salary" value="${client.monthly_salary || '0'}" />
      </div>
      <div class="form-group">
        <label>Expense Budget</label>
        <input type="number" step="0.01" name="agreed_expense_budget" value="${client.agreed_expense_budget || '0'}" />
      </div>
    </div>
    <div class="form-group">
      <label>Notes</label>
      <textarea name="notes" rows="3">${client.notes || ''}</textarea>
    </div>
  `
}

// Handle generate report form
export function handleGenerateReport(form) {
  const clientId = window.location.hash.split('/')[1]
  const data = {
    quarter: form.quarter.value,
    year: parseInt(form.year.value)
  }

  api.createReport(clientId, data)
    .then(result => {
      showToast('Report created!', 'success')
      hideModal('generate-report-modal')
      window.app.navigateTo(`report-entry?clientId=${clientId}&reportId=${result.id}`)
    })
    .catch(err => {
      showToast(err.message, 'error')
    })
}
