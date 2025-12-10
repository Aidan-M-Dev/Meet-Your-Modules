from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv
from pathlib import Path
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from db import search_modules_by_code, search_modules_by_name, get_module_info_with_iterations, get_all_courses, like_or_dislike_review, report_review, submit_review, get_pending_reviews, get_rejected_reviews, accept_review, reject_review
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

# Log application startup
env_name = os.getenv('FLASK_ENV', 'development')
logger.info(f"Starting Meet Your Modules backend server")
logger.info(f"Environment: {env_name}")
logger.info(f"Debug mode: {Config.DEBUG}")
logger.info(f"CORS enabled for: {', '.join(Config.CORS_ORIGINS)}")
logger.info(f"Rate limiting enabled: 200/hour, 50/minute per IP")


@app.route("/api/health")
def health():
    return jsonify({"status": "ok"}), 200

@app.route("/api/searchModulesByCode/<module_code>")
@limiter.limit("30 per minute")
def search_modules_by_code_route(module_code):
    try:
        # Validate module code
        validated_code = validate_module_code(module_code)
        logger.debug(f"Searching for module by code: {validated_code}")

        modules = search_modules_by_code(validated_code)
        logger.info(f"Found {len(modules)} module(s) with code: {validated_code}")
        return jsonify({"modules": modules}), 200
    except ValidationError as e:
        logger.warning(f"Validation error searching module by code '{module_code}': {str(e)}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Error searching module by code '{module_code}': {str(e)}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500

@app.route("/api/searchModules")
@limiter.limit("30 per minute")
def search_modules_route():
    try:
        search_term = request.args.get('q', '')
        if not search_term:
            return jsonify({"modules": []}), 200

        # Validate search query
        validated_query = validate_search_query(search_term)
        logger.debug(f"Searching modules with term: {validated_query}")

        modules = search_modules_by_name(validated_query)
        logger.info(f"Search for '{validated_query}' returned {len(modules)} module(s)")
        return jsonify({"modules": modules}), 200
    except ValidationError as e:
        logger.warning(f"Validation error searching modules: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Error searching modules: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500

@app.route("/api/courses")
def get_courses_route():
    try:
        courses = get_all_courses()
        return jsonify({"courses": courses}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/getModuleInfo/<module_id>")
@limiter.limit("60 per minute")
def get_module_info_route(module_id):
    try:
        # Validate module ID
        validated_id = validate_integer_id(module_id, "Module ID")
        years_info = get_module_info_with_iterations(validated_id)

        if years_info is None:
            return jsonify({"error": "Module not found"}), 404

        return jsonify({"yearsInfo": years_info}), 200
    except ValidationError as e:
        logger.warning(f"Validation error getting module info: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Error getting module info: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500

@app.route("/api/likeReview/<review_id>/<like_or_dislike>")
@limiter.limit("10 per minute")
def like_review_route(review_id, like_or_dislike):
    try:
        # Validate review ID
        validated_id = validate_integer_id(review_id, "Review ID")

        # Validate boolean
        like_bool = validate_boolean(like_or_dislike, "like_or_dislike")

        # Call the database function to like or dislike the review
        result = like_or_dislike_review(validated_id, like_bool)
        return jsonify({"result": result}), 200
    except ValidationError as e:
        logger.warning(f"Validation error liking review: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Error liking review: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500

@app.route("/api/reportReview/<review_id>")
@limiter.limit("5 per hour")  # Strict limit to prevent abuse
def report_review_route(review_id):
    try:
        # Validate review ID
        validated_id = validate_integer_id(review_id, "Review ID")

        # Call the database function to report the review
        result = report_review(validated_id)
        return jsonify({"result": result}), 200
    except ValidationError as e:
        logger.warning(f"Validation error reporting review: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Error reporting review: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500
    
@app.route("/api/submitReview/<module_iteration_id>", methods=["POST"])
@limiter.limit("5 per hour")  # Strict limit to prevent spam
def submit_review_route(module_iteration_id):
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
        return jsonify({"result": result}), 200
    except ValidationError as e:
        logger.warning(f"Validation error submitting review: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except ValueError as e:
        logger.warning(f"Validation error submitting review for iteration {module_iteration_id}: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Error submitting review for iteration {module_iteration_id}: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500

@app.route("/api/user")
def get_user():
    # TODO: Implement authentication with a local auth system
    return jsonify({"error": "Authentication not yet implemented"}), 501

@app.route("/api/admin/pendingReviews")
def get_pending_reviews_route():
    try:
        reviews = get_pending_reviews()
        return jsonify({"reviews": reviews}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/admin/rejectedReviews")
def get_rejected_reviews_route():
    try:
        reviews = get_rejected_reviews()
        return jsonify({"reviews": reviews}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/admin/acceptReview/<review_id>", methods=["POST"])
@limiter.limit("100 per hour")
def accept_review_route(review_id):
    try:
        # Validate review ID
        validated_id = validate_integer_id(review_id, "Review ID")

        logger.info(f"Admin accepting review {validated_id}")
        result = accept_review(validated_id)
        logger.info(f"Review {validated_id} accepted successfully")
        return jsonify({"result": result}), 200
    except ValidationError as e:
        logger.warning(f"Validation error accepting review: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Error accepting review {review_id}: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500

@app.route("/api/admin/rejectReview/<review_id>", methods=["POST"])
@limiter.limit("100 per hour")
def reject_review_route(review_id):
    try:
        # Validate review ID
        validated_id = validate_integer_id(review_id, "Review ID")

        logger.info(f"Admin rejecting review {validated_id}")
        result = reject_review(validated_id)
        logger.info(f"Review {validated_id} rejected successfully")
        return jsonify({"result": result}), 200
    except ValidationError as e:
        logger.warning(f"Validation error rejecting review: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Error rejecting review {review_id}: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    port = Config.BACKEND_PORT
    logger.info(f"Starting Flask server on port {port}")
    logger.info(f"Database: {Config.DATABASE_URL[:30]}..." if Config.DATABASE_URL else "Database: Not configured")
    app.run(debug=Config.DEBUG, host="0.0.0.0", port=port)
