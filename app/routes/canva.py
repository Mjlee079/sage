"""
SAGEN-Sync: Canva Export Routes
================================

**V2 Feature Stub**
This module provides the Canva export functionality.
In V1, it displays a "Coming in V2" message.
In V2, it will integrate with the Canva API to send reports data for editing.

URL Patterns:
    /canva/<report_id>/export  → Initiate Canva export

Planned V2 Integration:
    1. User clicks "Export to Canva"
    2. System authenticates with Canva API (using CANVA_API_KEY)
    3. Report data is formatted as a Canva-designable template
    4. Canva returns an edit URL
    5. User is redirected to Canva for final adjustments

Templates: none (returns JSON or redirect)
"""

from flask import Blueprint, jsonify, current_app, redirect

bp = Blueprint("canva", __name__, url_prefix="/canva")


@bp.route("/<int:report_id>/export")
def export_to_canva(report_id):
    """
    Export a finalized report to Canva for editing.
    
    **V1 Behavior:**
    Returns a JSON response indicating the feature is coming in V2.
    
    **V2 Behavior:**
    1. Authenticate with Canva API
    2. Upload report data as a Canva template
    3. Return a Canva edit URL for the user
    
    Args:
        report_id (int): The finalized report to export
    
    Returns:
        JSON: {status, message, url?}
    """
    # Check if Canva API key is configured
    api_key = current_app.config.get("CANVA_API_KEY")
    
    if not api_key:
        # V1: Feature not yet available
        return jsonify({
            "status": "not_implemented",
            "message": "Canva export will be available in V2. "
                      "For now, please download the PDF directly. "
                      "You can drag and drop the PDF into Canva for manual editing.",
            "version": "1.0"
        }), 501  # 501 = Not Implemented
    
    # V2: Implement actual Canva API integration here
    # This would call the Canva API to create a new design from template data
    # For now, it's a placeholder
    
    return jsonify({
        "status": "not_implemented",
        "message": "Canva API integration is planned for V2",
        "version": "1.0"
    }), 501
