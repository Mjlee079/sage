"""
SAGEN-Sync: Report Model
==========================

Handles all CRUD operations for quarterly financial reports.
Each report is linked to a client and contains all balances for a specific quarter/year.

Report Lifecycle:
    1. User clicks "Generate Report" → Report created with status 'draft'
    2. User enters quarterly balances → Report updated, status remains 'draft'
    3. User clicks "Finalize" → Calculations run, status changes to 'finalized'
    4. PDFs generated and saved → User can download or re-download
    5. Old reports are never deleted (history preserved)

Usage:
    from app.models.report import Report
    
    # Create new report for a client
    report_id = Report.create(1, "Q2", 2026)
    
    # Update balances
    Report.update_balances(report_id, {...})
    
    # Finalize (triggers calculations)
    Report.finalize(report_id)
    
    # Get all reports for a client
    reports = Report.get_by_client(1)
"""

import json
from datetime import datetime
from app.database import execute_query
from app.models.calculations import Calculator


class Report:
    """
    Report data model - quarterly financial data.
    
    Each report captures a snapshot of a client's financial situation
    for a specific quarter. The auto-calculation engine runs on finalize.
    """
    
    VALID_STATUSES = ["draft", "finalized", "archived"]
    VALID_QUARTERS = ["Q1", "Q2", "Q3", "Q4"]
    
    
    # ============================================
    # CREATE
    # ============================================
    
    @classmethod
    def create(cls, client_id, quarter, year):
        """
        Create a new report (draft status) for a client.
        
        Args:
            client_id (int): The client this report belongs to
            quarter (str): One of 'Q1', 'Q2', 'Q3', 'Q4'
            year (int): The year (e.g., 2026)
        
        Returns:
            int: The new report's ID
        
        Raises:
            ValueError: If quarter or year is invalid
        """
        if quarter not in cls.VALID_QUARTERS:
            raise ValueError(f"Invalid quarter: {quarter}. Must be one of {cls.VALID_QUARTERS}")
        
        if not (2000 <= year <= 2100):
            raise ValueError(f"Invalid year: {year}")
        
        query = """
            INSERT INTO reports (client_id, quarter, year, status)
            VALUES (?, ?, ?, 'draft')
        """
        
        return execute_query(query, (client_id, quarter, year))
    
    
    # ============================================
    # READ
    # ============================================
    
    @classmethod
    def get_by_id(cls, report_id):
        """
        Retrieve a single report by ID.
        
        Returns:
            dict: Report data, or None if not found
        """
        query = "SELECT * FROM reports WHERE id = ?"
        return execute_query(query, (report_id,), fetch_one=True)
    
    
    @classmethod
    def get_by_client(cls, client_id):
        """
        Get all reports for a client, ordered by year and quarter (newest first).
        
        Args:
            client_id (int): The client's ID
        
        Returns:
            list: List of report dictionaries
        """
        query = """
            SELECT * FROM reports 
            WHERE client_id = ? 
            ORDER BY year DESC, 
            CASE quarter 
                WHEN 'Q4' THEN 1 
                WHEN 'Q3' THEN 2 
                WHEN 'Q2' THEN 3 
                WHEN 'Q1' THEN 4 
            END
        """
        return execute_query(query, (client_id,))
    
    
    @classmethod
    def get_all(cls):
        """
        Get all reports across all clients, newest first.
        
        Useful for the dashboard "all reports" view.
        
        Returns:
            list: All report dictionaries with client names joined
        """
        query = """
            SELECT r.*, c.first_name, c.last_name 
            FROM reports r
            JOIN clients c ON r.client_id = c.id
            ORDER BY r.year DESC, 
            CASE r.quarter 
                WHEN 'Q4' THEN 1 
                WHEN 'Q3' THEN 2 
                WHEN 'Q2' THEN 3 
                WHEN 'Q1' THEN 4 
            END
        """
        return execute_query(query)
    
    
    @classmethod
    def get_latest(cls, client_id):
        """
        Get the most recent report for a client.
        
        Returns:
            dict: Most recent report, or None
        """
        query = """
            SELECT * FROM reports 
            WHERE client_id = ? 
            ORDER BY year DESC, 
            CASE quarter 
                WHEN 'Q4' THEN 1 
                WHEN 'Q3' THEN 2 
                WHEN 'Q2' THEN 3 
                WHEN 'Q1' THEN 4 
            END 
            LIMIT 1
        """
        return execute_query(query, (client_id,), fetch_one=True)
    
    
    # ============================================
    # UPDATE
    # ============================================
    
    @classmethod
    def update_balances(cls, report_id, data):
        """
        Update the quarterly balances from the data entry form.
        
        Args:
            report_id (int): The report to update
            data (dict): Dictionary of field names to values
                {
                    "zillow_home_value": 450000.00,
                    "private_reserve_balance": 25000.00,
                    "account_balances": {
                        "ira_1": 11000.00,
                        "roth_1": 15000.00,
                        ...
                    }
                }
        
        Returns:
            bool: True if successful
        """
        # Serialize account balances to JSON
        account_balances = json.dumps(data.get("account_balances", {}))
        
        query = """
            UPDATE reports 
            SET 
                account_balances = ?,
                zillow_home_value = ?,
                private_reserve_balance = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """
        
        params = (
            account_balances,
            float(data.get("zillow_home_value", 0)),
            float(data.get("private_reserve_balance", 0)),
            report_id
        )
        
        execute_query(query, params)
        return True
    
    
    @classmethod
    def finalize(cls, report_id, client_data):
        """
        Finalize a report: run all calculations and update totals.
        
        This is called when the user clicks "Generate Report" after
        entering all quarterly balances. It triggers the Calculator engine.
        
        Args:
            report_id (int): The report to finalize
            client_data (dict): Full client profile (needed for calculations)
        
        Returns:
            dict: Calculated report data with all totals
        """
        # Get the current report data
        report = cls.get_by_id(report_id)
        if not report:
            raise ValueError(f"Report {report_id} not found")
        
        # Run calculations
        calculations = Calculator.calculate_all(client_data, report)
        
        # Update report with calculated values
        query = """
            UPDATE reports 
            SET 
                inflow_amount = ?,
                outflow_amount = ?,
                excess_amount = ?,
                total_retirement_client1 = ?,
                total_retirement_client2 = ?,
                total_non_retirement = ?,
                trust_value = ?,
                total_liabilities = ?,
                grand_total = ?,
                status = 'finalized',
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """
        
        params = (
            calculations["sacs"]["inflow"],
            calculations["sacs"]["outflow"],
            calculations["sacs"]["excess"],
            calculations["tcc"]["total_retirement_client1"],
            calculations["tcc"]["total_retirement_client2"],
            calculations["tcc"]["total_non_retirement"],
            calculations["tcc"]["trust_value"],
            calculations["tcc"]["total_liabilities"],
            calculations["tcc"]["grand_total"],
            report_id
        )
        
        execute_query(query, params)
        
        return calculations
    
    
    @classmethod
    def update_pdf_paths(cls, report_id, sacs_path=None, tcc_path=None):
        """
        Store the file paths of generated PDFs.
        
        Args:
            report_id (int): The report to update
            sacs_path (str): Absolute path to the generated SACS PDF
            tcc_path (str): Absolute path to the generated TCC PDF
        """
        query = """
            UPDATE reports 
            SET pdf_sacs_path = ?, pdf_tcc_path = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """
        execute_query(query, (Sacs_path, tcc_path, report_id))
    
    
    # ============================================
    # DELETE
    # ============================================
    
    @classmethod
    def delete(cls, report_id):
        """
        Delete a report (rarely used - history is usually preserved).
        """
        query = "DELETE FROM reports WHERE id = ?"
        execute_query(query, (report_id,))
        return True
    
    
    # ============================================
    # HELPER METHODS
    # ============================================
    
    @classmethod
    def get_client_report_history(cls, client_id):
        """
        Get a summary of all reports for a client, showing only key dates.
        
        Returns:
            list: [{year, quarter, status, created_at}, ...]
        """
        query = """
            SELECT year, quarter, status, created_at 
            FROM reports 
            WHERE client_id = ?
            ORDER BY year DESC, 
            CASE quarter 
                WHEN 'Q4' THEN 1 
                WHEN 'Q3' THEN 2 
                WHEN 'Q2' THEN 3 
                WHEN 'Q1' THEN 4 
            END
        """
        return execute_query(query, (client_id,))
