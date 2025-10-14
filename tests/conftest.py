"""
Pytest configuration
"""
import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.fixture(scope='session')
def app():
    """Create application for testing"""
    try:
        from backend.app import app as flask_app
        flask_app.config['TESTING'] = True
        return flask_app
    except ImportError:
        return None
