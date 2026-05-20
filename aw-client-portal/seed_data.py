"""
SAGEN-Sync: Sample Data Seeder
================================

Creates sample clients and reports so you can test the app immediately.
Run this once after starting the server to populate the database.

Usage:
    python seed_data.py

This creates:
    - 2 sample clients (single & married)
    - Pre-defined account structures
    - A draft report for testing
"""

import json
from datetime import datetime
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))


def seed_database():
    """Insert sample data into the database."""
    
    from app import create_app
    app = create_app()
    
    with app.app_context():
        from app.database import get_db
        db = get_db()
        cursor = db.cursor()
        
        # Check if we already have data
        cursor.execute("SELECT COUNT(*) FROM clients")
        if cursor.fetchone()[0] > 0:
            print("Database already has clients. Skipping seed.")
            db.close()
            return
        
        # =====================================================
        # CLIENT 1: Single Individual
        # =====================================================
        client1_retirement = json.dumps([
            {"type": "IRA", "last_four": "4821", "owner": "client1"},
            {"type": "Roth IRA", "last_four": "7753", "owner": "client1"}
        ])
        
        client1_non_retirement = json.dumps([
            {"type": "Brokerage", "last_four": "9921", "owner": "client1"},
            {"type": "Joint Checking", "last_four": "1103", "owner": "client1"}
        ])
        
        client1_trust = json.dumps({
            "property_address": "123 Peachtree St, Atlanta, GA 30309",
            "zillow_value": 425000.00
        })
        
        client1_liabilities = json.dumps([
            {"type": "Mortgage", "balance": 185000.00, "interest_rate": 3.5, "insurance_deductible": 2500.00},
            {"type": "Auto Loan", "balance": 12500.00, "interest_rate": 4.2, "insurance_deductible": 500.00}
        ])
        
        cursor.execute("""
            INSERT INTO clients (
                first_name, last_name, date_of_birth, ssn_last_four,
                is_married, spouse_first_name, spouse_last_name,
                monthly_salary, agreed_expense_budget, private_reserve_target,
                retirement_accounts, non_retirement_accounts, trust_info, liabilities, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "Michael", "Thompson", "1965-03-15", "4821",
            0, None, None,
            12500.00, 8500.00, 0,
            client1_retirement, client1_non_retirement, client1_trust, client1_liabilities,
            "High net worth client. Prefers quarterly meetings. Tech executive."
        ))
        
        client1_id = cursor.lastrowid
        print(f"Created client: Michael Thompson (ID: {client1_id})")
        
        # Create a report for client 1
        cursor.execute("""
            INSERT INTO reports (client_id, quarter, year, status)
            VALUES (?, ?, ?, 'draft')
        """, (client1_id, "Q2", 2026))
        
        report1_id = cursor.lastrowid
        print(f"Created draft report: Q2 2026 (ID: {report1_id})")
        
        # =====================================================
        # CLIENT 2: Married Couple
        # =====================================================
        client2_retirement = json.dumps([
            {"type": "401(k)", "last_four": "5512", "owner": "client1"},
            {"type": "IRA", "last_four": "8834", "owner": "client1"},
            {"type": "401(k)", "last_four": "2291", "owner": "spouse"},
            {"type": "Roth IRA", "last_four": "6677", "owner": "spouse"}
        ])
        
        client2_non_retirement = json.dumps([
            {"type": "Brokerage", "last_four": "4455", "owner": "joint"},
            {"type": "Joint Savings", "last_four": "3321", "owner": "joint"}
        ])
        
        client2_trust = json.dumps({
            "property_address": "456 Piedmont Ave, Atlanta, GA 30305",
            "zillow_value": 550000.00
        })
        
        client2_liabilities = json.dumps([
            {"type": "Mortgage", "balance": 320000.00, "interest_rate": 3.75, "insurance_deductible": 2500.00}
        ])
        
        cursor.execute("""
            INSERT INTO clients (
                first_name, last_name, date_of_birth, ssn_last_four,
                is_married, spouse_first_name, spouse_last_name,
                spouse_dob, spouse_ssn_last_four,
                monthly_salary, agreed_expense_budget, private_reserve_target,
                retirement_accounts, non_retirement_accounts, trust_info, liabilities, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "David", "Roberts", "1968-07-22", "2291",
            1, "Sarah", "Roberts",
            "1970-11-08", "7756",
            18000.00, 12000.00, 0,
            client2_retirement, client2_non_retirement, client2_trust, client2_liabilities,
            "Married couple, both working. 2 children in college. Comprehensive planning."
        ))
        
        client2_id = cursor.lastrowid
        print(f"Created client: David & Sarah Roberts (ID: {client2_id})")
        
        # Create a finalized report for client 2
        cursor.execute("""
            INSERT INTO reports (client_id, quarter, year, status, account_balances,
                zillow_home_value, private_reserve_balance, inflow_amount, outflow_amount,
                excess_amount, total_retirement_client1, total_retirement_client2,
                total_non_retirement, trust_value, total_liabilities, grand_total
            ) VALUES (?, ?, ?, 'finalized', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            client2_id, "Q1", 2026,
            json.dumps({
                "c1_ret_1": 95000.00, "c1_ret_2": 45000.00,
                "c2_ret_1": 78000.00, "c2_ret_2": 32000.00,
                "non_ret_1": 120000.00, "non_ret_2": 25000.00
            }),
            475000.00,
            35000.00,
            18000.00,
            12000.00,
            6000.00,
            140000.00,
            110000.00,
            145000.00,
            475000.00,
            320000.00,
            770000.00
        ))
        
        report2_id = cursor.lastrowid
        print(f"Created finalized report: Q1 2026 (ID: {report2_id})")
        
        # Commit all changes
        db.commit()
        db.close()
        
        print("\n" + "="*50)
        print("DATABASE SEEDED SUCCESSFULLY!")
        print("="*50)
        print(f"\nClients: 2")
        print(f"Reports: 2")
        print(f"\nAccess at: http://127.0.0.1:5000")
        print("="*50)


if __name__ == "__main__":
    print("Seeding database with sample data...\n")
    seed_database()
