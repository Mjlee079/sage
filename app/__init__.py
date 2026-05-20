"""
SAGEN-Sync: Automated Wealth Orchestrator
Flask Application Factory
==========================

This module provides the create_app() factory function that:
1. Initializes the Flask application
2. Loads configuration (database path, secret key, etc.)
3. Registers all route blueprints
4. Initializes the database

Pattern: Application Factory (recommended for testing and modularity)
"""

from flask import Flask
from app.config import Config
from app.database import init_db
import os

def create_app(config_class=Config):
    """
    Application factory - creates and configures the Flask app.
    
    This pattern allows creating multiple app instances with different
    configurations (e.g., for testing vs production).
    
    Args:
        config_class: Configuration class to use (default: Config)
    
    Returns:
        Flask: Configured Flask application instance
    """
    
    # Create Flask app with explicit template and static folders
    # Pointing to the frontend folder for clean separation of concerns
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    app = Flask(
        __name__,
        template_folder=os.path.join(base_dir, "frontend", "templates"),
        static_folder=os.path.join(base_dir, "frontend", "static"),
        static_url_path="/static"
    )
    
    # Load configuration from Config class
    app.config.from_object(config_class)
    
    # Ensure instance folder exists (for database storage)
    # The instance folder stores data that shouldn't be committed to git
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass
    
    # Initialize the database (create tables if they don't exist)
    init_db(app)
    
    # Register all route blueprints
    # Blueprints organize routes into modular, reusable components
    from app.routes import dashboard, client, report, pdf, history, canva
    
    # Each blueprint handles a specific feature area
    app.register_blueprint(dashboard.bp)      # Home page, client list
    app.register_blueprint(client.bp)       # Client CRUD operations
    app.register_blueprint(report.bp)       # Report generation, data entry
    app.register_blueprint(pdf.bp)          # PDF download generation
    app.register_blueprint(history.bp)      # Report history and re-download
    app.register_blueprint(canva.bp)        # Canva export (V2 stub)
    
    # Register a before_request to ensure DB connection per request
    @app.before_request
    def before_request():
        """
        Runs before each request to ensure database is available.
        This is a hook for future connection pooling or auth checks.
        """
        pass
    
    @app.after_request
    def after_request(response):
        """
        Runs after each request. Adds security headers.
        These headers help protect against common web attacks.
        """
        # Prevent clickjacking attacks
        response.headers.set("X-Frame-Options", "SAMEORIGIN")
        # Restrict content types
        response.headers.set("X-Content-Type-Options", "nosniff")
        return response
    
    return app
