"""
SAGEN-Sync Models Package
=========================

Exposes the core data models for the application.
Each model handles CRUD operations for its respective domain.

Models:
    Client: Static client profiles, account structures
    Report: Quarterly financial data and report generation status

Usage:
    from app.models import Client
    
    # Create a new client
    client_id = Client.create(data)
    
    # Retrieve a client
    client = Client.get_by_id(client_id)
"""

from .client import Client
from .report import Report

__all__ = ["Client", "Report"]
