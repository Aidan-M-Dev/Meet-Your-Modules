from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv
from pathlib import Path
from flask_cors import CORS
from db import search_modules_by_code, search_modules_by_name, get_module_info_with_iterations, get_all_courses, like_or_dislike_review, report_review, submit_review, get_pending_reviews, get_rejected_reviews, accept_review, reject_review
from lib import sentiment_review
from logger import setup_logger
from config import get_config

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

# Log application startup
env_name = os.getenv('FLASK_ENV', 'development')
logger.info(f"Starting Meet Your Modules backend server")
logger.info(f"Environment: {env_name}")
logger.info(f"Debug mode: {Config.DEBUG}")
logger.info(f"CORS enabled for: {', '.join(Config.CORS_ORIGINS)}")


@app.route("/api/health")
def health():
    return jsonify({"status": "ok"}), 200

@app.route("/api/searchModulesByCode/<module_code>")
def search_modules_by_code_route(module_code):
    try:
        logger.debug(f"Searching for module by code: {module_code}")
        modules = search_modules_by_code(module_code)
        logger.info(f"Found {len(modules)} module(s) with code: {module_code}")
        return jsonify({"modules": modules}), 200
    except Exception as e:
        logger.error(f"Error searching module by code '{module_code}': {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 400

@app.route("/api/searchModules")
def search_modules_route():
    try:
        search_term = request.args.get('q', '')
        if not search_term:
            return jsonify({"modules": []}), 200

        logger.debug(f"Searching modules with term: {search_term}")
        modules = search_modules_by_name(search_term)
        logger.info(f"Search for '{search_term}' returned {len(modules)} module(s)")
        return jsonify({"modules": modules}), 200
    except Exception as e:
        logger.error(f"Error searching modules with term '{search_term}': {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 400

@app.route("/api/courses")
def get_courses_route():
    try:
        courses = get_all_courses()
        return jsonify({"courses": courses}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/getModuleInfo/<module_id>")
def get_module_info_route(module_id):
    try:
        years_info = get_module_info_with_iterations(module_id)

        if years_info is None:
            return jsonify({"error": "Module not found"}), 404

        return jsonify({"yearsInfo": years_info}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/likeReview/<review_id>/<like_or_dislike>")
def like_review_route(review_id, like_or_dislike):
    try:
        # Convert string to boolean
        like_bool = like_or_dislike.lower() == 'true'
        # Call the database function to like or dislike the review
        result = like_or_dislike_review(review_id, like_bool)
        return jsonify({"result": result}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/reportReview/<review_id>")
def report_review_route(review_id):
    try:
        # Call the database function to report the review
        result = report_review(review_id)
        return jsonify({"result": result}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
@app.route("/api/submitReview/<module_iteration_id>", methods=["POST"])
def submit_review_route(module_iteration_id):
    try:
        rating = request.args.get("overall_rating")
        text = request.form.get("reviewText")
        logger.info(f"Submitting review for module_iteration_id={module_iteration_id}, rating={rating}")

        reasonable = sentiment_review(text)
        logger.debug(f"AI sentiment analysis result: {'appropriate' if reasonable else 'flagged'}")

        result = submit_review(module_iteration_id, text, rating, reasonable)
        logger.info(f"Review submitted successfully for iteration {module_iteration_id}, status={'published' if reasonable else 'pending moderation'}")
        return jsonify({"result": result}), 200
    except ValueError as e:
        logger.warning(f"Validation error submitting review for iteration {module_iteration_id}: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Error submitting review for iteration {module_iteration_id}: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 400

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
def accept_review_route(review_id):
    try:
        logger.info(f"Admin accepting review {review_id}")
        result = accept_review(review_id)
        logger.info(f"Review {review_id} accepted successfully")
        return jsonify({"result": result}), 200
    except Exception as e:
        logger.error(f"Error accepting review {review_id}: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 400

@app.route("/api/admin/rejectReview/<review_id>", methods=["POST"])
def reject_review_route(review_id):
    try:
        logger.info(f"Admin rejecting review {review_id}")
        result = reject_review(review_id)
        logger.info(f"Review {review_id} rejected successfully")
        return jsonify({"result": result}), 200
    except Exception as e:
        logger.error(f"Error rejecting review {review_id}: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    port = Config.BACKEND_PORT
    logger.info(f"Starting Flask server on port {port}")
    logger.info(f"Database: {Config.DATABASE_URL[:30]}..." if Config.DATABASE_URL else "Database: Not configured")
    app.run(debug=Config.DEBUG, host="0.0.0.0", port=port)
