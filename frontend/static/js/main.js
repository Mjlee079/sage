/**
 * SAGEN-Sync: Main JavaScript
 * =============================
 * 
 * Global utility functions used across the application.
 * Specific page logic is in respective JS files:
 *   - client-form.js: Dynamic account/liability fields
 *   - report-form.js: Real-time calculations during data entry
 */

(function() {
    'use strict';
    
    // ============================================
    // FLASH MESSAGE AUTO-DISMISS
    // Automatically hide flash messages after 5 seconds
    // ============================================
    document.addEventListener('DOMContentLoaded', function() {
        const flashMessages = document.querySelectorAll('.flash-messages .alert');
        
        flashMessages.forEach(function(message) {
            setTimeout(function() {
                message.style.opacity = '0';
                message.style.transition = 'opacity 0.5s ease-out';
                setTimeout(function() {
                    message.remove();
                }, 500);
            }, 5000);
        });
    });
    
    // ============================================
    // CONFIRM DELETE
    // Shows a confirmation dialog before deleting records
    // ============================================
    document.addEventListener('click', function(event) {
        const deleteLink = event.target.closest('[data-confirm-delete]');
        if (deleteLink) {
            const message = deleteLink.getAttribute('data-confirm-message') || 
                          'Are you sure you want to delete this item?';
            if (!confirm(message)) {
                event.preventDefault();
            }
        }
    });
    
    // ============================================
    // CURRENCY FORMATTER
    // Formats numbers as currency: $1,234.56
    // ============================================
    window.formatCurrency = function(amount) {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD'
        }).format(amount);
    };
    
    // ============================================
    // NUMBER PARSER
    // Safely parses currency strings to floats
    // ============================================
    window.parseCurrency = function(value) {
        if (typeof value === 'number') return value;
        if (!value) return 0;
        // Remove commas and convert to float
        return parseFloat(value.toString().replace(/,/g, '')) || 0;
    };
    
    // ============================================
    // GENERAL UTILITIES
    // ============================================
    
    /**
     * Check if all required form fields are filled.
     * Used to enable/disable the submit button.
     */
    window.checkRequiredFields = function(form) {
        const requiredFields = form.querySelectorAll('[required]');
        let allFilled = true;
        
        requiredFields.forEach(function(field) {
            if (!field.value.trim()) {
                allFilled = false;
            }
        });
        
        return allFilled;
    };
    
    /**
     * Scroll to an element smoothly.
     */
    window.smoothScroll = function(element) {
        element.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    };
    
})();