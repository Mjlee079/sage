"""
SAGEN-Sync: Automated Wealth Orchestrator
Configuration Module
====================

Centralizes all application configuration.
Environment variables override defaults when available.

Environment Variables:
    RAILWAY_DATABASE_PATH: Path to SQLite database file
    SECRET_KEY: Flask session encryption key
    CANVA_API_KEY: API key for Canva export (V2)
    FLASK_ENV: 'development' or 'production'
"""

import os

class Config:
    """
    Base configuration class.
    
    Attributes:
        SECRET_KEY (str): Encryption key for Flask sessions
        DATABASE_PATH (str): Full path to SQLite database file
        CANVA_API_KEY (str): Optional API key for Canva integration
        MAX_CONTENT_LENGTH (int): Max upload size (10MB)
    """
    
    # Flask secret key - used for session cookies and CSRF protection
    # In production, set via environment variable
    SECRET_KEY = os.environ.get("SECRET_KEY", "sagen-sync-dev-key-2026")
    
    # Database path - defaults to instance folder for portability
    # Railway uses persistent volumes for the 'instance' directory
    DATABASE_PATH = os.environ.get(
        "RAILWAY_DATABASE_PATH",
        os.path.join(os.path.dirname(__file__), "..", "instance", "sagen_sync.db")
    )
    
    # Canva API - remains empty in V1, populated in V2
    CANVA_API_KEY = os.environ.get("CANVA_API_KEY", None)
    
    # Security settings
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10 MB file upload limit
    
    # Application constants
    FLOOR_AMOUNT = 1000  # Minimum buffer per account ($1,000)
    PRIVATE_RESERVE_MONTHS = 6  # Target: 6 months of expenses
    
    # Client limits (soft constraints)
    MAX_ACCOUNTS_PER_CLIENT = 20  # Generous limit
    MAX_LIABILITIES = 5
    
    # Financial year configuration
    QUARTERS = {
        "Q1": {"start_month": 1, "end_month": 3},
        "Q2": {"start_month": 4, "end_month": 6},
        "Q3": {"start_month": 7, "end_month": 9},
        "Q4": {"start_month": 10, "end_month": 12}
    }
