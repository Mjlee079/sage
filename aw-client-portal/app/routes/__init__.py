"""
SAGEN-Sync Routes Package
==========================

Blueprint registration for all application routes.
Each module handles a specific feature area.

Blueprints:
    dashboard: Home page, client list, stats
    client: Client CRUD (add, edit, view, delete)
    report: Report generation, data entry, preview
    pdf: PDF download generation
    history: Report history and re-download
    canva: Canva export (V2 stub)
"""

from .dashboard import bp as dashboard_bp
from .client import bp as client_bp
from .report import bp as report_bp
from .pdf import bp as pdf_bp
from .history import bp as history_bp
from .canva import bp as canva_bp

__all__ = [
    "dashboard_bp",
    "client_bp",
    "report_bp",
    "pdf_bp",
    "history_bp",
    "canva_bp"
]
