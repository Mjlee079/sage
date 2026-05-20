"""
SAGEN-Sync: Client Routes
===========================

Handles all client CRUD operations.

URL Patterns:
    /client                        → List all clients
    /client/add                    → Add new client form
    /client/create                 → POST: Create client
    /client/<id>                   → View client details
    /client/<id>/edit              → Edit client form
    /client/<id>/update            → POST: Update client
    /client/<id>/delete            → POST: Delete client
    /client/<id>/generate-report   → POST: Start report generation

Templates: client_form.html, client_detail.html
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from app.models.client import Client
from app.models.report import Report

bp = Blueprint("client", __name__, url_prefix="/client")


@bp.route("/")
def list_clients():
    """
    List all clients.
    
    Returns:
        Rendered page with all clients grouped alphabetically.
    """
    clients = Client.get_all()
    return render_template("dashboard.html", clients=clients, view="list")


@bp.route("/add")
def add_form():
    """
    Display the "Add New Client" form.
    
    This form collects all static client data:
        - Personal info (name, DOB, SSN, marital status)
        - Spouse info (if married)
        - Account structure (retirement, non-retirement, trust)
        - Financial data (salary, budget)
        - Liabilities (mortgage, auto loans)
    
    Returns:
        Rendered client_form.html with empty fields
    """
    return render_template("client_form.html", client=None, mode="add")


@bp.route("/create", methods=["POST"])
def create_client():
    """
    Process the "Add Client" form submission.
    
    Extracts form data, structures JSON fields, and creates a new client.
    Validates required fields and returns to form on error.
    
    Expected form fields:
        first_name, last_name, date_of_birth, ssn_last_four
        is_married, spouse_first_name, spouse_last_name, spouse_dob, spouse_ssn_last_four
        monthly_salary, agreed_expense_budget, private_reserve_target
        retirement_accounts[] (JSON array)
        non_retirement_accounts[] (JSON array)
        trust_info (JSON object)
        liabilities[] (JSON array)
    
    Returns:
        Redirect to client detail page on success
        Redirect to add form on validation error
    """
    try:
        # Extract and validate form data
        data = {
            "first_name": request.form.get("first_name"),
            "last_name": request.form.get("last_name"),
            "date_of_birth": request.form.get("date_of_birth"),
            "ssn_last_four": request.form.get("ssn_last_four"),
            "is_married": 1 if request.form.get("is_married") else 0,
            "spouse_first_name": request.form.get("spouse_first_name") or None,
            "spouse_last_name": request.form.get("spouse_last_name") or None,
            "spouse_dob": request.form.get("spouse_dob") or None,
            "spouse_ssn_last_four": request.form.get("spouse_ssn_last_four") or None,
            "monthly_salary": float(request.form.get("monthly_salary", 0)),
            "agreed_expense_budget": float(request.form.get("agreed_expense_budget", 0)),
            "private_reserve_target": float(request.form.get("private_reserve_target", 0)),
            "notes": request.form.get("notes", ""),
            # JSON fields (parsed from form)
            "retirement_accounts": parse_accounts_from_form(request, "retirement"),
            "non_retirement_accounts": parse_accounts_from_form(request, "non_retirement"),
            "trust_info": parse_trust_from_form(request),
            "liabilities": parse_liabilities_from_form(request)
        }
        
        # Create the client
        client_id = Client.create(data)
        flash(f"Client created successfully!", "success")
        return redirect(url_for("client.view_client", client_id=client_id))
        
    except ValueError as e:
        flash(f"Validation error: {e}", "error")
        return redirect(url_for("client.add_form"))
    except Exception as e:
        flash(f"Error creating client: {e}", "error")
        return redirect(url_for("client.add_form"))


@bp.route("/<int:client_id>")
def view_client(client_id):
    """
    View client details and report history.
    
    Displays:
        - Client profile (name, DOB, SSN, etc.)
        - Account structure summary
        - Each account with current/latest balance
        - Report history list (re-download button)
        - "Generate Report" button to start new quarterly report
    
    Args:
        client_id (int): The client's primary key
    
    Returns:
        Rendered client_detail.html
    """
    client = Client.get_by_id(client_id)
    if not client:
        abort(404, f"Client {client_id} not found")
    
    # Get report history for this client
    reports = Report.get_by_client(client_id)
    
    return render_template(
        "client_detail.html",
        client=client,
        reports=reports,
        report_count=len(reports)
    )


@bp.route("/<int:client_id>/edit")
def edit_form(client_id):
    """
    Display the "Edit Client" form.
    
    Pre-populates all fields with existing data.
    """
    client = Client.get_by_id(client_id)
    if not client:
        abort(404)
    
    return render_template("client_form.html", client=client, mode="edit")


@bp.route("/<int:client_id>/update", methods=["POST"])
def update_client(client_id):
    """
    Process the "Edit Client" form submission.
    
    Updates only the fields provided in the form.
    """
    try:
        data = {
            "first_name": request.form.get("first_name"),
            "last_name": request.form.get("last_name"),
            "date_of_birth": request.form.get("date_of_birth"),
            "ssn_last_four": request.form.get("ssn_last_four"),
            "is_married": 1 if request.form.get("is_married") else 0,
            "spouse_first_name": request.form.get("spouse_first_name") or None,
            "spouse_last_name": request.form.get("spouse_last_name") or None,
            "spouse_dob": request.form.get("spouse_dob") or None,
            "spouse_ssn_last_four": request.form.get("spouse_ssn_last_four") or None,
            "monthly_salary": float(request.form.get("monthly_salary", 0)),
            "agreed_expense_budget": float(request.form.get("agreed_expense_budget", 0)),
            "private_reserve_target": float(request.form.get("private_reserve_target", 0)),
            "notes": request.form.get("notes", ""),
            "retirement_accounts": parse_accounts_from_form(request, "retirement"),
            "non_retirement_accounts": parse_accounts_from_form(request, "non_retirement"),
            "trust_info": parse_trust_from_form(request),
            "liabilities": parse_liabilities_from_form(request)
        }
        
        Client.update(client_id, data)
        flash("Client updated successfully!", "success")
        return redirect(url_for("client.view_client", client_id=client_id))
        
    except ValueError as e:
        flash(f"Validation error: {e}", "error")
        return redirect(url_for("client.edit_form", client_id=client_id))
    except Exception as e:
        flash(f"Error updating client: {e}", "error")
        return redirect(url_for("client.edit_form", client_id=client_id))


@bp.route("/<int:client_id>/delete", methods=["POST"])
def delete_client(client_id):
    """
    Delete a client and all associated reports.
    
    Requires confirmation (handled client-side before POST).
    """
    try:
        Client.delete(client_id)
        flash("Client deleted successfully.", "success")
    except Exception as e:
        flash(f"Error deleting client: {e}", "error")
    
    return redirect(url_for("dashboard.index"))


# ============================================
# HELPER FUNCTIONS
# ============================================

def parse_accounts_from_form(request, account_type):
    """
    Parse retirement or non-retirement accounts from the form.
    
    Args:
        request: Flask request object
        account_type (str): 'retirement' or 'non_retirement'
    
    Returns:
        list: [{type, last_four}, ...]
    """
    accounts = []
    field_prefix = f"{account_type}_account_"
    
    # Get all form fields matching the pattern
    # e.g., retirement_account_1_type, retirement_account_1_last_four
    i = 0
    while True:
        account_type_field = f"{field_prefix}{i}_type"
        account_last_four_field = f"{field_prefix}{i}_last_four"
        
        if account_type_field not in request.form:
            break
        
        accounts.append({
            "type": request.form.get(account_type_field, ""),
            "last_four": request.form.get(account_last_four_field, ""),
            "owner": request.form.get(f"{field_prefix}{i}_owner", "client1")
        })
        i += 1
    
    return accounts


def parse_trust_from_form(request):
    """
    Parse trust information from the form.
    
    Returns:
        dict: {property_address, zillow_value}
    """
    return {
        "property_address": request.form.get("trust_property_address", ""),
        "zillow_value": float(request.form.get("trust_zillow_value", 0))
    }


def parse_liabilities_from_form(request):
    """
    Parse liability list from the form.
    
    Returns:
        list: [{type, balance, interest_rate, insurance_deductible}, ...]
    """
    liabilities = []
    i = 0
    
    while True:
        liability_type = request.form.get(f"liability_{i}_type")
        if liability_type is None:
            break
        
        liabilities.append({
            "type": liability_type,
            "balance": float(request.form.get(f"liability_{i}_balance", 0)),
            "interest_rate": float(request.form.get(f"liability_{i}_interest_rate", 0)),
            "insurance_deductible": float(request.form.get(f"liability_{i}_insurance_deductible", 0))
        })
        i += 1
    
    return liabilities
