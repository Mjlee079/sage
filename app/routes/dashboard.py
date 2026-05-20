"""
SAGEN-Sync: Dashboard Routes
============================

Handles the main entry point of the application.
Shows the client list, quick stats, and recent reports.

URL Patterns:
    /                   → Main dashboard
    /dashboard          → Redirect to / (convenience)

Template: dashboard.html
"""

from flask import Blueprint, render_template, redirect, url_for
from app.models.client import Client
from app.models.report import Report

# Create blueprint (modular routing component)
# url_prefix="" means these routes are at the root level
bp = Blueprint("dashboard", __name__, url_prefix="/")


@bp.route("/")
def index():
    """
    Main Dashboard Page
    ===================
    
    Displays:
        - Total number of clients
        - Total number of reports generated
        - List of all clients with last report date
        - Quick actions (Add Client, Generate Report)
    
    Data passed to template:
        clients: List of all client dicts
        report_count: Total reports in system
        recent_reports: Last 5 generated reports
    """
    # Fetch all clients from the database
    clients = Client.get_all()
    
    # Calculate statistics
    report_count = len(Report.get_all())
    recent_reports = Report.get_all()[:5]  # Last 5 reports
    
    # For each client, check if they have a last report date
    for client in clients:
        last_report = Client.get_last_report_date(client["id"])
        if last_report:
            client["last_report"] = last_report
        else:
            client["last_report"] = None
    
    return render_template(
        "dashboard.html",
        clients=clients,
        client_count=len(clients),
        report_count=report_count,
        recent_reports=recent_reports
    )
