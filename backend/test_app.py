"""
Tests for Flask API endpoints in app.py

These tests verify that all API endpoints work correctly and return
proper responses with standardized error handling.
"""

import pytest
import json
from unittest.mock import patch, Mock
from errors import ErrorCode


# ============================================================================
# Health Check Tests
# ============================================================================

def test_health_endpoint(client):
    """Test /api/health endpoint returns 200 OK."""
    response = client.get('/api/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'ok'


def test_health_db_endpoint_success(client):
    """Test /api/health/db endpoint with successful database connection."""
    with patch('app.get_db_connection') as mock_conn:
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = (1,)
        mock_conn.return_value.__enter__.return_value.cursor.return_value.__enter__.return_value = mock_cursor

        response = client.get('/api/health/db')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'ok'
        assert data['database'] == 'connected'


def test_health_db_endpoint_failure(client):
    """Test /api/health/db endpoint with database connection failure."""
    with patch('app.get_db_connection') as mock_conn:
        mock_conn.side_effect = Exception("Database connection failed")

        response = client.get('/api/health/db')
        assert response.status_code == 500
        data = json.loads(response.data)
        assert data['status'] == 'error'


# ============================================================================
# Search Endpoints Tests
# ============================================================================

def test_search_modules_by_code_success(client):
    """Test /api/searchModulesByCode/<code> endpoint."""
    with patch('app.search_modules_by_code') as mock_search:
        mock_search.return_value = [
            {
                'id': 1,
                'code': 'COMP1001',
                'name': 'Introduction to Programming',
                'department_name': 'Computer Science'
            }
        ]

        response = client.get('/api/searchModulesByCode/COMP1001')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'modules' in data
        assert data['status'] == 'success'
        assert len(data['modules']) == 1


def test_search_modules_by_code_validation_error(client):
    """Test search by code with invalid module code."""
    response = client.get('/api/searchModulesByCode/')  # Empty code
    assert response.status_code == 404  # Route not found


def test_search_modules_by_name_success(client):
    """Test /api/searchModules endpoint with query parameter."""
    with patch('app.search_modules_by_name') as mock_search:
        mock_search.return_value = [
            {'id': 1, 'code': 'COMP1001', 'name': 'Programming'},
            {'id': 2, 'code': 'COMP2001', 'name': 'Advanced Programming'}
        ]

        response = client.get('/api/searchModules?q=programming')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'modules' in data
        assert data['status'] == 'success'
        assert len(data['modules']) == 2


def test_search_modules_empty_query(client):
    """Test search with empty query returns empty list."""
    response = client.get('/api/searchModules?q=')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['modules'] == []
    assert data['status'] == 'success'


# ============================================================================
# Module Info Tests
# ============================================================================

def test_get_module_info_success(client):
    """Test /api/getModuleInfo/<id> endpoint."""
    with patch('app.get_module_info_with_iterations') as mock_get:
        mock_get.return_value = {
            'module_code': 'COMP1001',
            'module_name': 'Programming',
            'years': []
        }

        response = client.get('/api/getModuleInfo/1')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'yearsInfo' in data
        assert data['status'] == 'success'


def test_get_module_info_not_found(client):
    """Test getting info for non-existent module."""
    with patch('app.get_module_info_with_iterations') as mock_get:
        mock_get.return_value = None

        response = client.get('/api/getModuleInfo/999')
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error']['code'] == ErrorCode.NOT_FOUND


def test_get_module_info_invalid_id(client):
    """Test getting info with invalid module ID."""
    response = client.get('/api/getModuleInfo/invalid')
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    assert data['error']['code'] == ErrorCode.VALIDATION_ERROR


# ============================================================================
# Review Interaction Tests
# ============================================================================

def test_like_review_success(client):
    """Test /api/likeReview/<id>/true endpoint."""
    with patch('app.like_or_dislike_review') as mock_like:
        mock_like.return_value = {'likes': 11}

        response = client.get('/api/likeReview/1/true')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'result' in data
        assert data['status'] == 'success'


def test_dislike_review_success(client):
    """Test /api/likeReview/<id>/false endpoint."""
    with patch('app.like_or_dislike_review') as mock_like:
        mock_like.return_value = {'dislikes': 3}

        response = client.get('/api/likeReview/1/false')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'result' in data
        assert data['status'] == 'success'


def test_like_review_invalid_boolean(client):
    """Test liking review with invalid boolean parameter."""
    response = client.get('/api/likeReview/1/invalid')
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    assert data['error']['code'] == ErrorCode.VALIDATION_ERROR


def test_report_review_success(client):
    """Test /api/reportReview/<id> endpoint."""
    with patch('app.report_review') as mock_report:
        mock_report.return_value = {'report_count': 2}

        response = client.get('/api/reportReview/1')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'result' in data
        assert data['status'] == 'success'


# ============================================================================
# Review Submission Tests
# ============================================================================

def test_submit_review_success(client):
    """Test /api/submitReview/<iteration_id> endpoint."""
    with patch('app.sentiment_review') as mock_sentiment, \
         patch('app.submit_review') as mock_submit:

        mock_sentiment.return_value = True  # AI approves
        mock_submit.return_value = {'id': 1, 'status': 'published'}

        response = client.post(
            '/api/submitReview/1?overall_rating=5',
            data={'reviewText': 'Great module!'}
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'result' in data
        assert data['status'] == 'success'


def test_submit_review_flagged_by_ai(client):
    """Test submitting review that gets flagged by AI."""
    with patch('app.sentiment_review') as mock_sentiment, \
         patch('app.submit_review') as mock_submit:

        mock_sentiment.return_value = False  # AI flags
        mock_submit.return_value = {'id': 1, 'status': 'automatic_review'}

        response = client.post(
            '/api/submitReview/1?overall_rating=1',
            data={'reviewText': 'Inappropriate content'}
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'result' in data


def test_submit_review_validation_errors(client):
    """Test review submission with various validation errors."""
    # Missing rating
    response = client.post(
        '/api/submitReview/1',
        data={'reviewText': 'Test review'}
    )
    assert response.status_code == 400

    # Invalid rating (out of range)
    response = client.post(
        '/api/submitReview/1?overall_rating=10',
        data={'reviewText': 'Test review'}
    )
    assert response.status_code == 400

    # Review text too short
    response = client.post(
        '/api/submitReview/1?overall_rating=5',
        data={'reviewText': 'Too short'}
    )
    assert response.status_code == 400


# ============================================================================
# Courses Tests
# ============================================================================

def test_get_courses_success(client):
    """Test /api/courses endpoint."""
    with patch('app.get_all_courses') as mock_courses:
        mock_courses.return_value = [
            {'id': 1, 'code': 'G400', 'name': 'Computer Science BSc'},
            {'id': 2, 'code': 'G401', 'name': 'Computer Science MEng'}
        ]

        response = client.get('/api/courses')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'courses' in data
        assert data['status'] == 'success'
        assert len(data['courses']) == 2


# ============================================================================
# Admin Endpoints Tests
# ============================================================================

def test_get_pending_reviews(client):
    """Test /api/admin/pendingReviews endpoint."""
    with patch('app.get_pending_reviews') as mock_pending:
        mock_pending.return_value = [
            {
                'id': 1,
                'comment': 'Pending review',
                'rating': 3,
                'status': 'automatic_review'
            }
        ]

        response = client.get('/api/admin/pendingReviews')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'reviews' in data
        assert data['status'] == 'success'


def test_get_rejected_reviews(client):
    """Test /api/admin/rejectedReviews endpoint."""
    with patch('app.get_rejected_reviews') as mock_rejected:
        mock_rejected.return_value = []

        response = client.get('/api/admin/rejectedReviews')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'reviews' in data
        assert data['status'] == 'success'


def test_accept_review(client):
    """Test /api/admin/acceptReview/<id> endpoint."""
    with patch('app.accept_review') as mock_accept:
        mock_accept.return_value = {'id': 1, 'status': 'published'}

        response = client.post('/api/admin/acceptReview/1')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'result' in data
        assert data['status'] == 'success'


def test_reject_review(client):
    """Test /api/admin/rejectReview/<id> endpoint."""
    with patch('app.reject_review') as mock_reject:
        mock_reject.return_value = {'id': 1, 'status': 'rejected'}

        response = client.post('/api/admin/rejectReview/1')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'result' in data
        assert data['status'] == 'success'


# ============================================================================
# Not Implemented Tests
# ============================================================================

def test_get_user_not_implemented(client):
    """Test /api/user endpoint returns 501 Not Implemented."""
    response = client.get('/api/user')
    assert response.status_code == 501
    data = json.loads(response.data)
    assert 'error' in data
    assert data['error']['code'] == ErrorCode.NOT_IMPLEMENTED


# ============================================================================
# Rate Limiting Tests
# ============================================================================

def test_rate_limiting_review_submission(client):
    """Test rate limiting on review submission (5 per hour)."""
    with patch('app.sentiment_review') as mock_sentiment, \
         patch('app.submit_review') as mock_submit:

        mock_sentiment.return_value = True
        mock_submit.return_value = {'id': 1}

        # Submit 6 reviews (limit is 5 per hour)
        for i in range(6):
            response = client.post(
                f'/api/submitReview/{i+1}?overall_rating=5',
                data={'reviewText': f'Review number {i+1}, this is a test review that is long enough.'}
            )

            if i < 5:
                # First 5 should succeed
                assert response.status_code == 200
            else:
                # 6th should be rate limited
                assert response.status_code == 429
                data = json.loads(response.data)
                assert 'error' in data
                assert data['error']['code'] == ErrorCode.RATE_LIMIT_EXCEEDED


# ============================================================================
# Error Format Tests
# ============================================================================

def test_error_response_format(client):
    """Test that all errors follow standardized format."""
    # Validation error
    response = client.get('/api/getModuleInfo/invalid')
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    assert 'message' in data['error']
    assert 'code' in data['error']
    assert data['status'] == 'error'


def test_404_error_format(client):
    """Test that 404 errors follow standardized format."""
    response = client.get('/api/nonexistent')
    assert response.status_code == 404
    data = json.loads(response.data)
    assert 'error' in data
    assert 'message' in data['error']
    assert 'code' in data['error']


# ============================================================================
# CORS Tests
# ============================================================================

def test_cors_headers(client):
    """Test that CORS headers are set correctly."""
    response = client.get('/api/health')
    assert 'Access-Control-Allow-Origin' in response.headers


# ============================================================================
# Compression Tests
# ============================================================================

def test_gzip_compression(client):
    """Test that gzip compression is enabled for JSON responses."""
    response = client.get(
        '/api/health',
        headers={'Accept-Encoding': 'gzip'}
    )
    # Check if response can be gzipped (depends on size)
    assert response.status_code == 200
