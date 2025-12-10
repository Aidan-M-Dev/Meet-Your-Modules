"""
Tests for lib.py utility functions.

These tests cover sentiment analysis, admin notifications, and other helper functions.
"""

import pytest
from unittest.mock import patch, Mock, mock_open
import os


# ============================================================================
# Sentiment Analysis Tests
# ============================================================================

def test_sentiment_review_approved(mock_google_api):
    """Test sentiment_review with appropriate content (AI returns 'Yes')."""
    from lib import sentiment_review

    # Mock API to return "Yes"
    mock_google_api.generate_content.return_value.text = "Yes"

    result = sentiment_review("This is a great module with excellent teaching!")

    assert result is True
    assert mock_google_api.generate_content.called


def test_sentiment_review_flagged(mock_google_api):
    """Test sentiment_review with inappropriate content (AI returns 'No')."""
    from lib import sentiment_review

    # Mock API to return "No"
    mock_google_api.generate_content.return_value.text = "No"

    result = sentiment_review("This contains inappropriate content")

    assert result is False
    assert mock_google_api.generate_content.called


def test_sentiment_review_retry_then_success(mock_google_api):
    """Test sentiment_review retries on non-binary response, then succeeds."""
    from lib import sentiment_review

    # First call returns invalid, second returns "Yes"
    mock_google_api.generate_content.return_value.text = Mock(side_effect=["Maybe", "Yes"])

    # Need to set up side_effect properly
    responses = [Mock(text="Maybe"), Mock(text="Yes")]
    mock_google_api.generate_content.side_effect = responses

    result = sentiment_review("Test review")

    assert result is True
    assert mock_google_api.generate_content.call_count == 2


def test_sentiment_review_max_retries_exceeded(mock_google_api):
    """Test sentiment_review raises exception after 3 failed attempts."""
    from lib import sentiment_review

    # All attempts return non-binary response
    mock_google_api.generate_content.return_value.text = "I don't know"

    with pytest.raises(Exception, match="Gen AI not raising binary answers"):
        sentiment_review("Test review")

    # Should have tried 3 times
    assert mock_google_api.generate_content.call_count == 3


def test_query_calls_gemini_api(mock_google_api):
    """Test that query function calls Gemini API correctly."""
    from lib import query

    mock_google_api.generate_content.return_value.text = "Response text"

    result = query("Test prompt")

    assert result == "Response text"
    assert mock_google_api.generate_content.called
    call_args = mock_google_api.generate_content.call_args[0]
    assert "Test prompt" in call_args


# ============================================================================
# Admin Notification Tests
# ============================================================================

def test_notify_admins_of_reported_review():
    """Test notify_admins_of_reported_review logs warning."""
    from lib import notify_admins_of_reported_review

    # This is a skeleton function that just logs
    # Should not raise any errors
    notify_admins_of_reported_review(123)

    # Function should complete without error
    # (actual implementation would send emails/notifications)


# ============================================================================
# Module Initialization Tests
# ============================================================================

def test_sentiment_prompt_file_loaded():
    """Test that sentiment analysis prompt file is loaded."""
    from lib import master_prompt

    # Prompt should be loaded and not empty
    assert master_prompt is not None
    assert len(master_prompt) > 0
    assert isinstance(master_prompt, str)


def test_model_id_configured():
    """Test that model ID is properly configured."""
    from lib import MODEL_ID

    assert MODEL_ID == "gemini-2.5-flash-lite"
