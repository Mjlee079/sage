import * as api from '../api.js'
import { formatCurrency, showToast, hideModal } from '../utils.js'
import { navigateTo } from '../router.js'

// Render the clients list page
export async function renderClientsPage() {
  try {
    const data = await api.getClients()
    const clients = data.clients || []
    
    return `
      <div class="page-header">
        <div>
          <h2>Clients</h2>
          <p>Manage your client profiles</p>
        </div>
        <button class="btn btn-primary" onclick="window.app.navigateTo('clients?add=true')">
          + Add Client
        </button>
      </div>
      
      ${clients.length === 0 
        ? '<p class="empty-state">No clients yet. Add your first client!</p>'
        : `<div class="client-grid">${clients.map(renderClientCard).join('')}</div>`
      }
      
      ${renderAddClientModal()}
    `
  } catch (err) {
    console.error('Clients error:', err)
    return `<p class="empty-state">Error loading clients: ${err.message}</p>`
  }
}

function renderClientCard(client) {
  return `
    <div class="client-card" onclick="window.app.navigateTo('client-detail/${client.id}')">
      <h4>${client.first_name} ${client.last_name}</h4>
      <div class="client-info">DOB: ${client.date_of_birth}</div>
      <div class="client-info">Monthly Salary: ${formatCurrency(client.monthly_salary)}</div>
      <div class="client-info">Expense Budget: ${formatCurrency(client.agreed_expense_budget)}</div>
      ${client.is_married ? '<div class="client-info">Married</div>' : ''}
      <div class="client-actions">
        <button class="btn btn-outline btn-sm" onclick="event.stopPropagation(); window.app.navigateTo('client-detail/${client.id}')">
          View
        </button>
        <button class="btn btn-primary btn-sm" onclick="event.stopPropagation(); window.app.navigateTo('report-entry/${client.id}')">
          + Report
        </button>
      </div>
    </div>
  `
}

function renderAddClientModal() {
  return `
    <div id="add-client-modal" class="modal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>Add New Client</h3>
          <button class="modal-close" onclick="window.app.hideModal('add-client-modal')">&times;</button>
        </div>
        <form id="add-client-form" onsubmit="event.preventDefault(); window.app.handleAddClient(this);">
          <div class="modal-body">
            ${renderClientForm()}
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-outline" onclick="window.app.hideModal('add-client-modal')">Cancel</button>
            <button type="submit" class="btn btn-primary">Save Client</button>
          </div>
        </form>
      </div>
    </div>
  `
}

function renderClientForm(client = null) {
  const mode = client ? 'edit' : 'add'
  return `
    <div class="form-row">
      <div class="form-group">
        <label>First Name *</label>
        <input type="text" name="first_name" value="${client?.first_name || ''}" required />
      </div>
      <div class="form-group">
        <label>Last Name *</label>
        <input type="text" name="last_name" value="${client?.last_name || ''}" required />
      </div>
    </div>
    <div class="form-row">
      <div class="form-group">
        <label>Date of Birth *</label>
        <input type="date" name="date_of_birth" value="${client?.date_of_birth || ''}" required />
      </div>
      <div class="form-group">
        <label>SSN (Last Four) *</label>
        <input type="text" name="ssn_last_four" value="${client?.ssn_last_four || ''}" required maxlength="4" />
      </div>
    </div>

    <div class="form-group">
      <label>
        <input type="checkbox" name="is_married" ${client?.is_married ? 'checked' : ''} />
        Married
      </label>
    </div>

    <h4 style="margin-top:1.5rem; margin-bottom:0.75rem;">Spouse Information</h4>
    <div class="form-row">
      <div class="form-group">
        <label>First Name</label>
        <input type="text" name="spouse_first_name" value="${client?.spouse_first_name || ''}" />
      </div>
      <div class="form-group">
        <label>Last Name</label>
        <input type="text" name="spouse_last_name" value="${client?.spouse_last_name || ''}" />
      </div>
    </div>
    <div class="form-row">
      <div class="form-group">
        <label>Date of Birth</label>
        <input type="date" name="spouse_dob" value="${client?.spouse_dob || ''}" />
      </div>
      <div class="form-group">
        <label>SSN (Last Four)</label>
        <input type="text" name="spouse_ssn_last_four" value="${client?.spouse_ssn_last_four || ''}" maxlength="4" />
      </div>
    </div>

    <h4 style="margin-top:1.5rem; margin-bottom:0.75rem;">Financial Information</h4>
    <div class="form-row">
      <div class="form-group">
        <label>Monthly Salary (after tax)</label>
        <input type="number" step="0.01" name="monthly_salary" value="${client?.monthly_salary || ''}" />
      </div>
      <div class="form-group">
        <label>Agreed Expense Budget</label>
        <input type="number" step="0.01" name="agreed_expense_budget" value="${client?.agreed_expense_budget || ''}" />
      </div>
    </div>
    <div class="form-group">
      <label>Private Reserve Target</label>
      <input type="number" step="0.01" name="private_reserve_target" value="${client?.private_reserve_target || ''}" />
      <small style="color:var(--gray-500)">Leave empty to auto-calculate</small>
    </div>
    <div class="form-group">
      <label>Notes</label>
      <textarea name="notes" rows="3">${client?.notes || ''}</textarea>
    </div>
  `
}

// Handle form submission
export function handleAddClient(form) {
  const data = {
    first_name: form.first_name.value,
    last_name: form.last_name.value,
    date_of_birth: form.date_of_birth.value,
    ssn_last_four: form.ssn_last_four.value,
    is_married: form.is_married.checked ? 1 : 0,
    spouse_first_name: form.spouse_first_name.value || null,
    spouse_last_name: form.spouse_last_name.value || null,
    spouse_dob: form.spouse_dob.value || null,
    spouse_ssn_last_four: form.spouse_ssn_last_four.value || null,
    monthly_salary: parseFloat(form.monthly_salary.value) || 0,
    agreed_expense_budget: parseFloat(form.agreed_expense_budget.value) || 0,
    private_reserve_target: parseFloat(form.private_reserve_target.value) || 0,
    notes: form.notes.value,
    retirement_accounts: [],
    non_retirement_accounts: [],
    trust_info: {},
    liabilities: []
  }
  
  api.createClient(data)
    .then(() => {
      showToast('Client created successfully!', 'success')
      hideModal('add-client-modal')
      navigateTo('clients')
    })
    .catch(err => {
      showToast(err.message, 'error')
    })
}
