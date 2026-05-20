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
from app.database import init_db, db
import os

def create_app(config_class=Config):
    """
    Application factory - creates and configures the Flask app.
    """
    
    # Create Flask app
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    app = Flask(
        __name__,
        template_folder=os.path.join(base_dir, "frontend-vite-dist"),
        static_folder=os.path.join(base_dir, "frontend-vite-dist", "assets"),
        static_url_path="/assets"
    )
    
    # Load configuration from Config class
    app.config.from_object(config_class)
    
    # Ensure instance folder exists (for SQLite local dev)
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass
    
    # Initialize the database (create tables if they don't exist)
    init_db(app)
    
    # Register all route blueprints
    from app.routes import api
    
    # Register the API blueprint
    app.register_blueprint(api.bp)
    
    @app.before_request
    def before_request():
        pass
    
    @app.after_request
    def after_request(response):
        response.headers.set("X-Frame-Options", "SAMEORIGIN")
        response.headers.set("X-Content-Type-Options", "nosniff")
        return response
    
    return app
