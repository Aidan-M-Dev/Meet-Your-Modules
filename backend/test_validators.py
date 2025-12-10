"""
Tests for validators.py input validation and sanitization functions.

Covers edge cases and error paths for all validation functions.
"""

import pytest
from validators import (
    ValidationError,
    validate_review_rating,
    sanitize_review_text,
    validate_module_code,
    validate_search_query,
    validate_integer_id,
    validate_boolean,
    MAX_REVIEW_LENGTH,
    MIN_REVIEW_LENGTH,
    MAX_SEARCH_QUERY_LENGTH,
    MAX_MODULE_CODE_LENGTH
)


# ============================================================================
# Review Rating Validation Tests
# ============================================================================

def test_validate_review_rating_valid():
    """Test validate_review_rating with valid ratings."""
    assert validate_review_rating(1) == 1
    assert validate_review_rating(3) == 3
    assert validate_review_rating(5) == 5
    assert validate_review_rating("4") == 4  # String input


def test_validate_review_rating_invalid_type():
    """Test validate_review_rating with invalid types."""
    with pytest.raises(ValidationError, match="Rating must be a number"):
        validate_review_rating(None)

    with pytest.raises(ValidationError, match="Rating must be a number"):
        validate_review_rating("abc")


def test_validate_review_rating_out_of_range():
    """Test validate_review_rating with out-of-range values."""
    with pytest.raises(ValidationError, match="Rating must be between 1 and 5"):
        validate_review_rating(0)

    with pytest.raises(ValidationError, match="Rating must be between 1 and 5"):
        validate_review_rating(6)

    with pytest.raises(ValidationError, match="Rating must be between 1 and 5"):
        validate_review_rating(-1)


# ============================================================================
# Review Text Sanitization Tests
# ============================================================================

def test_sanitize_review_text_valid():
    """Test sanitize_review_text with valid text."""
    text = "This is a great module with excellent teaching!"
    result = sanitize_review_text(text)
    assert result == text


def test_sanitize_review_text_none_or_non_string():
    """Test sanitize_review_text with None or non-string input."""
    with pytest.raises(ValidationError, match="Review text is required"):
        sanitize_review_text(None)

    with pytest.raises(ValidationError, match="Review text is required"):
        sanitize_review_text(123)

    with pytest.raises(ValidationError, match="Review text is required"):
        sanitize_review_text([])


def test_sanitize_review_text_too_short():
    """Test sanitize_review_text with text below minimum length."""
    with pytest.raises(ValidationError, match=f"Review must be at least {MIN_REVIEW_LENGTH} characters"):
        sanitize_review_text("Too short")


def test_sanitize_review_text_too_long():
    """Test sanitize_review_text with text exceeding maximum length."""
    long_text = "x" * (MAX_REVIEW_LENGTH + 1)
    with pytest.raises(ValidationError, match=f"Review must not exceed {MAX_REVIEW_LENGTH} characters"):
        sanitize_review_text(long_text)


def test_sanitize_review_text_removes_html():
    """Test that HTML tags are removed from review text."""
    text_with_html = "This is a <b>great</b> module with <script>alert('xss')</script> excellent teaching!"
    result = sanitize_review_text(text_with_html)

    # Should remove all HTML tags
    assert "<b>" not in result
    assert "</b>" not in result
    assert "<script>" not in result
    assert "great" in result
    assert "excellent teaching" in result


def test_sanitize_review_text_strips_whitespace():
    """Test that whitespace is stripped from review text."""
    text = "   This is a great module   "
    result = sanitize_review_text(text)
    assert result == "This is a great module"


# ============================================================================
# Module Code Validation Tests
# ============================================================================

def test_validate_module_code_valid():
    """Test validate_module_code with valid codes."""
    assert validate_module_code("COMP1001") == "COMP1001"
    assert validate_module_code("comp1001") == "COMP1001"  # Converts to uppercase
    assert validate_module_code("  CS101  ") == "CS101"  # Strips whitespace


def test_validate_module_code_none_or_non_string():
    """Test validate_module_code with None or non-string input."""
    with pytest.raises(ValidationError, match="Module code is required"):
        validate_module_code(None)

    with pytest.raises(ValidationError, match="Module code is required"):
        validate_module_code(123)

    with pytest.raises(ValidationError, match="Module code is required"):
        validate_module_code("")


def test_validate_module_code_too_long():
    """Test validate_module_code with code exceeding maximum length."""
    long_code = "A" * (MAX_MODULE_CODE_LENGTH + 1)
    with pytest.raises(ValidationError, match=f"Module code too long"):
        validate_module_code(long_code)


def test_validate_module_code_invalid_format():
    """Test validate_module_code with invalid characters."""
    with pytest.raises(ValidationError, match="Module code must contain only letters and numbers"):
        validate_module_code("COMP-1001")

    with pytest.raises(ValidationError, match="Module code must contain only letters and numbers"):
        validate_module_code("COMP 1001")

    with pytest.raises(ValidationError, match="Module code must contain only letters and numbers"):
        validate_module_code("COMP@1001")


# ============================================================================
# Search Query Validation Tests
# ============================================================================

def test_validate_search_query_valid():
    """Test validate_search_query with valid queries."""
    assert validate_search_query("programming") == "programming"
    assert validate_search_query("computer science") == "computer science"


def test_validate_search_query_none_or_non_string():
    """Test validate_search_query with None or non-string input."""
    with pytest.raises(ValidationError, match="Search query is required"):
        validate_search_query(None)

    with pytest.raises(ValidationError, match="Search query is required"):
        validate_search_query(123)

    with pytest.raises(ValidationError, match="Search query is required"):
        validate_search_query("")


def test_validate_search_query_too_long():
    """Test validate_search_query with query exceeding maximum length."""
    long_query = "x" * (MAX_SEARCH_QUERY_LENGTH + 1)
    with pytest.raises(ValidationError, match=f"Search query too long"):
        validate_search_query(long_query)


def test_validate_search_query_wildcard():
    """Test validate_search_query with wildcard '*' character."""
    assert validate_search_query("*") == "*"


def test_validate_search_query_removes_html():
    """Test that HTML is removed from search queries."""
    query_with_html = "programming<script>alert('xss')</script>"
    result = validate_search_query(query_with_html)
    assert "<script>" not in result
    assert "programming" in result


def test_validate_search_query_normalizes_whitespace():
    """Test that excess whitespace is normalized."""
    assert validate_search_query("  multiple   spaces  ") == "multiple spaces"


# ============================================================================
# Integer ID Validation Tests
# ============================================================================

def test_validate_integer_id_valid():
    """Test validate_integer_id with valid IDs."""
    assert validate_integer_id(1) == 1
    assert validate_integer_id("42") == 42
    assert validate_integer_id(999, "Review ID") == 999


def test_validate_integer_id_invalid_type():
    """Test validate_integer_id with invalid types."""
    with pytest.raises(ValidationError, match="ID must be a number"):
        validate_integer_id("abc")

    with pytest.raises(ValidationError, match="Module ID must be a number"):
        validate_integer_id(None, "Module ID")


def test_validate_integer_id_negative_or_zero():
    """Test validate_integer_id with negative or zero values."""
    with pytest.raises(ValidationError, match="ID must be a positive number"):
        validate_integer_id(0)

    with pytest.raises(ValidationError, match="Review ID must be a positive number"):
        validate_integer_id(-1, "Review ID")

    with pytest.raises(ValidationError, match="ID must be a positive number"):
        validate_integer_id(-999)


# ============================================================================
# Boolean Validation Tests
# ============================================================================

def test_validate_boolean_valid_bool():
    """Test validate_boolean with actual boolean values."""
    assert validate_boolean(True) is True
    assert validate_boolean(False) is False


def test_validate_boolean_valid_strings():
    """Test validate_boolean with valid string representations."""
    assert validate_boolean("true") is True
    assert validate_boolean("True") is True
    assert validate_boolean("TRUE") is True
    assert validate_boolean("1") is True
    assert validate_boolean("yes") is True

    assert validate_boolean("false") is False
    assert validate_boolean("False") is False
    assert validate_boolean("FALSE") is False
    assert validate_boolean("0") is False
    assert validate_boolean("no") is False


def test_validate_boolean_invalid():
    """Test validate_boolean with invalid values."""
    with pytest.raises(ValidationError, match="value must be true or false"):
        validate_boolean("maybe")

    with pytest.raises(ValidationError, match="like must be true or false"):
        validate_boolean(123, "like")

    with pytest.raises(ValidationError, match="flag must be true or false"):
        validate_boolean(None, "flag")
