"""
SAGEN-Sync: Automated Wealth Orchestrator
===========================================

Entry point for the Flask application.
This file initializes the app and starts the development server.

For production (Railway), use: gunicorn -w 4 'app:create_app()'

Usage:
    python run.py          # Starts development server on http://localhost:5000
    python -m flask run    # Alternative Flask CLI method

Author: AI Developer
Version: 1.0
"""

from app import create_app

# Create the Flask application instance
app = create_app()

if __name__ == "__main__":
    # Development server configuration
    # debug=True enables auto-reload and detailed error pages
    # host='0.0.0.0' makes the server available on all network interfaces
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
