import * as api from '../api.js'
import { formatCurrency, showToast } from '../utils.js'

// Render report entry form
export async function renderReportEntry(clientId, reportId) {
  try {
    const [clientData, reportData] = await Promise.all([
      api.getClient(clientId),
      api.getReport(reportId)
    ])

    const client = clientData.client
    const report = reportData.report
    const accounts = getAccountList(client)

    return `
      <div class="page-header">
        <div>
          <h2>Quarterly Report Entry</h2>
          <p>${client.first_name} ${client.last_name} — ${report.quarter} ${report.year}</p>
        </div>
        <button class="btn btn-outline" onclick="window.app.navigateTo('client-detail/${clientId}')">← Cancel</button>
      </div>

      <div class="card">
        <div class="card-header">
          <h3>Account Balances</h3>
        </div>
        <div class="card-body">
          <form id="report-entry-form" onsubmit="event.preventDefault(); window.app.handleReportEntry(this);">
            <input type="hidden" name="report_id" value="${reportId}" />

            <h4 style="margin-bottom:1rem;">Retirement Accounts</h4>
            ${renderAccountInputs(accounts.retirement, report.account_balances) || '<p>No retirement accounts configured.</p>'}

            <h4 style="margin-top:1.5rem; margin-bottom:1rem;">Non-Retirement Accounts</h4>
            ${renderAccountInputs(accounts.non_retirement, report.account_balances) || '<p>No non-retirement accounts configured.</p>'}

            <div class="form-row" style="margin-top:2rem;">
              <div class="form-group">
                <label>Zillow Home Value</label>
                <input type="number" step="0.01" name="zillow_home_value" 
                       value="${report.zillow_home_value || '0'}" />
              </div>
              <div class="form-group">
                <label>Private Reserve Balance</label>
                <input type="number" step="0.01" name="private_reserve_balance" 
                       value="${report.private_reserve_balance || '0'}" />
              </div>
            </div>

            <div class="modal-footer" style="margin-top:2rem; padding:0;">
              <button type="submit" class="btn btn-primary btn-lg">Save & Preview</button>
            </div>
          </form>
        </div>
      </div>
    `
  } catch (err) {
    console.error('Report entry error:', err)
    return `<p class="empty-state">Error loading report: ${err.message}</p>`
  }
}

function getAccountList(client) {
  const retirement = []
  const non_retirement = []

  if (client.retirement_accounts) {
    client.retirement_accounts.forEach((acc, idx) => {
      retirement.push({ id: `c1_ret_${idx + 1}`, name: `Client 1 ${acc.type || 'Retirement Account'}`, type: 'retirement' })
      if (client.is_married) {
        retirement.push({ id: `c2_ret_${idx + 1}`, name: `Client 2 ${acc.type || 'Retirement Account'}`, type: 'retirement' })
      }
    })
  }

  if (client.non_retirement_accounts) {
    client.non_retirement_accounts.forEach((acc, idx) => {
      non_retirement.push({ id: `non_ret_${idx + 1}`, name: acc.type || 'Brokerage Account', type: 'non_retirement' })
    })
  }

  return { retirement, non_retirement }
}

function renderAccountInputs(accounts, balances) {
  if (!accounts || accounts.length === 0) return ''

  const balancesObj = safeJson(balances, {})

  return accounts.map(acc => `
    <div class="form-row">
      <div class="form-group">
        <label>${acc.name}</label>
        <input type="number" step="0.01" 
               name="balance_${acc.id}" 
               value="${balancesObj[acc.id] || '0'}" 
               placeholder="0.00" />
      </div>
    </div>
  `).join('')
}

// Handle report entry form
export function handleReportEntry(form) {
  const formData = new FormData(form)
  const account_balances = {}
  let zillow_home_value = 0
  let private_reserve_balance = 0

  for (const [key, value] of formData) {
    if (key.startsWith('balance_')) {
      account_balances[key.replace('balance_', '')] = parseFloat(value) || 0
    } else if (key === 'zillow_home_value') {
      zillow_home_value = parseFloat(value) || 0
    } else if (key === 'private_reserve_balance') {
      private_reserve_balance = parseFloat(value) || 0
    }
  }

  const reportId = form.report_id.value

  api.updateReportBalances(reportId, {
    account_balances,
    zillow_home_value,
    private_reserve_balance
  })
    .then(() => {
      showToast('Balances saved!', 'success')
      window.app.navigateTo(`report-preview/${reportId}`)
    })
    .catch(err => {
      showToast(err.message, 'error')
    })
}
