"""
SAGEN-Sync: Report History Routes
==================================

Handles viewing and re-downloading past reports.

URL Patterns:
    /history                  → All reports (with filters)
    /history/client/<id>     → Reports for a specific client
    /history/<id>/re-download → Re-download a finalized report

Template: history.html
"""

from flask import Blueprint, render_template, redirect, url_for, abort
from app.models.client import Client
from app.models.report import Report

bp = Blueprint("history", __name__, url_prefix="/history")


@bp.route("/")
def all_reports():
    """
    Display all historical reports across all clients.
    
    Shows a table with:
        - Client name
        - Quarter/Year
        - Status (finalized, draft, archived)
        - Date generated
        - Re-download button
    
    User can filter by:
        - Quarter (Q1, Q2, Q3, Q4)
        - Year
        - Client
    
    Returns:
        Rendered history.html
    """
    reports = Report.get_all()
    
    # Enrich with client names
    for report in reports:
        client = Client.get_by_id(report["client_id"])
        if client:
            report["client_name"] = f"{client['first_name']} {client['last_name']}"
        else:
            report["client_name"] = "Unknown"
    
    return render_template("history.html", reports=reports, view="all")


@bp.route("/client/<int:client_id>")
def client_reports(client_id):
    """
    Display all reports for a specific client.
    
    Same layout as all_reports but filtered to one client.
    """
    client = Client.get_by_id(client_id)
    if not client:
        abort(404)
    
    reports = Report.get_by_client(client_id)
    
    return render_template(
        "history.html",
        reports=reports,
        client=client,
        view="client"
    )


@bp.route("/<int:report_id>/re-download")
def re_download(report_id):
    """
    Redirect to the PDF download page for a previously finalized report.
    
    If the report is still in 'draft' status, shows a message to finalize first.
    """
    report = Report.get_by_id(report_id)
    if not report:
        abort(404)
    
    if report["status"] != "finalized":
        return "This report is still in draft status. Please finalize it first.", 400
    
    # Redirect to the download options page
    return redirect(url_for("pdf.download_options", report_id=report_id))
