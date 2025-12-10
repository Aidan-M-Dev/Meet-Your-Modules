"""
Input validation and sanitization functions for API endpoints.

Provides validation for:
- Review text and ratings
- Module codes and IDs
- Search queries
- HTML sanitization
"""

import re
import bleach
from logger import setup_logger

logger = setup_logger(__name__)

# Configuration
MAX_REVIEW_LENGTH = 5000
MIN_REVIEW_LENGTH = 10
MAX_SEARCH_QUERY_LENGTH = 200
MAX_MODULE_CODE_LENGTH = 20


class ValidationError(ValueError):
    """Custom exception for validation errors."""
    pass


def validate_review_rating(rating):
    """
    Validate review rating is between 1-5.

    Args:
        rating: Rating value (can be string or int)

    Returns:
        int: Validated rating

    Raises:
        ValidationError: If rating is invalid
    """
    try:
        rating_int = int(rating)
    except (TypeError, ValueError):
        logger.warning(f"Invalid rating type: {type(rating)}")
        raise ValidationError("Rating must be a number")

    if not 1 <= rating_int <= 5:
        logger.warning(f"Rating out of range: {rating_int}")
        raise ValidationError("Rating must be between 1 and 5")

    return rating_int


def sanitize_review_text(text):
    """
    Sanitize review text to prevent XSS attacks.

    Removes all HTML tags and dangerous content while preserving
    basic formatting like newlines.

    Args:
        text (str): Raw review text

    Returns:
        str: Sanitized text

    Raises:
        ValidationError: If text is invalid or too long/short
    """
    if not text or not isinstance(text, str):
        raise ValidationError("Review text is required")

    # Strip whitespace
    text = text.strip()

    # Check length limits
    if len(text) < MIN_REVIEW_LENGTH:
        raise ValidationError(f"Review must be at least {MIN_REVIEW_LENGTH} characters")

    if len(text) > MAX_REVIEW_LENGTH:
        raise ValidationError(f"Review must not exceed {MAX_REVIEW_LENGTH} characters")

    # Remove all HTML tags (no tags allowed in reviews)
    sanitized = bleach.clean(text, tags=[], strip=True)

    # Log if HTML was found and removed
    if sanitized != text:
        logger.warning(f"HTML tags removed from review text (original length: {len(text)}, sanitized: {len(sanitized)})")

    return sanitized


def validate_module_code(module_code):
    """
    Validate module code format.

    Args:
        module_code (str): Module code to validate

    Returns:
        str: Validated module code (uppercase)

    Raises:
        ValidationError: If module code is invalid
    """
    if not module_code or not isinstance(module_code, str):
        raise ValidationError("Module code is required")

    # Remove whitespace and convert to uppercase
    code = module_code.strip().upper()

    # Check length
    if len(code) > MAX_MODULE_CODE_LENGTH:
        raise ValidationError(f"Module code too long (max {MAX_MODULE_CODE_LENGTH} characters)")

    # Validate format: letters and numbers only, no special characters
    if not re.match(r'^[A-Z0-9]+$', code):
        logger.warning(f"Invalid module code format: {module_code}")
        raise ValidationError("Module code must contain only letters and numbers")

    return code


def validate_search_query(query):
    """
    Validate and sanitize search query.

    Args:
        query (str): Search query

    Returns:
        str: Sanitized query

    Raises:
        ValidationError: If query is invalid
    """
    if not query or not isinstance(query, str):
        raise ValidationError("Search query is required")

    # Remove excess whitespace
    query = ' '.join(query.split())

    # Check length
    if len(query) > MAX_SEARCH_QUERY_LENGTH:
        raise ValidationError(f"Search query too long (max {MAX_SEARCH_QUERY_LENGTH} characters)")

    # Remove HTML to prevent XSS
    sanitized = bleach.clean(query, tags=[], strip=True)

    # Allow wildcard for "get all" queries
    if query == '*':
        return query

    return sanitized


def validate_integer_id(id_value, field_name="ID"):
    """
    Validate that a value is a valid positive integer ID.

    Args:
        id_value: Value to validate (can be string or int)
        field_name (str): Name of the field for error messages

    Returns:
        int: Validated ID

    Raises:
        ValidationError: If ID is invalid
    """
    try:
        id_int = int(id_value)
    except (TypeError, ValueError):
        logger.warning(f"Invalid {field_name} type: {type(id_value)}")
        raise ValidationError(f"{field_name} must be a number")

    if id_int < 1:
        logger.warning(f"Invalid {field_name} value: {id_int}")
        raise ValidationError(f"{field_name} must be a positive number")

    return id_int


def validate_boolean(value, field_name="value"):
    """
    Validate boolean value from string or bool.

    Args:
        value: Value to validate
        field_name (str): Name of the field for error messages

    Returns:
        bool: Validated boolean

    Raises:
        ValidationError: If value is not a valid boolean
    """
    if isinstance(value, bool):
        return value

    if isinstance(value, str):
        lower_value = value.lower()
        if lower_value in ('true', '1', 'yes'):
            return True
        if lower_value in ('false', '0', 'no'):
            return False

    raise ValidationError(f"{field_name} must be true or false")
