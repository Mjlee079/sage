"""
SAGEN-Sync: Business Logic Services (V2 Extensibility)
=======================================================

This package contains high-level business logic that orchestrates
data between models and external systems.

Services Planned:
    automation:      Automated money movement (Inflow -> Lifestyle accounts)
    change_detector: Alert system for salary/expense changes
    buffer_manager:  Monitor account balances, trigger alerts when below floor
    audit_logger:    Compliance logging for all actions

Usage in V2:
    from services.automation import AutomationService
    
    automation = AutomationService()
    result = automation.calculate_monthly_transfer(client_id)
    
Each service is self-contained and testable.
"""
