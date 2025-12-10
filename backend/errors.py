"""
Error handling utilities for Meet Your Modules API.

Provides standardized error responses with consistent format and error codes.
"""

from flask import jsonify
from logger import setup_logger

logger = setup_logger(__name__)


# Error codes for machine-readable error handling
class ErrorCode:
    """Standardized error codes for API responses."""

    # Client errors (4xx)
    VALIDATION_ERROR = "VALIDATION_ERROR"
    NOT_FOUND = "NOT_FOUND"
    BAD_REQUEST = "BAD_REQUEST"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    NOT_IMPLEMENTED = "NOT_IMPLEMENTED"

    # Server errors (5xx)
    INTERNAL_ERROR = "INTERNAL_ERROR"
    DATABASE_ERROR = "DATABASE_ERROR"
    EXTERNAL_SERVICE_ERROR = "EXTERNAL_SERVICE_ERROR"


def create_error_response(message: str, error_code: str, status_code: int):
    """
    Create a standardized error response.

    Args:
        message: Human-readable error message
        error_code: Machine-readable error code from ErrorCode class
        status_code: HTTP status code

    Returns:
        tuple: (JSON response, status_code)

    Example:
        return create_error_response(
            "Module not found",
            ErrorCode.NOT_FOUND,
            404
        )
    """
    response = {
        "error": {
            "message": message,
            "code": error_code
        },
        "status": "error"
    }
    return jsonify(response), status_code


def handle_validation_error(error_message: str):
    """
    Handle validation errors with standardized format.

    Args:
        error_message: Validation error message

    Returns:
        tuple: (JSON response, 400)
    """
    logger.warning(f"Validation error: {error_message}")
    return create_error_response(
        error_message,
        ErrorCode.VALIDATION_ERROR,
        400
    )


def handle_not_found(resource_name: str = "Resource"):
    """
    Handle not found errors with standardized format.

    Args:
        resource_name: Name of the resource that wasn't found

    Returns:
        tuple: (JSON response, 404)
    """
    message = f"{resource_name} not found"
    logger.info(f"Not found: {message}")
    return create_error_response(
        message,
        ErrorCode.NOT_FOUND,
        404
    )


def handle_internal_error(error: Exception, context: str = ""):
    """
    Handle internal server errors with standardized format.

    Args:
        error: The exception that occurred
        context: Additional context about where the error occurred

    Returns:
        tuple: (JSON response, 500)
    """
    error_message = f"Internal server error{': ' + context if context else ''}"
    logger.error(f"{error_message} - {str(error)}", exc_info=True)
    return create_error_response(
        "An internal server error occurred. Please try again later.",
        ErrorCode.INTERNAL_ERROR,
        500
    )


def handle_database_error(error: Exception, operation: str = ""):
    """
    Handle database errors with standardized format.

    Args:
        error: The database exception that occurred
        operation: Description of the database operation that failed

    Returns:
        tuple: (JSON response, 500)
    """
    error_message = f"Database error{': ' + operation if operation else ''}"
    logger.error(f"{error_message} - {str(error)}", exc_info=True)
    return create_error_response(
        "A database error occurred. Please try again later.",
        ErrorCode.DATABASE_ERROR,
        500
    )


def handle_not_implemented():
    """
    Handle not implemented errors (for planned features).

    Returns:
        tuple: (JSON response, 501)
    """
    logger.info("Not implemented endpoint accessed")
    return create_error_response(
        "This feature is not yet implemented",
        ErrorCode.NOT_IMPLEMENTED,
        501
    )


def register_error_handlers(app):
    """
    Register global error handlers for Flask app.

    Args:
        app: Flask application instance
    """
    from werkzeug.exceptions import HTTPException
    from validators import ValidationError

    @app.errorhandler(ValidationError)
    def handle_validation_exception(e):
        """Handle ValidationError exceptions globally."""
        return handle_validation_error(str(e))

    @app.errorhandler(404)
    def handle_404(e):
        """Handle 404 Not Found errors globally."""
        return handle_not_found()

    @app.errorhandler(429)
    def handle_rate_limit(e):
        """Handle rate limit exceeded errors."""
        logger.warning(f"Rate limit exceeded: {e.description}")
        return create_error_response(
            "Rate limit exceeded. Please try again later.",
            ErrorCode.RATE_LIMIT_EXCEEDED,
            429
        )

    @app.errorhandler(500)
    def handle_500(e):
        """Handle 500 Internal Server Error globally."""
        return handle_internal_error(e)

    @app.errorhandler(Exception)
    def handle_generic_exception(e):
        """Handle any unhandled exceptions."""
        # Don't catch HTTPExceptions (they have their own handlers)
        if isinstance(e, HTTPException):
            return e
        return handle_internal_error(e, "Unhandled exception")

    logger.info("Global error handlers registered")
