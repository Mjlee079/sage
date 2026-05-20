"""
SAGEN-Sync: Automated Wealth Orchestrator
Database Module
===============

Handles all database operations using SQLite.
Provides a clean interface for app initialization and query execution.

Schema Design:
    clients: Static client information (one per client/family)
    reports: Quarterly report data (one per quarter per client)
    audit_logs: Compliance tracking (V2 extensibility)

All tables use INTEGER PRIMARY KEY for auto-increment IDs.
JSON columns store flexible data (account lists, liability details).
"""

import sqlite3
import json
from datetime import datetime
from flask import g, current_app


def get_db():
    """
    Get a database connection for the current request.
    
    Uses Flask's g object to persist the connection across
    a single request (not across requests).
    
    Returns:
        sqlite3.Connection: Active database connection
    """
    if "db" not in g:
        # Connect with row factory for dict-like access
        g.db = sqlite3.connect(
            current_app.config["DATABASE_PATH"],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row  # Access columns by name
    return g.db


def close_db(e=None):
    """
    Close the database connection at the end of each request.
    Registered as a teardown function on the Flask app.
    """
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db(app):
    """
    Initialize the database schema.
    Creates all tables if they don't exist.
    Also registers the close_db teardown function.
    
    Called once when the Flask app starts.
    """
    # Register teardown to close DB after each request
    app.teardown_appcontext(close_db)
    
    # Create tables within app context
    with app.app_context():
        db = get_db()
        create_tables(db)


def create_tables(db):
    """
    Create all database tables if they don't exist.
    
    Tables:
        clients: Static client profile data
        reports: Quarterly financial report data
        audit_logs: V2 compliance tracking (currently unused)
    
    Args:
        db (sqlite3.Connection): Active database connection
    """
    cursor = db.cursor()
    
    # ============================================================
    # CLIENTS TABLE
    # Stores static client information entered once during setup.
    # JSON fields allow flexible account and liability structures.
    # ============================================================
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            
            -- Basic Info (required)
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            date_of_birth TEXT NOT NULL,  -- YYYY-MM-DD format
            ssn_last_four TEXT NOT NULL,  -- e.g., "1234"
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            
            -- Marital Status
            is_married INTEGER DEFAULT 0,  -- 0 = single, 1 = married
            
            -- Spouse Info (optional, NULL if single)
            spouse_first_name TEXT,
            spouse_last_name TEXT,
            spouse_dob TEXT,
            spouse_ssn_last_four TEXT,
            
            -- Financial Info (static)
            monthly_salary REAL DEFAULT 0,      -- After-tax monthly income
            agreed_expense_budget REAL DEFAULT 0, -- Agreed monthly expense budget
            private_reserve_target REAL DEFAULT 0, -- If manually set; otherwise auto-calc
            
            -- Flexible Data (stored as JSON for extensibility)
            retirement_accounts TEXT DEFAULT '[]',    -- JSON: [{type, last_four, is_spouse}]
            non_retirement_accounts TEXT DEFAULT '[]',  -- JSON: [{type, last_four, is_joint}]
            trust_info TEXT DEFAULT '{}',               -- JSON: {address, property_value}
            liabilities TEXT DEFAULT '[]',            -- JSON: [{type, balance, interest_rate}]
            
            -- Metadata
            notes TEXT
        )
    """)
    
    # ============================================================
    # REPORTS TABLE
    # Stores quarterly financial data entered before each client meeting.
    # Links to clients table via client_id.
    # ============================================================
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER NOT NULL,
            quarter TEXT NOT NULL,          -- Q1, Q2, Q3, or Q4
            year INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            
            -- Dynamic Balances (JSON for flexibility)
            account_balances TEXT DEFAULT '{}',  -- JSON: {account_id: balance}
            zillow_home_value REAL DEFAULT 0,     -- Trust property Zestimate
            private_reserve_balance REAL DEFAULT 0,
            
            -- SACS Data
            inflow_amount REAL DEFAULT 0,
            outflow_amount REAL DEFAULT 0,
            excess_amount REAL DEFAULT 0,       -- Auto-calculated
            
            -- TCC Data
            total_retirement_client1 REAL DEFAULT 0,
            total_retirement_client2 REAL DEFAULT 0,
            total_non_retirement REAL DEFAULT 0,
            trust_value REAL DEFAULT 0,
            total_liabilities REAL DEFAULT 0,
            grand_total REAL DEFAULT 0,
            
            -- Status & Output
            status TEXT DEFAULT 'draft',  -- draft, finalized, archived
            pdf_sacs_path TEXT,           -- Path to generated SACS PDF
            pdf_tcc_path TEXT,            -- Path to generated TCC PDF
            
            -- Foreign key constraint
            FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE
        )
    """)
    
    # ============================================================
    # AUDIT_LOGS TABLE (V2 Extensibility)
    # Prepared for future compliance and auditing requirements.
    # Currently unused but schema is ready.
    # ============================================================
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action TEXT NOT NULL,           -- e.g., 'data_pull', 'report_generated'
            user_id TEXT,                   -- Who performed the action
            client_id INTEGER,              -- Which client affected
            details TEXT DEFAULT '{}',      -- JSON: additional context
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create indexes for common queries
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_reports_client ON reports(client_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_reports_quarter ON reports(quarter, year)")
    
    db.commit()
    
    
def execute_query(query, params=(), fetch_one=False):
    """
    Execute a parameterized SQL query.
    
    This helper provides safe query execution (prevents SQL injection)
    and consistent error handling across the application.
    
    Args:
        query (str): SQL query string with ? placeholders
        params (tuple): Values to substitute into the query
        fetch_one (bool): Return single row or all rows
    
    Returns:
        dict or list: Query results
    """
    db = get_db()
    cursor = db.cursor()
    
    try:
        cursor.execute(query, params)
        db.commit()
        
        # For SELECT queries, return results
        if query.strip().upper().startswith("SELECT"):
            if fetch_one:
                row = cursor.fetchone()
                return dict(row) if row else None
            return [dict(row) for row in cursor.fetchall()]
        
        # For INSERT, return the last inserted ID
        return cursor.lastrowid
        
    except sqlite3.Error as e:
        db.rollback()
        current_app.logger.error(f"Database error: {e}")
        raise
