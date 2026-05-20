"""
SAGEN-Sync: API Routes (JSON-Only)
====================================

All backend routes serve JSON instead of HTML templates.
CORS is enabled for the separate frontend.
"""

from flask import Blueprint, jsonify, request, current_app, send_file
from app.models.client import Client
from app.models.report import Report
from app.models.calculations import Calculator
import json
import os
import tempfile

bp = Blueprint("api", __name__, url_prefix="/api")


def json_response(data, status=200):
    """Create a JSON response with CORS headers."""
    response = jsonify(data)
    return response, status


@bp.after_request
def after_request(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
    response.headers.add("Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS")
    response.headers.set("X-Frame-Options", "SAMEORIGIN")
    response.headers.set("X-Content-Type-Options", "nosniff")
    return response


# ============================================
# DASHBOARD
# ============================================

@bp.route("/dashboard")
def dashboard():
    clients = Client.get_all()
    reports = Report.get_all()
    recent_reports = reports[:5]
    
    return json_response({
        "clients": clients,
        "client_count": len(clients),
        "report_count": len(reports),
        "recent_reports": recent_reports
    })


# ============================================
# CLIENTS
# ============================================

@bp.route("/clients")
def list_clients():
    clients = Client.get_all()
    return json_response({"clients": clients})


@bp.route("/clients", methods=["POST"])
def create_client():
    try:
        data = request.get_json() or {}
        client_id = Client.create(data)
        return json_response({"id": client_id, "message": "Client created successfully"}, 201)
    except ValueError as e:
        return json_response({"error": str(e)}, 400)
    except Exception as e:
        return json_response({"error": str(e)}, 500)


@bp.route("/clients/<int:client_id>")
def get_client(client_id):
    client = Client.get_by_id(client_id)
    if not client:
        return json_response({"error": "Client not found"}, 404)
    return json_response({"client": client})


@bp.route("/clients/<int:client_id>", methods=["PUT"])
def update_client(client_id):
    try:
        data = request.get_json() or {}
        Client.update(client_id, data)
        return json_response({"message": "Client updated successfully"})
    except ValueError as e:
        return json_response({"error": str(e)}, 400)
    except Exception as e:
        return json_response({"error": str(e)}, 500)


@bp.route("/clients/<int:client_id>", methods=["DELETE"])
def delete_client(client_id):
    try:
        Client.delete(client_id)
        return json_response({"message": "Client deleted successfully"})
    except Exception as e:
        return json_response({"error": str(e)}, 500)


# ============================================
# REPORTS
# ============================================

@bp.route("/reports")
def list_reports():
    reports = Report.get_all()
    return json_response({"reports": reports})


@bp.route("/reports/<int:report_id>")
def get_report(report_id):
    report = Report.get_by_id(report_id)
    if not report:
        return json_response({"error": "Report not found"}, 404)
    return json_response({"report": report})


@bp.route("/clients/<int:client_id>/reports")
def get_client_reports(client_id):
    reports = Report.get_by_client(client_id)
    return json_response({"reports": reports})


@bp.route("/clients/<int:client_id>/reports", methods=["POST"])
def create_report(client_id):
    try:
        data = request.get_json() or {}
        quarter = data.get("quarter")
        year = data.get("year")
        
        if not quarter or not year:
            return json_response({"error": "quarter and year are required"}, 400)
        
        report_id = Report.create(client_id, quarter, int(year))
        return json_response({"id": report_id, "message": "Report created successfully"}, 201)
    except ValueError as e:
        return json_response({"error": str(e)}, 400)
    except Exception as e:
        return json_response({"error": str(e)}, 500)


@bp.route("/reports/<int:report_id>/balances", methods=["PUT"])
def update_balances(report_id):
    try:
        data = request.get_json() or {}
        Report.update_balances(report_id, data)
        return json_response({"message": "Balances updated successfully"})
    except Exception as e:
        return json_response({"error": str(e)}, 500)


@bp.route("/reports/<int:report_id>/finalize", methods=["POST"])
def finalize_report(report_id):
    try:
        report = Report.get_by_id(report_id)
        if not report:
            return json_response({"error": "Report not found"}, 404)
        
        client = Client.get_by_id(report["client_id"])
        calculations = Report.finalize(report_id, client)
        
        return json_response({"message": "Report finalized", "calculations": calculations})
    except Exception as e:
        return json_response({"error": str(e)}, 500)


@bp.route("/reports/<int:report_id>/preview")
def preview_report(report_id):
    report = Report.get_by_id(report_id)
    if not report:
        return json_response({"error": "Report not found"}, 404)
    
    client = Client.get_by_id(report["client_id"])
    calculations = Calculator.calculate_all(client, report)
    
    return json_response({"report": report, "client": client, "calculations": calculations})


# ============================================
# HISTORY
# ============================================

@bp.route("/history")
def all_reports():
    reports = Report.get_all()
    return json_response({"reports": reports})


# ============================================
# PDF GENERATION
# ============================================

@bp.route("/reports/<int:report_id>/sacs")
def download_sacs(report_id):
    report = Report.get_by_id(report_id)
    if not report:
        return json_response({"error": "Report not found"}, 404)
    
    client = Client.get_by_id(report["client_id"])
    
    from flask import render_template_string
    template_path = os.path.join(current_app.root_path, "pdf_templates", "sacs_template.html")
    with open(template_path, "r") as f:
        template = f.read()
    
    html_content = render_template_string(template, client=client, report=report, calculations=Calculator.calculate_all(client, report))
    
    try:
        from xhtml2pdf import pisa
        temp_dir = tempfile.gettempdir()
        filename = f"SACS_{report['quarter']}_{report['year']}_{client['last_name']}.pdf"
        pdf_path = os.path.join(temp_dir, filename)
        
        with open(pdf_path, "w+b") as pdf_file:
            pisa_status = pisa.CreatePDF(html_content, dest=pdf_file)
        
        if pisa_status.err:
            return json_response({"error": "PDF generation failed"}, 500)
        
        return send_file(pdf_path, mimetype="application/pdf", as_attachment=True, download_name=filename)
    except Exception as e:
        return json_response({"error": f"PDF generation failed: {str(e)}"}, 500)


@bp.route("/reports/<int:report_id>/tcc")
def download_tcc(report_id):
    report = Report.get_by_id(report_id)
    if not report:
        return json_response({"error": "Report not found"}, 404)
    
    client = Client.get_by_id(report["client_id"])
    
    from flask import render_template_string
    template_path = os.path.join(current_app.root_path, "pdf_templates", "tcc_template.html")
    with open(template_path, "r") as f:
        template = f.read()
    
    html_content = render_template_string(template, client=client, report=report, calculations=Calculator.calculate_all(client, report))
    
    try:
        from xhtml2pdf import pisa
        temp_dir = tempfile.gettempdir()
        filename = f"TCC_{report['quarter']}_{report['year']}_{client['last_name']}.pdf"
        pdf_path = os.path.join(temp_dir, filename)
        
        with open(pdf_path, "w+b") as pdf_file:
            pisa_status = pisa.CreatePDF(html_content, dest=pdf_file)
        
        if pisa_status.err:
            return json_response({"error": "PDF generation failed"}, 500)
        
        return send_file(pdf_path, mimetype="application/pdf", as_attachment=True, download_name=filename)
    except Exception as e:
        return json_response({"error": f"PDF generation failed: {str(e)}"}, 500)


# ============================================
# CANVA (V2 STUB)
# ============================================

@bp.route("/canva/<int:report_id>/export")
def export_to_canva(report_id):
    api_key = current_app.config.get("CANVA_API_KEY")
    
    if not api_key:
        return json_response({
            "status": "not_implemented",
            "message": "Canva export will be available in V2.",
            "version": "1.0"
        }, 501)
    
    return json_response({
        "status": "not_implemented",
        "message": "Canva API integration is planned for V2",
        "version": "1.0"
    }, 501)
