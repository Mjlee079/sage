"""
SAGEN-Sync: Report Routes
==========================

Handles report generation, data entry, and preview.

URL Patterns:
    /report/<client_id>/new             → Create a new report for a client
    /report/<client_id>/entry/<report_id> → Quarterly data entry form
    /report/<report_id>/update          → POST: Save entered balances
    /report/<report_id>/finalize        → POST: Run calculations and mark as finalized
    /report/<report_id>/preview         → Preview calculated results before PDF
    /report/<report_id>                 → View finalized report

Templates: report_entry.html, report_preview.html
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from app.models.client import Client
from app.models.report import Report
from app.models.calculations import Calculator

bp = Blueprint("report", __name__, url_prefix="/report")


@bp.route("/<int:client_id>/new")
def new_report(client_id):
    """
    Create a new report (draft) for a client.
    
    Creates a new record in the 'reports' table with status 'draft'.
    Redirects to the data entry form where the user enters balances.
    
    Args:
        client_id (int): The client to generate a report for
    
    Returns:
        Redirect to the data entry form
    """
    client = Client.get_by_id(client_id)
    if not client:
        abort(404, "Client not found")
    
    # Get quarter/year from query params or default to current
    from datetime import datetime
    now = datetime.now()
    quarter = request.args.get("quarter", f"Q{(now.month - 1) // 3 + 1}")
    year = int(request.args.get("year", now.year))
    
    # Create the report (status = 'draft')
    report_id = Report.create(client_id, quarter, year)
    
    flash(f"New report created for {quarter} {year}. Enter quarterly balances below.", "info")
    return redirect(url_for("report.entry_form", client_id=client_id, report_id=report_id))


@bp.route("/<int:client_id>/entry/<int:report_id>")
def entry_form(client_id, report_id):
    """
    Display the quarterly data entry form.
    
    This is the main interface where the team enters current balances.
    All static data (salary, budget, account structure) is pre-filled.
    Dynamic fields (balances) are blank or show last quarter's values.
    
    Form sections:
    1. SACS Section: Inflow (salary), Outflow (budget), Private Reserve balance
    2. TCC Section: Retirement and non-retirement account balances
    3. Trust: Zillow home value
    4. Liabilities: Current balances
    
    Args:
        client_id (int): The client's ID
        report_id (int): The report being created
    
    Returns:
        Rendered report_entry.html with pre-filled data
    """
    client = Client.get_by_id(client_id)
    report = Report.get_by_id(report_id)
    
    if not client or not report:
        abort(404)
    
    # Get the previous quarter's report (for reference values)
    previous_report = Report.get_latest(client_id)
    if previous_report and previous_report["id"] == report_id:
        previous_report = None  # Don't show current report as reference
    
    # Get account list for display
    accounts = Client.get_account_names(client)
    
    return render_template(
        "report_entry.html",
        client=client,
        report=report,
        accounts=accounts,
        previous_report=previous_report,
        floor=1000  # $1,000 floor per account
    )


@bp.route("/<int:report_id>/update", methods=["POST"])
def update_balances(report_id):
    """
    Save the quarterly balances from the data entry form.
    
    Processes form data:
        - account_balances: Dictionary of {account_id: balance}
        - zillow_home_value: Current Zillow estimate
        - private_reserve_balance: Current savings balance
    
    Args:
        report_id (int): The report to update
    
    Returns:
        Redirect to preview page
    """
    try:
        # Extract account balances from form
        account_balances = {}
        for key in request.form:
            if key.startswith("balance_"):
                account_id = key.replace("balance_", "")
                balance = request.form.get(key, "0").replace(",", "")
                account_balances[account_id] = float(balance) if balance else 0
        
        data = {
            "account_balances": account_balances,
            "zillow_home_value": float(request.form.get("zillow_home_value", 0)),
            "private_reserve_balance": float(request.form.get("private_reserve_balance", 0))
        }
        
        Report.update_balances(report_id, data)
        flash("Balances saved successfully. Review calculations below.", "success")
        
        # Redirect to preview page
        return redirect(url_for("report.preview", report_id=report_id))
        
    except ValueError as e:
        flash(f"Invalid data: {e}", "error")
        return redirect(url_for("report.entry_form", report_id=report_id))


@bp.route("/<int:report_id>/finalize", methods=["POST"])
def finalize_report(report_id):
    """
    Finalize a report: run calculations and mark as 'finalized'.
    
    This action triggers the Calculator engine which:
        1. SACS: Excess = Inflow - Outflow
        2. TCC: Sum all accounts by type
        3. Buffer: Check all accounts against $1,000 floor
    
    After finalization, the report can be downloaded as PDF.
    
    Args:
        report_id (int): The report to finalize
    
    Returns:
        Redirect to report view or PDF generation page
    """
    try:
        report = Report.get_by_id(report_id)
        if not report:
            abort(404)
        
        # Get the client profile (needed for calculations)
        client = Client.get_by_id(report["client_id"])
        
        # Run all calculations
        calculations = Report.finalize(report_id, client)
        
        flash("Report finalized! Generated PDFs are ready for download.", "success")
        return redirect(url_for("pdf.download_options", report_id=report_id))
        
    except Exception as e:
        flash(f"Error finalizing report: {e}", "error")
        return redirect(url_for("report.preview", report_id=report_id))


@bp.route("/<int:report_id>/preview")
def preview(report_id):
    """
    Preview the calculated results before finalization.
    
    Shows:
        - SACS: Inflow, Outflow, Excess, Private Reserve Target
        - TCC: All account totals, Grand Total, Liabilities
        - Buffer warnings (accounts below $1,000)
    
    User can:
        - Go back and edit balances
        - Finalize the report (triggers PDF generation)
    
    Args:
        report_id (int): The report to preview
    
    Returns:
        Rendered report_preview.html
    """
    report = Report.get_by_id(report_id)
    if not report:
        abort(404)
    
    client = Client.get_by_id(report["client_id"])
    
    # Run calculations for preview (don't save to DB yet)
    calculations = Calculator.calculate_all(client, report)
    
    return render_template(
        "report_preview.html",
        client=client,
        report=report,
        calculations=calculations
    )
