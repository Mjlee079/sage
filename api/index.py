"""
Vercel Serverless Function Entry Point
========================================

This file is the entry point for the Vercel Python serverless function.
It creates and exports the Flask application instance.

Vercel expects the WSGI app to be exported as 'app'.
"""

import sys
import os

# Add the parent directory to the path so we can import the app module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app

# Create the Flask app instance
app = create_app()
