from flask import Flask, request, jsonify, send_from_directory, send_file
import os
from dotenv import load_dotenv
from pathlib import Path
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_compress import Compress
from db import (
    initialize_connection_pool,
    close_connection_pool,
    search_modules_by_code,
    search_modules_by_name,
    get_module_info_with_iterations,
    get_all_courses,
    like_or_dislike_review,
    report_review,
    submit_review,
    get_pending_reviews,
    get_rejected_reviews,
    accept_review,
    reject_review
)
from lib import sentiment_review
from logger import setup_logger
from config import get_config
from validators import (
    ValidationError,
    validate_review_rating,
    sanitize_review_text,
    validate_module_code,
    validate_search_query,
    validate_integer_id,
    validate_boolean
)
from errors import (
    register_error_handlers,
    handle_validation_error,
    handle_not_found,
    handle_internal_error,
    handle_database_error,
    handle_not_implemented,
    ErrorCode
)

# Load .env from repo root if present so frontend and backend can share the same env file.
# Fallback to default behaviour (load from CWD) if repo-root .env is not present.
repo_root = Path(__file__).resolve().parents[1]
env_path = repo_root / '.env'
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv()

# Get configuration based on FLASK_ENV
Config = get_config()

# Set up logger
logger = setup_logger(__name__)

# Create Flask app with configuration
app = Flask(__name__)
app.config.from_object(Config)

# Configure CORS with environment-specific origins
CORS(app, origins=Config.CORS_ORIGINS)

# Configure rate limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per hour", "50 per minute"],
    storage_uri="memory://",
)

# Enable gzip compression for all responses
compress = Compress()
compress.init_app(app)
app.config['COMPRESS_MIMETYPES'] = [
    'text/html',
    'text/css',
    'text/xml',
    'text/plain',
    'application/json',
    'application/javascript',
    'application/x-javascript',
    'image/svg+xml',
]
app.config['COMPRESS_LEVEL'] = 6  # Compression level (1-9, default 6)
app.config['COMPRESS_MIN_SIZE'] = 500  # Minimum response size to compress (bytes)

# Initialize database connection pool
initialize_connection_pool()

# Register global error handlers
register_error_handlers(app)

# Log application startup
env_name = os.getenv('FLASK_ENV', 'development')
logger.info(f"Starting Meet Your Modules backend server")
logger.info(f"Environment: {env_name}")
logger.info(f"Debug mode: {Config.DEBUG}")
logger.info(f"CORS enabled for: {', '.join(Config.CORS_ORIGINS)}")
logger.info(f"Rate limiting enabled: 200/hour, 50/minute per IP")


# Shutdown handler
import atexit
atexit.register(close_connection_pool)


@app.route("/api/health")  # Keep old route for backward compatibility
@app.route("/api/v1/health")
def health():
    """Basic health check endpoint."""
    return jsonify({"status": "ok", "version": "v1"}), 200


@app.route("/api/health/db")  # Keep old route for backward compatibility
@app.route("/api/v1/health/db")
def health_db():
    """Database health check endpoint."""
    try:
        from db import get_db_connection
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                result = cur.fetchone()
                if result and result[0] == 1:
                    return jsonify({"status": "ok", "database": "connected"}), 200
        return jsonify({"status": "error", "database": "query failed"}), 500
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}", exc_info=True)
        return jsonify({"status": "error", "database": "disconnected", "error": str(e)}), 500

@app.route("/api/v1/searchModulesByCode/<module_code>")
@limiter.limit("30 per minute")
def search_modules_by_code_route(module_code):
    """Search for modules by module code."""
    try:
        # Validate module code
        validated_code = validate_module_code(module_code)
        logger.debug(f"Searching for module by code: {validated_code}")

        modules = search_modules_by_code(validated_code)
        logger.info(f"Found {len(modules)} module(s) with code: {validated_code}")
        return jsonify({"modules": modules, "status": "success"}), 200
    except ValidationError:
        raise  # Let global handler catch it
    except Exception as e:
        return handle_internal_error(e, f"searching for module code '{module_code}'")

@app.route("/api/v1/searchModules")
@limiter.limit("30 per minute")
def search_modules_route():
    """Search for modules by name, code, or lecturer."""
    try:
        search_term = request.args.get('q', '')
        if not search_term:
            return jsonify({"modules": [], "status": "success"}), 200

        # Validate search query
        validated_query = validate_search_query(search_term)
        logger.debug(f"Searching modules with term: {validated_query}")

        modules = search_modules_by_name(validated_query)
        logger.info(f"Search for '{validated_query}' returned {len(modules)} module(s)")
        return jsonify({"modules": modules, "status": "success"}), 200
    except ValidationError:
        raise  # Let global handler catch it
    except Exception as e:
        return handle_internal_error(e, "searching modules")

@app.route("/api/v1/courses")
def get_courses_route():
    """Get all available courses."""
    try:
        courses = get_all_courses()
        return jsonify({"courses": courses, "status": "success"}), 200
    except Exception as e:
        return handle_database_error(e, "fetching courses")

@app.route("/api/v1/getModuleInfo/<module_id>")
@limiter.limit("60 per minute")
def get_module_info_route(module_id):
    """Get detailed information for a specific module including all iterations."""
    try:
        # Validate module ID
        validated_id = validate_integer_id(module_id, "Module ID")
        years_info = get_module_info_with_iterations(validated_id)

        if years_info is None:
            return handle_not_found("Module")

        return jsonify({"yearsInfo": years_info, "status": "success"}), 200
    except ValidationError:
        raise  # Let global handler catch it
    except Exception as e:
        return handle_internal_error(e, "fetching module info")

@app.route("/api/v1/likeReview/<review_id>/<like_or_dislike>")
@limiter.limit("10 per minute")
def like_review_route(review_id, like_or_dislike):
    """Like or dislike a review."""
    try:
        # Validate review ID
        validated_id = validate_integer_id(review_id, "Review ID")

        # Validate boolean
        like_bool = validate_boolean(like_or_dislike, "like_or_dislike")

        # Call the database function to like or dislike the review
        result = like_or_dislike_review(validated_id, like_bool)
        return jsonify({"result": result, "status": "success"}), 200
    except ValidationError:
        raise  # Let global handler catch it
    except Exception as e:
        return handle_database_error(e, "updating review likes")

@app.route("/api/v1/reportReview/<review_id>")
@limiter.limit("5 per hour")  # Strict limit to prevent abuse
def report_review_route(review_id):
    """Report a review as inappropriate."""
    try:
        # Validate review ID
        validated_id = validate_integer_id(review_id, "Review ID")

        # Call the database function to report the review
        result = report_review(validated_id)
        return jsonify({"result": result, "status": "success"}), 200
    except ValidationError:
        raise  # Let global handler catch it
    except Exception as e:
        return handle_database_error(e, "reporting review")
    
@app.route("/api/v1/submitReview/<module_iteration_id>", methods=["POST"])
@limiter.limit("5 per hour")  # Strict limit to prevent spam
def submit_review_route(module_iteration_id):
    """Submit a new review for a module iteration."""
    try:
        # Validate module iteration ID
        validated_iteration_id = validate_integer_id(module_iteration_id, "Module iteration ID")

        # Validate and sanitize rating
        rating = request.args.get("overall_rating")
        validated_rating = validate_review_rating(rating)

        # Validate and sanitize review text
        text = request.form.get("reviewText")
        sanitized_text = sanitize_review_text(text)

        logger.info(f"Submitting review for module_iteration_id={validated_iteration_id}, rating={validated_rating}")

        # AI sentiment analysis
        reasonable = sentiment_review(sanitized_text)
        logger.debug(f"AI sentiment analysis result: {'appropriate' if reasonable else 'flagged'}")

        # Submit review with sanitized data
        result = submit_review(validated_iteration_id, sanitized_text, validated_rating, reasonable)
        logger.info(f"Review submitted successfully for iteration {validated_iteration_id}, status={'published' if reasonable else 'pending moderation'}")
        return jsonify({"result": result, "status": "success"}), 200
    except ValidationError:
        raise  # Let global handler catch it
    except ValueError as e:
        # ValueError from database (e.g., module iteration not found)
        return handle_validation_error(str(e))
    except Exception as e:
        return handle_internal_error(e, "submitting review")

@app.route("/api/v1/user")
def get_user():
    """Get current user information (not yet implemented)."""
    # TODO: Implement authentication with a local auth system
    return handle_not_implemented()

@app.route("/api/v1/admin/pendingReviews")
def get_pending_reviews_route():
    """Get all reviews pending admin moderation."""
    try:
        reviews = get_pending_reviews()
        return jsonify({"reviews": reviews, "status": "success"}), 200
    except Exception as e:
        return handle_database_error(e, "fetching pending reviews")

@app.route("/api/v1/admin/rejectedReviews")
def get_rejected_reviews_route():
    """Get all rejected reviews."""
    try:
        reviews = get_rejected_reviews()
        return jsonify({"reviews": reviews, "status": "success"}), 200
    except Exception as e:
        return handle_database_error(e, "fetching rejected reviews")

@app.route("/api/v1/admin/acceptReview/<review_id>", methods=["POST"])
@limiter.limit("100 per hour")
def accept_review_route(review_id):
    """Admin endpoint to accept a pending or reported review."""
    try:
        # Validate review ID
        validated_id = validate_integer_id(review_id, "Review ID")

        logger.info(f"Admin accepting review {validated_id}")
        result = accept_review(validated_id)
        logger.info(f"Review {validated_id} accepted successfully")
        return jsonify({"result": result, "status": "success"}), 200
    except ValidationError:
        raise  # Let global handler catch it
    except Exception as e:
        return handle_database_error(e, f"accepting review {review_id}")

@app.route("/api/v1/admin/rejectReview/<review_id>", methods=["POST"])
@limiter.limit("100 per hour")
def reject_review_route(review_id):
    """Admin endpoint to reject a pending or reported review."""
    try:
        # Validate review ID
        validated_id = validate_integer_id(review_id, "Review ID")

        logger.info(f"Admin rejecting review {validated_id}")
        result = reject_review(validated_id)
        logger.info(f"Review {validated_id} rejected successfully")
        return jsonify({"result": result, "status": "success"}), 200
    except ValidationError:
        raise  # Let global handler catch it
    except Exception as e:
        return handle_database_error(e, f"rejecting review {review_id}")


# Static file serving for production
# In production, frontend build files are copied to /app/dist
STATIC_FOLDER = Path(__file__).parent / 'dist'

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    """
    Serve frontend static files in production mode.

    In development, frontend is served by Vite dev server on port 5173.
    In production, this serves the built static files from /app/dist.
    """
    # Only serve static files in production mode
    if not Config.DEBUG and STATIC_FOLDER.exists():
        # If path is empty or is a directory route (no file extension), serve index.html
        if path == '' or '.' not in path:
            return send_file(STATIC_FOLDER / 'index.html')

        # Serve static files (JS, CSS, images, etc.)
        static_file = STATIC_FOLDER / path
        if static_file.exists() and static_file.is_file():
            # Set cache headers for static assets
            response = send_file(static_file)

            # Cache static assets for 1 year (they have hashed names)
            if any(path.endswith(ext) for ext in ['.js', '.css', '.woff', '.woff2', '.ttf', '.eot']):
                response.headers['Cache-Control'] = 'public, max-age=31536000, immutable'
            # Cache images for 1 week
            elif any(path.endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.ico', '.svg']):
                response.headers['Cache-Control'] = 'public, max-age=604800'

            return response

        # File not found, serve index.html for SPA routing
        return send_file(STATIC_FOLDER / 'index.html')

    # Development mode or static folder doesn't exist
    return jsonify({
        "error": {
            "message": "Frontend not available. In development, use Vite dev server on port 5173.",
            "code": "FRONTEND_NOT_AVAILABLE"
        },
        "status": "error"
    }), 404


if __name__ == "__main__":
    port = Config.BACKEND_PORT
    logger.info(f"Starting Flask server on port {port}")
    logger.info(f"Database: {Config.DATABASE_URL[:30]}..." if Config.DATABASE_URL else "Database: Not configured")
    app.run(debug=Config.DEBUG, host="0.0.0.0", port=port)
