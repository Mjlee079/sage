"""
SAGEN-Sync: PDF Routes
========================

Handles PDF generation and download for SACS and TCC reports.

Uses xhtml2pdf for cross-platform PDF generation (works on Windows without GTK).

URL Patterns:
    /pdf/<report_id>/download   → Show download options
    /pdf/<report_id>/sacs       → Download SACS PDF
    /pdf/<report_id>/tcc        → Download TCC PDF
"""

from flask import Blueprint, send_file, render_template_string, url_for, abort, current_app
from app.models.client import Client
from app.models.report import Report
from app.models.calculations import Calculator
import os
import tempfile

bp = Blueprint("pdf", __name__, url_prefix="/pdf")

# xhtml2pdf availability
XHTML2PDF_AVAILABLE = None


def xhtml2pdf_available():
    """Check if xhtml2pdf is installed and available."""
    global XHTML2PDF_AVAILABLE
    if XHTML2PDF_AVAILABLE is not None:
        return XHTML2PDF_AVAILABLE
    
    try:
        from xhtml2pdf import pisa
        XHTML2PDF_AVAILABLE = True
        return True
    except (ImportError, OSError):
        XHTML2PDF_AVAILABLE = False
        return False


def generate_pdf(html_content, css_content=None, filename="report.pdf"):
    """
    Generate a PDF from HTML content using xhtml2pdf.
    
    Args:
        html_content (str): The complete HTML document to render
        css_content (str): Optional CSS stylesheet (embedded in HTML)
        filename (str): The filename for the download
    
    Returns:
        Flask Response: PDF file for download
    """
    from xhtml2pdf import pisa
    
    # Create a temporary file for the PDF
    temp_dir = tempfile.gettempdir()
    pdf_path = os.path.join(temp_dir, filename)
    
    # Generate PDF using xhtml2pdf
    with open(pdf_path, "w+b") as pdf_file:
        pisa_status = pisa.CreatePDF(html_content, dest=pdf_file)
    
    if pisa_status.err:
        abort(500, "PDF generation failed")
    
    return send_file(
        pdf_path,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=filename
    )


@bp.route("/<int:report_id>/download")
def download_options(report_id):
    """
    Display PDF download options after report is finalized.
    """
    report = Report.get_by_id(report_id)
    if not report:
        abort(404)
    
    client = Client.get_by_id(report["client_id"])
    calculations = Calculator.calculate_all(client, report)
    
    return render_template_string("""
        {% extends "base.html" %}
        {% block title %}Download Reports | SAGEN-Sync{% endblock %}
        {% block content %}
        <div class="container" style="max-width: 700px; margin: 0 auto;">
            <header class="page-header" style="text-align: center;">
                <h1>Download Reports</h1>
                <p class="lead">
                    {{ client.first_name }} {{ client.last_name }} &mdash; {{ report.quarter }} {{ report.year }}
                </p>
            </header>
            
            <div class="calculation-card" style="text-align: center; padding: 2rem;">
                <h3 style="margin-bottom: 1.5rem;">Select Report to Download</h3>
                
                <div style="display: flex; gap: 1.5rem; justify-content: center; flex-wrap: wrap;">
                    <a href="{{ url_for('pdf.download_sacs', report_id=report.id) }}" 
                       class="btn btn-primary btn-lg" 
                       style="min-width: 200px; padding: 1rem 2rem; font-size: 1.1rem;">
                        Download SACS (Cash Flow)
                    </a>
                    
                    <a href="{{ url_for('pdf.download_tcc', report_id=report.id) }}" 
                       class="btn btn-outline btn-lg" 
                       style="min-width: 200px; padding: 1rem 2rem; font-size: 1.1rem;">
                        Download TCC (Net Worth)
                    </a>
                </div>
                
                <div style="margin-top: 2rem; padding-top: 1.5rem; border-top: 1px solid #E2E8F0;">
                    <h4 style="margin-bottom: 1rem;">Report Summary</h4>
                    <table style="width: 100%; text-align: left; border-collapse: collapse;">
                        <tr>
                            <td style="padding: 0.5rem; color: #64748B;">Excess (Monthly)</td>
                            <td style="padding: 0.5rem; font-weight: bold; text-align: right;">${{ "{:.2f}".format(calculations.sacs.excess) }}</td>
                        </tr>
                        <tr>
                            <td style="padding: 0.5rem; color: #64748B;">Grand Total (Net Worth)</td>
                            <td style="padding: 0.5rem; font-weight: bold; text-align: right;">${{ "{:.2f}".format(calculations.tcc.grand_total) }}</td>
                        </tr>
                    </table>
                </div>
            </div>
            
            <div style="text-align: center; margin-top: 1.5rem;">
                <a href="{{ url_for('client.view_client', client_id=client.id) }}" class="btn btn-outline">
                    &larr; Back to Client Profile
                </a>
            </div>
        </div>
        {% endblock %}
    """, report=report, client=client, calculations=calculations)


@bp.route("/<int:report_id>/sacs")
def download_sacs(report_id):
    """
    Generate and download the SACS (cash flow) PDF report.
    """
    report = Report.get_by_id(report_id)
    if not report:
        abort(404)
    
    client = Client.get_by_id(report["client_id"])
    
    # Load and render the SACS template
    template_path = os.path.join(current_app.root_path, "pdf_templates", "sacs_template.html")
    with open(template_path, "r") as f:
        template = f.read()
    
    html_content = render_template_string(template, client=client, report=report, calculations=Calculator.calculate_all(client, report))
    
    if not xhtml2pdf_available():
        abort(500, "PDF library not available. Please install xhtml2pdf.")
    
    filename = f"SACS_{report['quarter']}_{report['year']}_{client['last_name']}.pdf"
    return generate_pdf(html_content, filename=filename)


@bp.route("/<int:report_id>/tcc")
def download_tcc(report_id):
    """
    Generate and download the TCC (net worth) PDF report.
    """
    report = Report.get_by_id(report_id)
    if not report:
        abort(404)
    
    client = Client.get_by_id(report["client_id"])
    
    # Load and render the TCC template
    template_path = os.path.join(current_app.root_path, "pdf_templates", "tcc_template.html")
    with open(template_path, "r") as f:
        template = f.read()
    
    html_content = render_template_string(template, client=client, report=report, calculations=Calculator.calculate_all(client, report))
    
    if not xhtml2pdf_available():
        abort(500, "PDF library not available. Please install xhtml2pdf.")
    
    filename = f"TCC_{report['quarter']}_{report['year']}_{client['last_name']}.pdf"
    return generate_pdf(html_content, filename=filename)
