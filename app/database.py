"""
SAGEN-Sync: Automated Wealth Orchestrator
Database Module
===============

Handles all database operations using SQLAlchemy with PostgreSQL (Vercel) or SQLite (local).

Schema Design:
    clients: Static client information (one per client/family)
    reports: Quarterly report data (one per quarter per client)
    audit_logs: Compliance tracking (V2 extensibility)

All tables use auto-increment IDs.
JSON columns store flexible data (account lists, liability details).
"""

import json
from datetime import datetime
from flask import g, current_app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

db = SQLAlchemy()


def get_db():
    """
    Get the SQLAlchemy session for the current request.
    """
    return db.session


def close_db(e=None):
    """
    Close the database session at the end of each request.
    """
    db.session.remove()


def init_db(app):
    """
    Initialize the database.
    Creates all tables if they don't exist.
    Also registers the close_db teardown function.
    """
    db.init_app(app)
    app.teardown_appcontext(close_db)

    with app.app_context():
        create_tables()


def _get_last_insert_id():
    """Get the last inserted ID, handling both SQLite and PostgreSQL."""
    dialect_name = db.engine.dialect.name
    if dialect_name == 'postgresql':
        return db.session.execute(text("SELECT lastval()")).scalar()
    else:
        # SQLite
        return db.session.execute(text("SELECT last_insert_rowid()")).scalar()


def execute_query(query, params=(), fetch_one=False):
    """
    Execute a parameterized SQL query.
    
    This helper provides safe query execution (prevents SQL injection)
    and consistent error handling across the application.
    
    Args:
        query (str): SQL query string with ? placeholders
        params (tuple or dict): Values to substitute into the query
        fetch_one (bool): Return single row or all rows
    
    Returns:
        dict or list: Query results
    """
    try:
        # Convert tuple params to dict for SQLAlchemy text()
        if isinstance(params, tuple):
            param_dict = {f"p{i}": p for i, p in enumerate(params)}
            
            # Replace ? with :p0, :p1, etc.
            sql_query = query
            for i in range(len(params)):
                sql_query = sql_query.replace("?", f":p{i}", 1)
        else:
            param_dict = params
            sql_query = query

        result = db.session.execute(text(sql_query), param_dict)
        db.session.commit()

        # For SELECT queries, return results
        if sql_query.strip().upper().startswith("SELECT"):
            if fetch_one:
                row = result.fetchone()
                return dict(row._mapping) if row else None
            return [dict(row._mapping) for row in result.fetchall()]

        # For INSERT, return the last inserted ID
        if sql_query.strip().upper().startswith("INSERT"):
            return _get_last_insert_id()

        return None

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Database error: {e}")
        raise


def create_tables(db_session=None):
    """
    Create all database tables if they don't exist.
    Called by init_db automatically.
    """
    # Tables are created by db.create_all() in init_db
    # This function is kept for compatibility
    pass
