"""
Pytest configuration and shared fixtures for Meet Your Modules backend tests.

This file provides common fixtures used across all test files.
"""

import pytest
import os
from pathlib import Path
from unittest.mock import Mock, MagicMock
import psycopg2
from psycopg2.extras import RealDictCursor

# Set testing environment before importing app
os.environ['FLASK_ENV'] = 'testing'

# Add parent directory to path so we can import modules
import sys
sys.path.insert(0, str(Path(__file__).parent))

from app import app as flask_app
from config import TestingConfig


# ============================================================================
# Application Fixtures
# ============================================================================

@pytest.fixture
def app():
    """
    Create and configure a Flask app instance for testing.

    Uses TestingConfig which sets DEBUG=True and uses in-memory database.
    """
    flask_app.config.from_object(TestingConfig)

    # Set up application context
    with flask_app.app_context():
        yield flask_app


@pytest.fixture
def client(app):
    """
    Create a test client for the Flask app.

    Usage:
        def test_health(client):
            response = client.get('/api/health')
            assert response.status_code == 200
    """
    return app.test_client()


@pytest.fixture
def runner(app):
    """
    Create a test runner for CLI commands.
    """
    return app.test_cli_runner()


# ============================================================================
# Database Fixtures
# ============================================================================

@pytest.fixture(scope='session')
def test_database_url():
    """
    Provide test database URL.

    Uses a separate test database to avoid affecting production/development data.
    """
    return os.getenv('TEST_DATABASE_URL', 'postgresql://module_guide:module_guide_dev_password@localhost:5432/module_guide_test')


@pytest.fixture
def db_connection(test_database_url):
    """
    Create a database connection for testing.

    Automatically rolls back changes after each test.
    """
    conn = psycopg2.connect(test_database_url)
    yield conn
    conn.rollback()  # Rollback any changes made during test
    conn.close()


@pytest.fixture
def db_cursor(db_connection):
    """
    Create a database cursor for testing.

    Returns RealDictCursor for easy access to column names.
    """
    cursor = db_connection.cursor(cursor_factory=RealDictCursor)
    yield cursor
    cursor.close()


# ============================================================================
# Mock Fixtures
# ============================================================================

@pytest.fixture
def mock_google_api(monkeypatch):
    """
    Mock Google Gemini API calls for testing.

    Usage:
        def test_sentiment_review(mock_google_api):
            from lib import sentiment_review
            result = sentiment_review("This is a test review")
            assert result is True
    """
    mock_response = Mock()
    mock_response.text = "yes"  # Default to "yes" (appropriate review)

    mock_model = Mock()
    mock_model.generate_content.return_value = mock_response

    # Patch the google.generativeai.GenerativeModel
    import google.generativeai as genai
    monkeypatch.setattr(genai, 'GenerativeModel', lambda *args, **kwargs: mock_model)

    return mock_model


@pytest.fixture
def mock_db_connection(monkeypatch):
    """
    Mock database connection for unit tests that don't need real database.

    Usage:
        def test_search_modules(mock_db_connection):
            from db import search_modules_by_name
            result = search_modules_by_name("computing")
            # Test passes without hitting real database
    """
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_cursor.fetchall.return_value = []
    mock_cursor.fetchone.return_value = None

    import db
    monkeypatch.setattr(db, 'get_db_connection', lambda: mock_conn)

    return mock_cursor


# ============================================================================
# Test Data Fixtures
# ============================================================================

@pytest.fixture
def sample_module():
    """
    Provide sample module data for testing.
    """
    return {
        'id': 1,
        'code': 'COMP1001',
        'name': 'Introduction to Computer Science',
        'credits': 20,
        'department_id': 1,
        'department_code': 'COMP',
        'department_name': 'Computer Science'
    }


@pytest.fixture
def sample_review():
    """
    Provide sample review data for testing.
    """
    return {
        'id': 1,
        'module_iteration_id': 1,
        'rating': 5,
        'comment': 'Excellent module! Very well taught and interesting content.',
        'status': 'published',
        'likes': 10,
        'dislikes': 2,
        'report_count': 0,
        'report_tolerance': 3,
        'created_at': '2024-01-15'
    }


@pytest.fixture
def sample_lecturer():
    """
    Provide sample lecturer data for testing.
    """
    return {
        'id': 1,
        'name': 'Dr. John Smith'
    }


@pytest.fixture
def sample_course():
    """
    Provide sample course data for testing.
    """
    return {
        'id': 1,
        'code': 'G400',
        'name': 'Computer Science BSc'
    }


# ============================================================================
# Authentication Fixtures (for future use)
# ============================================================================

@pytest.fixture
def admin_user():
    """
    Provide sample admin user data for testing.

    TODO: Implement when admin authentication is added (MYM-001).
    """
    return {
        'id': 1,
        'username': 'admin',
        'role': 'senior'
    }


# ============================================================================
# Helper Functions
# ============================================================================

def create_test_module(db_cursor, module_data=None):
    """
    Helper function to create a test module in the database.

    Args:
        db_cursor: Database cursor
        module_data: Optional dict with module data

    Returns:
        dict: Created module data with ID
    """
    data = module_data or {}
    db_cursor.execute("""
        INSERT INTO modules (code, name, credits, department_id)
        VALUES (%(code)s, %(name)s, %(credits)s, %(department_id)s)
        RETURNING id, code, name, credits, department_id
    """, {
        'code': data.get('code', 'TEST001'),
        'name': data.get('name', 'Test Module'),
        'credits': data.get('credits', 20),
        'department_id': data.get('department_id', 1)
    })
    return db_cursor.fetchone()


def create_test_review(db_cursor, review_data=None):
    """
    Helper function to create a test review in the database.

    Args:
        db_cursor: Database cursor
        review_data: Optional dict with review data

    Returns:
        dict: Created review data with ID
    """
    data = review_data or {}
    db_cursor.execute("""
        INSERT INTO reviews (module_iteration_id, rating, comment, status)
        VALUES (%(iteration_id)s, %(rating)s, %(comment)s, %(status)s)
        RETURNING id, module_iteration_id, rating, comment, status
    """, {
        'iteration_id': data.get('module_iteration_id', 1),
        'rating': data.get('rating', 5),
        'comment': data.get('comment', 'Test review'),
        'status': data.get('status', 'published')
    })
    return db_cursor.fetchone()
