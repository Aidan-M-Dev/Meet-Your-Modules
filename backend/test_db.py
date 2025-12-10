"""
Tests for database functions in db.py

These tests verify that all database operations work correctly.
Uses mock database connections to avoid dependency on actual database.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from psycopg2.extras import RealDictRow


# ============================================================================
# Connection Pool Tests
# ============================================================================

def test_initialize_connection_pool():
    """Test that connection pool initializes correctly."""
    from db import initialize_connection_pool
    import os

    # Reset pool
    import db
    db._connection_pool = None

    # Temporarily set environment to non-testing to test pool initialization
    old_env = os.environ.get('FLASK_ENV')
    os.environ['FLASK_ENV'] = 'development'

    try:
        # Initialize pool
        with patch('db.pool.SimpleConnectionPool') as mock_pool:
            initialize_connection_pool()
            assert mock_pool.called
    finally:
        # Restore environment
        if old_env:
            os.environ['FLASK_ENV'] = old_env
        else:
            os.environ.pop('FLASK_ENV', None)
        # Reset pool again
        db._connection_pool = None


def test_get_connection_pool():
    """Test that get_connection_pool returns the pool, auto-initializing if needed."""
    from db import get_connection_pool
    import os

    import db
    db._connection_pool = None

    # Temporarily set environment to non-testing
    old_env = os.environ.get('FLASK_ENV')
    os.environ['FLASK_ENV'] = 'development'

    try:
        # Should auto-initialize and return pool
        with patch('db.pool.SimpleConnectionPool') as mock_pool:
            mock_pool.return_value = MagicMock()
            pool = get_connection_pool()
            assert pool is not None
            assert mock_pool.called
    finally:
        # Restore environment
        if old_env:
            os.environ['FLASK_ENV'] = old_env
        else:
            os.environ.pop('FLASK_ENV', None)
        # Reset pool
        db._connection_pool = None


# ============================================================================
# Search Functions Tests
# ============================================================================

def test_search_modules_by_code(mock_db_connection):
    """Test searching modules by code."""
    from db import search_modules_by_code

    # Mock return data
    mock_db_connection.fetchall.return_value = [
        {
            'id': 1,
            'code': 'COMP1001',
            'name': 'Introduction to Programming',
            'department_name': 'Computer Science'
        }
    ]

    result = search_modules_by_code('COMP1001')

    # Verify query was called
    assert mock_db_connection.execute.called
    # Verify results were returned (note: mock returns empty list by default)
    assert isinstance(result, list)


def test_search_modules_by_name(mock_db_connection):
    """Test searching modules by name."""
    from db import search_modules_by_name

    # Mock return data
    mock_db_connection.fetchall.return_value = [
        {
            'id': 1,
            'code': 'COMP1001',
            'name': 'Introduction to Programming',
            'department_name': 'Computer Science'
        },
        {
            'id': 2,
            'code': 'COMP2001',
            'name': 'Advanced Programming',
            'department_name': 'Computer Science'
        }
    ]

    result = search_modules_by_name('programming')

    # Verify query was called with ILIKE pattern
    assert mock_db_connection.execute.called
    call_args = mock_db_connection.execute.call_args
    assert '%programming%' in str(call_args).lower() or 'programming' in str(call_args)


def test_search_modules_empty_query(mock_db_connection):
    """Test searching modules with empty query returns empty list."""
    from db import search_modules_by_name

    result = search_modules_by_name('')

    # Should return empty list without querying database
    assert result == []
    assert not mock_db_connection.execute.called


# ============================================================================
# Module Info Tests
# ============================================================================

def test_get_module_info_with_iterations(mock_db_connection):
    """Test getting module information with all iterations."""
    from db import get_module_info_with_iterations

    # Mock module data
    mock_db_connection.fetchone.side_effect = [
        # First call: module basic info
        {
            'id': 1,
            'code': 'COMP1001',
            'name': 'Introduction to Programming',
            'credits': 20,
            'department_name': 'Computer Science'
        },
        # Subsequent calls: iteration details
        {'id': 1, 'academic_year': '2024/2025'},
    ]

    # Mock iterations list
    mock_db_connection.fetchall.side_effect = [
        # Iterations
        [{'id': 1, 'academic_year': '2024/2025'}],
        # Lecturers for iteration
        [{'id': 1, 'name': 'Dr. Smith'}],
        # Courses for iteration
        [{'id': 1, 'code': 'G400', 'name': 'Computer Science BSc'}],
        # Reviews for iteration
        [
            {
                'id': 1,
                'rating': 5,
                'comment': 'Great module',
                'status': 'published',
                'likes': 10,
                'dislikes': 1,
                'academic_year': '2024/2025'
            }
        ]
    ]

    result = get_module_info_with_iterations(1)

    # Verify structure
    assert 'module_code' in result
    assert 'years' in result
    assert isinstance(result['years'], list)


def test_get_module_info_not_found(mock_db_connection):
    """Test getting info for non-existent module."""
    from db import get_module_info_with_iterations

    # Mock no module found
    mock_db_connection.fetchone.return_value = None

    result = get_module_info_with_iterations(999)

    assert result is None


# ============================================================================
# Review Functions Tests
# ============================================================================

def test_submit_review_appropriate(mock_db_connection):
    """Test submitting an appropriate review (AI approved)."""
    from db import submit_review

    mock_db_connection.fetchone.return_value = {'id': 1}

    result = submit_review(
        module_iteration_id=1,
        text="Great module, very informative!",
        rating=5,
        reasonable=True  # AI approved
    )

    # Verify query was called
    assert mock_db_connection.execute.called

    # Verify status is 'published' for appropriate reviews
    call_args = str(mock_db_connection.execute.call_args)
    assert 'published' in call_args


def test_submit_review_inappropriate(mock_db_connection):
    """Test submitting an inappropriate review (AI flagged)."""
    from db import submit_review

    mock_db_connection.fetchone.return_value = {'id': 1}

    result = submit_review(
        module_iteration_id=1,
        text="Inappropriate content",
        rating=1,
        reasonable=False  # AI flagged
    )

    # Verify query was called
    assert mock_db_connection.execute.called

    # Verify status is 'automatic_review' for flagged reviews
    call_args = str(mock_db_connection.execute.call_args)
    assert 'automatic_review' in call_args


def test_submit_review_invalid_iteration(mock_db_connection):
    """Test submitting review for non-existent module iteration."""
    from db import submit_review

    # Mock iteration check failure
    mock_db_connection.fetchone.return_value = None

    with pytest.raises(ValueError, match="Module iteration .* not found"):
        submit_review(
            module_iteration_id=999,
            text="Test review",
            rating=5,
            reasonable=True
        )


def test_like_review(mock_db_connection):
    """Test liking a review."""
    from db import like_or_dislike_review

    mock_db_connection.fetchone.return_value = {'like_dislike': 11}

    result = like_or_dislike_review(review_id=1, like_or_dislike=True)

    # Verify UPDATE query was called
    assert mock_db_connection.execute.called
    call_args = str(mock_db_connection.execute.call_args)
    assert 'like_dislike' in call_args.lower()


def test_dislike_review(mock_db_connection):
    """Test disliking a review."""
    from db import like_or_dislike_review

    mock_db_connection.fetchone.return_value = {'like_dislike': 3}

    result = like_or_dislike_review(review_id=1, like_or_dislike=False)

    # Verify UPDATE query was called
    assert mock_db_connection.execute.called
    call_args = str(mock_db_connection.execute.call_args)
    assert 'like_dislike' in call_args.lower()


def test_report_review(mock_db_connection):
    """Test reporting a review."""
    from db import report_review

    mock_db_connection.fetchone.return_value = {'report_count': 2, 'report_tolerance': 3}

    result = report_review(review_id=1)

    # Verify UPDATE query was called
    assert mock_db_connection.execute.called
    call_args = str(mock_db_connection.execute.call_args)
    assert 'report_count' in call_args.lower()


# ============================================================================
# Admin Functions Tests
# ============================================================================

def test_get_pending_reviews(mock_db_connection):
    """Test getting pending reviews for moderation."""
    from db import get_pending_reviews

    mock_db_connection.fetchall.return_value = [
        {
            'id': 1,
            'comment': 'Test review',
            'rating': 3,
            'module_code': 'COMP1001',
            'status': 'automatic_review'
        }
    ]

    result = get_pending_reviews()

    # Verify query was called
    assert mock_db_connection.execute.called

    # Verify results
    assert isinstance(result, list)


def test_get_rejected_reviews(mock_db_connection):
    """Test getting rejected reviews."""
    from db import get_rejected_reviews

    mock_db_connection.fetchall.return_value = [
        {
            'id': 1,
            'comment': 'Rejected review',
            'rating': 1,
            'module_code': 'COMP1001',
            'status': 'rejected'
        }
    ]

    result = get_rejected_reviews()

    # Verify query was called
    assert mock_db_connection.execute.called


def test_accept_review(mock_db_connection):
    """Test accepting a pending review."""
    from db import accept_review

    mock_db_connection.fetchone.return_value = {'id': 1, 'status': 'published'}

    result = accept_review(review_id=1)

    # Verify UPDATE query was called
    assert mock_db_connection.execute.called
    call_args = str(mock_db_connection.execute.call_args)
    assert 'published' in call_args
    assert 'report_tolerance' in call_args.lower()  # Should increase tolerance


def test_reject_review(mock_db_connection):
    """Test rejecting a pending review."""
    from db import reject_review

    mock_db_connection.fetchone.return_value = {'id': 1, 'status': 'rejected'}

    result = reject_review(review_id=1)

    # Verify UPDATE query was called
    assert mock_db_connection.execute.called
    call_args = str(mock_db_connection.execute.call_args)
    assert 'rejected' in call_args


# ============================================================================
# Courses Tests
# ============================================================================

def test_get_all_courses(mock_db_connection):
    """Test getting all available courses."""
    from db import get_all_courses

    mock_db_connection.fetchall.return_value = [
        {'id': 1, 'code': 'G400', 'name': 'Computer Science BSc'},
        {'id': 2, 'code': 'G401', 'name': 'Computer Science MEng'}
    ]

    result = get_all_courses()

    # Verify query was called
    assert mock_db_connection.execute.called

    # Verify results
    assert isinstance(result, list)


# ============================================================================
# Error Handling Tests
# ============================================================================

def test_database_error_handling(mock_db_connection):
    """Test that database errors are properly handled."""
    from db import search_modules_by_code
    import psycopg2

    # Mock database error
    mock_db_connection.execute.side_effect = psycopg2.Error("Database error")

    with pytest.raises(psycopg2.Error):
        search_modules_by_code('COMP1001')


def test_connection_context_manager():
    """Test that database connection context manager works correctly."""
    from db import get_db_connection

    with patch('db.get_connection_pool') as mock_pool:
        mock_conn = MagicMock()
        mock_pool.return_value.getconn.return_value = mock_conn

        # Test successful connection
        with get_db_connection() as conn:
            assert conn == mock_conn

        # Verify connection was returned to pool
        assert mock_pool.return_value.putconn.called


def test_connection_rollback_on_error():
    """Test that database connection rolls back on error."""
    from db import get_db_connection
    import psycopg2

    with patch('db.get_connection_pool') as mock_pool:
        mock_conn = MagicMock()
        mock_pool.return_value.getconn.return_value = mock_conn

        # Simulate error inside context
        try:
            with get_db_connection() as conn:
                raise psycopg2.Error("Test error")
        except psycopg2.Error:
            pass

        # Verify rollback was called
        assert mock_conn.rollback.called
