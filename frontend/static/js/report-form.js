/**
 * SAGEN-Sync: Report Form JavaScript
 * =====================================
 * 
 * Handles real-time calculations during quarterly data entry.
 * As the user types balances, auto-calculates totals and displays them.
 * 
 * Features:
 *   - Real-time sum of retirement accounts (per client)
 *   - Real-time sum of non-retirement accounts
 *   - Auto-calculate grand total
 *   - Floor ($1,000) buffer warnings
 *   - Format numbers as currency on blur
 */

(function() {
    'use strict';
    
    // Constants
    const FLOOR = 1000;
    const INSURANCE_MONTHS = 6;
    
    // ============================================
    // INITIALIZATION
    // Runs when page loads
    // ============================================
    document.addEventListener('DOMContentLoaded', function() {
        // Find all balance input fields
        const balanceInputs = document.querySelectorAll('input[name^="balance_"]');
        
        // Add input listeners for real-time calculation
        balanceInputs.forEach(input => {
            input.addEventListener('input', debounce(calculateAllTotals, 300));
            input.addEventListener('blur', formatCurrencyValue);
        });
        
        // Initial calculation
        calculateAllTotals();
    });
    
    // ============================================
    // REAL-TIME CALCULATIONS
    // ============================================
    
    function calculateAllTotals() {
        calculateSACS();
        calculateTCC();
    }
    
    /**
     * Calculate SACS values (cash flow)
     * Excess = Inflow - Outflow
     */
    function calculateSACS() {
        // Get static values from the page (passed from client model)
        const inflowElement = document.getElementById('monthly_salary_display');
        const outflowElement = document.getElementById('monthly_budget_display');
        
        if (!inflowElement || !outflowElement) return;
        
        const inflow = parseCurrencyValue(inflowElement.textContent);
        const outflow = parseCurrencyValue(outflowElement.textContent);
        const excess = inflow - outflow;
        
        // Update display
        updateDisplay('sacs_excess', formatCurrencyValue(excess));
        
        // Calculate private reserve target (6 * expenses + floor)
        const numAccounts = document.querySelectorAll('input[name^="balance_"]')?.length || 1;
        const insuranceDeductibles = parseCurrencyValue(document.getElementById('insurance_deductibles')?.value) || 0;
        const prTarget = (INSURANCE_MONTHS * outflow) + (numAccounts * FLOOR) + insuranceDeductibles;
        
        updateDisplay('sacs_pr_target', formatCurrencyValue(prTarget));
        
        return { inflow, outflow, excess, prTarget };
    }
    
    /**
     * Calculate TCC values (net worth)
     * Sums all accounts by type
     */
    function calculateTCC() {
        // Client 1 Retirement
        const c1Retirement = sumAccountsByType('c1_retirement');
        updateDisplay('tcc_c1_retirement', formatCurrencyValue(c1Retirement));
        
        // Client 2 Retirement
        const c2Retirement = sumAccountsByType('c2_retirement');
        updateDisplay('tcc_c2_retirement', formatCurrencyValue(c2Retirement));
        
        // Non-Retirement
        const nonRetirement = sumAccountsByType('non_retirement');
        updateDisplay('tcc_non_retirement', formatCurrencyValue(nonRetirement));
        
        // Trust (Zillow value)
        const trustValue = parseCurrencyValue(document.querySelector('input[name="zillow_home_value"]')?.value) || 0;
        updateDisplay('tcc_trust', formatCurrencyValue(trustValue));
        
        // Liabilities (sum from the form if available)
        const liabilities = sumLiabilities();
        updateDisplay('tcc_liabilities', formatCurrencyValue(liabilities));
        
        // Grand Total = C1 + C2 + Non-Ret + Trust
        const grandTotal = c1Retirement + c2Retirement + nonRetirement + trustValue;
        updateDisplay('tcc_grand_total', formatCurrencyValue(grandTotal));
        
        // Buffer check
        checkFloorWarnings();
        
        return { c1Retirement, c2Retirement, nonRetirement, trustValue, liabilities, grandTotal };
    }
    
    // ============================================
    // ACCOUNT SUMMATION
    // ============================================
    
    /**
     * Sums all accounts matching the given type.
     * 
     * @param {string} type - Account type: 'c1_retirement', 'c2_retirement', 'non_retirement'
     * @returns {number} Total balance
     */
    function sumAccountsByType(type) {
        let total = 0;
        const inputs = document.querySelectorAll(`input[data-account-type="${type}"]`);
        
        inputs.forEach(input => {
            total += parseCurrencyValue(input.value);
        });
        
        // Also sum ownership-based if needed
        if (type === 'c1_retirement' || type === 'c2_retirement') {
            const owner = type === 'c1_retirement' ? 'client1' : 'spouse';
            const ownerInputs = document.querySelectorAll(`input[data-owner="${owner}"]`);
            ownerInputs.forEach(input => {
                total += parseCurrencyValue(input.value);
            });
        }
        
        return total;
    }
    
    /**
     * Sum all liability balances.
     */
    function sumLiabilities() {
        let total = 0;
        const liabilityInputs = document.querySelectorAll('input[name^="liability_"][name$="_balance"]');
        
        liabilityInputs.forEach(input => {
            total += parseCurrencyValue(input.value);
        });
        
        return total;
    }
    
    // ============================================
    // FLOOR CHECKS
    // ============================================
    
    function checkFloorWarnings() {
        const warningsContainer = document.getElementById('floor-warnings');
        if (!warningsContainer) return;
        
        const warnings = [];
        const inputs = document.querySelectorAll('input[name^="balance_"]');
        
        inputs.forEach(input => {
            const balance = parseCurrencyValue(input.value);
            if (balance < FLOOR) {
                const accountName = input.closest('.account-field')?.querySelector('label')?.textContent || 'Account';
                warnings.push(`${accountName} is below floor: $${formatCurrencyValue(balance)} (minimum: $${formatCurrencyValue(FLOOR)})`);
            }
        });
        
        // Update warning display
        if (warnings.length > 0) {
            warningsContainer.innerHTML = warnings.map(w => `<div class="alert alert-warning">${w}</div>`).join('');
            warningsContainer.style.display = 'block';
        } else {
            warningsContainer.style.display = 'none';
        }
        
        return warnings;
    }
    
    // ============================================
    // UTILITY HELPERS
    // ============================================
    
    /**
     * Parse a currency string or value to a number.
     */
    function parseCurrencyValue(value) {
        if (typeof value === 'number') return value;
        if (!value) return 0;
        const cleaned = value.toString().replace(/[$,]/g, '').trim();
        return parseFloat(cleaned) || 0;
    }
    
    /**
     * Format a number as currency string.
     */
    function formatCurrencyValue(value) {
        if (typeof value === 'string') return value; // Already formatted
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD'
        }).format(value);
    }
    
    /**
     * Update the text content of an element.
     */
    function updateDisplay(elementId, value) {
        const element = document.getElementById(elementId);
        if (element) {
            element.textContent = value;
        }
    }
    
    /**
     * Debounce function to limit how often a function fires.
     */
    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
    
    /**
     * Format input value as currency on blur.
     */
    function formatCurrencyValue(event) {
        const input = event.target;
        const value = parseCurrencyValue(input.value);
        if (value) {
            input.value = formatCurrencyValue(value);
        }
    }
    
})();
