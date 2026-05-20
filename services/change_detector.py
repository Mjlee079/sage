"""
SAGEN-Sync: Change Detection Service (V2 Stub)
==============================================

Monitors client financial data for changes that require adjustments.
Alerts the team when action is needed.

Detection Rules:
    - Salary change: Compare new salary vs. previous month
    - Insurance rate change: Check liability interest rates
    - Account closure: Missing account in new reports
    - New account added: Extra account not in profile
    
Alert Methods:
    - In-app notifications (V2)
    - Email alerts (V2)
    - Dashboard flagging (V1-V2)
    
Status: Stub - V2 implementation planned
"""

class ChangeDetectorService:
    """
    Detects financial changes and alerts the team.
    
    V2 Features:
        - Automatic discrepancy detection
        - Threshold-based alerting
        - Email notifications
    """
    
    def __init__(self):
        self.salary_threshold = 0.05  # Alert if salary changes > 5%
        self.expense_threshold = 0.05  # Alert if expenses change > 5%
        
    def analyze_report(self, previous_report, current_report):
        """
        Compare two reports and detect changes.
        
        Args:
            previous_report (dict): Previous quarter's data
            current_report (dict): Current quarter's data
            
        Returns:
            dict: {changes: [], alerts: [], needs_review: bool}
        """
        changes = []
        alerts = []
        
        # Check salary change
        if previous_report and current_report:
            prev_salary = previous_report.get("inflow_amount", 0)
            curr_salary = current_report.get("inflow_amount", 0)
            
            if prev_salary > 0 and curr_salary > 0:
                change_pct = (curr_salary - prev_salary) / prev_salary
                if abs(change_pct) > self.salary_threshold:
                    changes.append(f"Salary changed by {change_pct:.1%}")
                    
        return {
            "changes": changes,
            "alerts": alerts,
            "needs_review": len(alerts) > 0
        }
    
    def check_floor_violation(self, account_balances):
        """
        Check if any account is below the $1,000 floor.
        
        Args:
            account_balances (dict): {account_id: balance}
            
        Returns:
            list: Warning messages
        """
        warnings = []
        for account_id, balance in account_balances.items():
            if balance < 1000:
                warnings.append(f"Account {account_id} below floor: ${balance:.2f}")
        return warnings
