"""
Pytest configuration
"""
import pytest
import sys
import os

# Add backend directory to path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend'))
sys.path.insert(0, backend_path)

@pytest.fixture(scope='session')
def app():
    """Create application for testing"""
    try:
        from app import app as flask_app
        flask_app.config['TESTING'] = True
        return flask_app
    except ImportError:
        return None
