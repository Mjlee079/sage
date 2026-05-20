/**
 * SAGEN-Sync: Client Form JavaScript
 * ====================================
 * 
 * Handles dynamic form elements on the Add/Edit Client page:
 *   - Toggle spouse section based on marital status
 *   - Add/remove retirement accounts dynamically
 *   - Add/remove non-retirement accounts dynamically
 *   - Add/remove liabilities dynamically
 */

(function() {
    'use strict';
    
    // ============================================
    // MARRIAGE TOGGLE
    // Show/hide spouse section based on checkbox
    // ============================================
    const marriageToggle = document.getElementById('is_married');
    const spouseSection = document.getElementById('spouse-section');
    
    if (marriageToggle && spouseSection) {
        marriageToggle.addEventListener('change', toggleSpouseSection);
        // Run once on load
        toggleSpouseSection();
    }
    
    function toggleSpouseSection() {
        if (marriageToggle.checked) {
            spouseSection.style.display = 'block';
            // Make required fields
            const spouseFields = spouseSection.querySelectorAll('input, select');
            spouseFields.forEach(function(field) {
                field.setAttribute('required', '');
            });
        } else {
            spouseSection.style.display = 'none';
            // Remove required to avoid validation errors
            const spouseFields = spouseSection.querySelectorAll('input, select');
            spouseFields.forEach(function(field) {
                field.removeAttribute('required');
            });
        }
    }
    
    // ============================================
    // DYNAMIC ACCOUNT FIELDS
    // Add/remove retirement and non-retirement accounts
    // ============================================
    
    let retirementCount = 0;
    let nonRetirementCount = 0;
    let liabilityCount = 0;
    
    // Initialize counters based on existing fields
    function initCounters() {
        const retirementList = document.getElementById('retirement-accounts-list');
        const nonRetirementList = document.getElementById('non-retirement-accounts-list');
        const liabilityList = document.getElementById('liabilities-list');
        
        if (retirementList) {
            retirementCount = retirementList.children.length;
        }
        if (nonRetirementList) {
            nonRetirementCount = nonRetirementList.children.length;
        }
        if (liabilityList) {
            liabilityCount = liabilityList.children.length;
        }
    }
    
    // Initialize on page load
    document.addEventListener('DOMContentLoaded', initCounters);
    
    // Global function called by onclick in HTML
    window.addAccount = function(accountType) {
        const listId = accountType === 'retirement' 
            ? 'retirement-accounts-list' 
            : 'non-retirement-accounts-list';
        const list = document.getElementById(listId);
        
        if (!list) return;
        
        const count = accountType === 'retirement' 
            ? ++retirementCount 
            : ++nonRetirementCount;
        
        const row = document.createElement('div');
        row.className = 'account-row';
        row.innerHTML = accountType === 'retirement' 
            ? getRetirementAccountFields(count)
            : getNonRetirementAccountFields(count);
        
        list.appendChild(row);
    };
    
    window.addLiability = function() {
        const list = document.getElementById('liabilities-list');
        if (!list) return;
        
        const count = liabilityCount++;
        const row = document.createElement('div');
        row.className = 'liability-row';
        row.innerHTML = getLiabilityFields(count);
        
        list.appendChild(row);
    };
    
    // HTML templates for dynamic fields
    function getRetirementAccountFields(index) {
        return `
            <input type="text" name="retirement_account_${index}_type" placeholder="Account type (e.g., IRA, Roth IRA)">
            <input type="text" name="retirement_account_${index}_last_four" placeholder="Last 4 digits" maxlength="4">
            <select name="retirement_account_${index}_owner">
                <option value="client1">Client 1</option>
                <option value="spouse">Client 2 (Spouse)</option>
            </select>
            <button type="button" class="btn btn-sm btn-danger" onclick="this.parentElement.remove()">&times;</button>
        `;
    }
    
    function getNonRetirementAccountFields(index) {
        return `
            <input type="text" name="non_retirement_account_${index}_type" placeholder="Account type (e.g., Brokerage, Joint)">
            <input type="text" name="non_retirement_account_${index}_last_four" placeholder="Last 4 digits" maxlength="4">
            <button type="button" class="btn btn-sm btn-danger" onclick="this.parentElement.remove()">&times;</button>
        `;
    }
    
    function getLiabilityFields(index) {
        return `
            <input type="text" name="liability_${index}_type" placeholder="Type (e.g., Mortgage, Auto Loan)">
            <input type="number" name="liability_${index}_balance" step="0.01" placeholder="Balance">
            <input type="number" name="liability_${index}_interest_rate" step="0.01" placeholder="Interest Rate %">
            <input type="number" name="liability_${index}_insurance_deductible" step="0.01" placeholder="Insurance Deductible">
            <button type="button" class="btn btn-sm btn-danger" onclick="this.parentElement.remove()">&times;</button>
        `;
    }
    
})();
