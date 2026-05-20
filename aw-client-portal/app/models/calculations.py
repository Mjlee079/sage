"""
SAGEN-Sync: Calculator Engine
================================

Central hub for all automated financial calculations.
Every calculation in the app passes through this module.

Rules (From PRD - Must Follow Exactly):
  1. SACS: Excess = Inflow - Outflow
     - Inflow = monthly_salary (after tax)
     - Outflow = agreed_expense_budget
  2. SACS: Private Reserve Target = (6 × monthly_expenses) + sum(all_insurance_deductibles) + ($1,000 × num_accounts)
  3. TCC: Client 1 Retirement = sum of Client 1's retirement accounts
  4. TCC: Client 2 Retirement = sum of Client 2's retirement accounts
  5. TCC: Non-Retirement Total = sum of all non-retirement accounts (excluding trust)
  6. TCC: Grand Total = C1 Retirement + C2 Retirement + Non-Retirement + Trust
  7. TCC: Liabilities Total = sum of all liabilities (displayed separately, NOT subtracted)
  8. TCC: Trust IS NOT added to non-retirement (separate line item)

Buffer/Floor Rules (User Clarified):
  - Floor = $1,000 per account (never changes)
  - Any account balance below $1,000 triggers a flag
  - Private Reserve calculation includes floor per active account

Usage:
    from app.models.calculations import Calculator
    
    results = Calculator.calculate_all(client_data, report_data)
    # results = {
    #     "sacs": { inflow, outflow, excess, private_reserve_target, buffer_warnings },
    #     "tcc": { c1_retirement, c2_retirement, non_retirement, trust, liabilities, grand_total }
    # }
"""

from app.database import get_db


class Calculator:
    """
    Encapsulates all financial calculation logic.
    
    This class is stateless - all methods are classmethod or staticmethod.
    Every calculation is deterministic given the same inputs.
    """
    
    # Constants (from config)
    FLOOR = 1000.0             # $1,000 per account
    PRIVATE_RESERVE_MONTHS = 6  # 6 months of expenses
    
    
    # ============================================
    # MAIN CALCULATION ENTRY POINT
    # ============================================
    
    @classmethod
    def calculate_all(cls, client, report):
        """
        Run all calculations for a client report.
        
        This is the single entry point - it calls both SACS and TCC
        calculation methods and returns a combined result dictionary.
        
        Args:
            client (dict): Client profile data (from Client model)
            report (dict): Report data (from Report model)
        
        Returns:
            dict: Complete calculation results
                {
                    "sacs": {
                        "inflow": float,
                        "outflow": float,
                        "excess": float,
                        "private_reserve_target": float,
                        "buffer_warnings": [list of warning strings]
                    },
                    "tcc": {
                        "total_retirement_client1": float,
                        "total_retirement_client2": float,
                        "total_non_retirement": float,
                        "trust_value": float,
                        "total_liabilities": float,
                        "grand_total": float,
                        "net_worth_components": dict  # For detailed display
                    }
                }
        """
        # Calculate SACS (cash flow)
        sacs = cls.calculate_sacs(client)
        
        # Calculate TCC (net worth)
        tcc = cls.calculate_tcc(client, report)
        
        # Calculate buffer/floor warnings
        buffer_warnings = cls.calculate_buffer_warnings(client, report)
        
        return {
            "sacs": {**sacs, "buffer_warnings": buffer_warnings},
            "tcc": tcc
        }
    
    
    # ============================================
    # SACS CALCULATIONS (Cash Flow)
    # ============================================
    
    @classmethod
    def calculate_sacs(cls, client):
        """
        Calculate Simple Automated Cash Flow System (SACS) values.
        
        Formula:
          Inflow = client.monthly_salary (after-tax income)
          Outflow = client.agreed_expense_budget
          Excess = Inflow - Outflow
          Private Reserve Target = (6 × Outflow) + insurance_deductibles + ($1,000 × num_accounts)
        
        Args:
            client (dict): Client profile with salary and budget
        
        Returns:
            dict: SACS calculation results
        """
        # Extract static financial data from client profile
        inflow = float(client.get("monthly_salary", 0))  # After-tax income
        outflow = float(client.get("agreed_expense_budget", 0))  # Monthly expense budget
        
        # Excess = Inflow - Outflow (what goes to private reserve)
        excess = inflow - outflow
        
        # Calculate private reserve target
        private_reserve_target = cls.calculate_private_reserve_target(client)
        
        # Calculate number of active accounts (for floor calculation)
        num_accounts = cls.count_active_accounts(client)
        
        return {
            "inflow": inflow,
            "outflow": outflow,
            "excess": excess,
            "private_reserve_target": private_reserve_target,
            "floor_per_account": cls.FLOOR,
            "num_accounts": num_accounts
        }
    
    
    @classmethod
    def calculate_private_reserve_target(cls, client):
        """
        Calculate the target amount for the Private Reserve (high-yield savings).
        
        Formula (from PRD):
          Private Reserve Target = (6 × monthly_expenses) + sum(all_insurance_deductibles) + floor_adjustment
        
        Where:
          monthly_expenses = client.agreed_expense_budget
          insurance_deductibles = sum of all liability-related insurance deductibles
          floor_adjustment = $1,000 × number_of_active_accounts
        
        Note: The PRD says insurance deductibles are "sum of all insurance deductibles".
        We calculate this from the liabilities table (mortgage, auto, health insurance).
        If not specified, defaults to 0.
        
        Args:
            client (dict): Client profile
        
        Returns:
            float: Target amount for private reserve
        """
        # Base: 6 months of expenses
        monthly_expenses = float(client.get("agreed_expense_budget", 0))
        base_target = cls.PRIVATE_RESERVE_MONTHS * monthly_expenses
        
        # Insurance deductibles (from liabilities)
        insurance_deductibles = cls.calculate_insurance_deductibles(client)
        
        # Floor adjustment: $1,000 per active account
        num_accounts = cls.count_active_accounts(client)
        floor_adjustment = num_accounts * cls.FLOOR
        
        return base_target + insurance_deductibles + floor_adjustment
    
    
    @classmethod
    def calculate_insurance_deductibles(cls, client):
        """
        Sum all insurance-related deductibles from liabilities.
        
        For each liability, check if it has an 'insurance_deductible' field.
        This is often auto & home insurance (not health insurance, which is separate).
        
        Args:
            client (dict): Client profile
        
        Returns:
            float: Total insurance deductibles
        """
        liabilities = client.get("liabilities", [])
        total = 0.0
        
        for liability in liabilities:
            # Each liability may have an insurance_deductible field
            # If not present, we lookup common defaults based on type
            deductible = liability.get("insurance_deductible")
            
            if deductible is not None:
                total += float(deductible)
            else:
                # Use default deductibles based on type
                liab_type = liability.get("type", "").lower()
                if "mortgage" in liab_type or "home" in liab_type:
                    total += 2500.0  # Common homeowners deductible
                elif "auto" in liab_type or "car" in liab_type:
                    total += 500.0   # Common auto deductible
        
        return total
    
    
    # ============================================
    # TCC CALCULATIONS (Net Worth Overview)
    # ============================================
    
    @classmethod
    def calculate_tcc(cls, client, report):
        """
        Calculate Total Client Chart (TCC) values.
        
        Formula (from PRD):
          Client 1 Retirement = sum(all C1 retirement accounts)
          Client 2 Retirement = sum(all C2 retirement accounts)
          Non-Retirement Total = sum(all non-retirement accounts, excluding trust)
          Trust Value = Zillow home value (from trust_info)
          Grand Total = C1 Retirement + C2 Retirement + Non-Retirement + Trust
          Liabilities Total = sum(all liabilities) [displayed separately, NOT subtracted]
        
        Important rules:
          - Trust is NOT added to non-retirement total (separate line)
          - Liabilities are NOT subtracted from net worth
        
        Args:
            client (dict): Client profile (account structure)
            report (dict): Report with quarterly balances
        
        Returns:
            dict: TCC calculation results
        """
        # Get account balances from the report
        account_balances = report.get("account_balances", {})
        if isinstance(account_balances, str):
            import json
            account_balances = json.loads(account_balances)
        
        # Calculate retirement totals by person
        c1_retirement = cls.sum_accounts_by_owner(client, report, "retirement", is_spouse=False)
        c2_retirement = cls.sum_accounts_by_owner(client, report, "retirement", is_spouse=True)
        
        # Non-retirement total (all non-retirement accounts, excluding trust)
        non_retirement = cls.sum_accounts_by_type(client, report, "non_retirement")
        
        # Trust value (from Zillow or manual entry)
        trust_value = cls.calculate_trust_value(client, report)
        
        # Liabilities total
        total_liabilities = cls.calculate_liabilities_total(client)
        
        # Grand total (the big number)
        grand_total = c1_retirement + c2_retirement + non_retirement + trust_value
        
        return {
            "total_retirement_client1": c1_retirement,
            "total_retirement_client2": c2_retirement,
            "total_non_retirement": non_retirement,
            "trust_value": trust_value,
            "total_liabilities": total_liabilities,
            "grand_total": grand_total,
            "net_worth_components": {
                "c1_retirement_accounts": cls.get_account_breakdown(client, report, "c1_retirement"),
                "c2_retirement_accounts": cls.get_account_breakdown(client, report, "c2_retirement"),
                "non_retirement_accounts": cls.get_account_breakdown(client, report, "non_retirement"),
                "trust": trust_value,
                "liabilities": cls.get_liability_breakdown(client)
            }
        }
    
    
    @classmethod
    def sum_accounts_by_owner(cls, client, report, account_type, is_spouse=False):
        """
        Sum account balances for a specific owner (Client 1 or Client 2).
        
        For married clients, we track which accounts belong to which spouse.
        For single clients, all retirement accounts belong to Client 1.
        
        Args:
            client (dict): Client profile
            report (dict): Report with balances
            account_type (str): 'retirement' or 'non_retirement'
            is_spouse (bool): If True, sum spouse's accounts; if False, primary client's
        
        Returns:
            float: Sum of matching account balances
        """
        account_balances = report.get("account_balances", {})
        if isinstance(account_balances, str):
            import json
            account_balances = json.loads(account_balances)
        
        total = 0.0
        account_list = client.get(f"{account_type}_accounts", [])
        
        for idx, account in enumerate(account_list, 1):
            # Check if this account belongs to the requested owner
            # In a real app, each account has an 'owner' field: 'client1', 'client2', or 'joint'
            account_owner = account.get("owner", "client1")  # Default to client 1
            
            if is_spouse and account_owner != "spouse":
                continue
            elif not is_spouse and account_owner == "spouse":
                continue
            
            # Get the balance for this account
            account_id = None
            if account_type == "retirement":
                account_id = f"c1_ret_{idx}" if not is_spouse else f"c2_ret_{idx}"
            elif account_type == "non_retirement":
                account_id = f"non_ret_{idx}"
            
            if account_id and account_id in account_balances:
                total += float(account_balances[account_id])
        
        return total
    
    
    @classmethod
    def sum_accounts_by_type(cls, client, report, account_type):
        """
        Sum all accounts of a given type (retirement or non-retirement).
        Used for non-retirement total (all accounts, both clients).
        
        Args:
            client (dict): Client profile
            report (dict): Report with balances
            account_type (str): 'retirement' or 'non_retirement'
        
        Returns:
            float: Sum of matching account balances
        """
        account_balances = report.get("account_balances", {})
        if isinstance(account_balances, str):
            import json
            account_balances = json.loads(account_balances)
        
        total = 0.0
        account_list = client.get(f"{account_type}_accounts", [])
        
        for idx, _ in enumerate(account_list, 1):
            account_id = None
            if account_type == "retirement":
                account_id = f"c1_ret_{idx}"
                # Also check for c2 if married
                c2_id = f"c2_ret_{idx}"
                if c2_id in account_balances:
                    total += float(account_balances[c2_id])
            elif account_type == "non_retirement":
                account_id = f"non_ret_{idx}"
            
            if account_id and account_id in account_balances:
                total += float(account_balances[account_id])
        
        return total
    
    
    @classmethod
    def calculate_trust_value(cls, client, report):
        """
        Calculate trust value from Zillow home value.
        
        In V1, this is manually entered (Zillow API deferred to V2).
        
        Args:
            client (dict): Client profile
            report (dict): Report with Zillow value
        
        Returns:
            float: Trust value (usually Zillow home value)
        """
        # First, check the report for the latest Zillow value
        zillow_value = report.get("zillow_home_value", 0)
        
        # Fall back to the static trust info if report has no value
        if not zillow_value:
            trust_info = client.get("trust_info", {})
            if isinstance(trust_info, str):
                import json
                trust_info = json.loads(trust_info)
            zillow_value = float(trust_info.get("zillow_value", 0))
        
        return zillow_value
    
    
    @classmethod
    def calculate_liabilities_total(cls, client):
        """
        Sum all liability balances.
        
        Liabilities are displayed as a separate section in the TCC.
        They are NOT subtracted from net worth.
        
        Args:
            client (dict): Client profile with liabilities list
        
        Returns:
            float: Sum of all liability balances
        """
        liabilities = client.get("liabilities", [])
        if isinstance(liabilities, str):
            import json
            liabilities = json.loads(liabilities)
        
        total = 0.0
        for liability in liabilities:
            total += float(liability.get("balance", 0))
        
        return total
    
    
    # ============================================
    # BUFFER / FLOOR CALCULATIONS (User Clarified)
    # ============================================
    
    @classmethod
    def calculate_buffer_warnings(cls, client, report):
        """
        Check all accounts for floor violations.
        
        Rule: Each account must maintain a $1,000 minimum balance.
        If any account is at or below floor, return a warning.
        
        Args:
            client (dict): Client profile
            report (dict): Report with balances
        
        Returns:
            list: Warning messages for accounts below floor
        """
        warnings = []
        account_balances = report.get("account_balances", {})
        
        if isinstance(account_balances, str):
            import json
            account_balances = json.loads(account_balances)
        
        # Check each account in the report
        for account_id, balance in account_balances.items():
            if account_id == "_total":
                continue  # Skip totals
            
            balance = float(balance or 0)
            if balance < cls.FLOOR:
                warnings.append(
                    f"Account {account_id} is below floor: ${balance:,.2f} "
                    f"(minimum required: ${cls.FLOOR:,.2f})"
                )
            elif balance == cls.FLOOR:
                warnings.append(
                    f"Account {account_id} is at floor: ${balance:,.2f} "
                    f"(minimum required: ${cls.FLOOR:,.2f})"
                )
        
        return warnings
    
    
    # ============================================
    # HELPER METHODS
    # ============================================
    
    @classmethod
    def count_active_accounts(cls, client):
        """
        Count the number of active (non-empty) accounts for a client.
        Used for floor calculation ($1,000 per account).
        
        Args:
            client (dict): Client profile
        
        Returns:
            int: Number of accounts
        """
        count = 0
        
        # Count retirement accounts (both primary and spouse)
        count += len(client.get("retirement_accounts", []))
        if client.get("is_married"):
            count += len(client.get("retirement_accounts", []))  # Spouse's accounts
        
        # Count non-retirement accounts
        count += len(client.get("non_retirement_accounts", []))
        
        return max(count, 1)  # Always return at least 1 to ensure some floor
    
    
    @classmethod
    def get_account_breakdown(cls, client, report, category):
        """
        Get a detailed breakdown of accounts for display in the TCC.
        
        Returns a list of dicts with account name and balance.
        
        Args:
            client (dict): Client profile
            report (dict): Report with balances
            category (str): 'c1_retirement', 'c2_retirement', or 'non_retirement'
        
        Returns:
            list: [{name, balance, type}, ...]
        """
        account_balances = report.get("account_balances", {})
        if isinstance(account_balances, str):
            import json
            account_balances = json.loads(account_balances)
        
        breakdown = []
        
        if category in ["c1_retirement", "c2_retirement"]:
            accounts = client.get("retirement_accounts", [])
            prefix = "c1_ret_" if category == "c1_retirement" else "c2_ret_"
            
            for idx, account in enumerate(accounts, 1):
                account_id = f"{prefix}{idx}"
                balance = float(account_balances.get(account_id, 0))
                breakdown.append({
                    "name": account.get("type", f"Retirement Account {idx}"),
                    "balance": balance,
                    "type": "retirement"
                })
        
        elif category == "non_retirement":
            accounts = client.get("non_retirement_accounts", [])
            
            for idx, account in enumerate(accounts, 1):
                account_id = f"non_ret_{idx}"
                balance = float(account_balances.get(account_id, 0))
                breakdown.append({
                    "name": account.get("type", f"Brokerage Account {idx}"),
                    "balance": balance,
                    "type": "non_retirement"
                })
        
        return breakdown
    
    
    @classmethod
    def get_liability_breakdown(cls, client):
        """
        Get a detailed breakdown of liabilities for display.
        
        Returns:
            list: [{type, balance, interest_rate}, ...]
        """
        liabilities = client.get("liabilities", [])
        if isinstance(liabilities, str):
            import json
            liabilities = json.loads(liabilities)
        
        return [
            {
                "type": liab.get("type", "Liability"),
                "balance": float(liab.get("balance", 0)),
                "interest_rate": float(liab.get("interest_rate", 0))
            }
            for liab in liabilities
        ]


# ============================================
# CONVENIENCE FUNCTION (for imports)
# ============================================

def calculate_all(client, report):
    """
    Convenience function to run all calculations.
    
    Args:
        client (dict): Client profile
        report (dict): Report data
    
    Returns:
        dict: Complete calculation results
    """
    return Calculator.calculate_all(client, report)
