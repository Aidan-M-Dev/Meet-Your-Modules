from flask import Flask, request, jsonify
import os
import tempfile
from dotenv import load_dotenv
from pathlib import Path
from flask_cors import CORS
from db import search_modules_by_code, search_modules_by_name, get_module_info_with_iterations, get_all_courses, like_or_dislike_review, report_review, submit_review, get_pending_reviews, get_rejected_reviews, accept_review, reject_review
from lib import sentiment_review, programme_specification_pdf_parser

# Load .env from repo root if present so frontend and backend can share the same env file.
# Fallback to default behaviour (load from CWD) if repo-root .env is not present.
repo_root = Path(__file__).resolve().parents[1]
env_path = repo_root / '.env'
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv()

app = Flask(__name__)
CORS(app, origins=f"http://{os.getenv('FRONTEND_ADDRESS')}:{os.getenv('FRONTEND_PORT')}")


@app.route("/api/health")
def health():
    return jsonify({"status": "ok"}), 200

@app.route("/api/searchModulesByCode/<module_code>")
def search_modules_by_code_route(module_code):
    try:
        modules = search_modules_by_code(module_code)
        return jsonify({"modules": modules}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/searchModules")
def search_modules_route():
    try:
        search_term = request.args.get('q', '')
        if not search_term:
            return jsonify({"modules": []}), 200

        modules = search_modules_by_name(search_term)
        return jsonify({"modules": modules}), 200
    except Exception as e:
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
        module_info = get_module_info_with_iterations(module_id)

        if module_info is None:
            return jsonify({"error": "Module not found"}), 404

        return jsonify(module_info), 200
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
        reasonable = sentiment_review(text)
        result = submit_review(module_iteration_id, text, rating, reasonable) 
        return jsonify({"result": result}), 200
    except Exception as e:
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
        result = accept_review(review_id)
        return jsonify({"result": result}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/admin/rejectReview/<review_id>", methods=["POST"])
def reject_review_route(review_id):
    try:
        result = reject_review(review_id)
        return jsonify({"result": result}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/admin/uploadProgrammeSpec", methods=["POST"])
def upload_programme_spec_route():
    try:
        # Check if file was uploaded
        if 'pdf' not in request.files:
            return jsonify({"error": "No PDF file uploaded"}), 400

        pdf_file = request.files['pdf']

        if pdf_file.filename == '':
            return jsonify({"error": "No file selected"}), 400

        if not pdf_file.filename.endswith('.pdf'):
            return jsonify({"error": "File must be a PDF"}), 400

        # Save file to temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            pdf_file.save(tmp_file.name)
            tmp_path = tmp_file.name

        try:
            # Parse the PDF
            pdf_data = programme_specification_pdf_parser(tmp_path)

            # TODO: Process and store the data in database
            # result = process_programme_spec_data(pdf_data)

            # For now, just return the parsed data
            return jsonify(pdf_data), 200

        finally:
            # Clean up temp file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    except Exception as e:
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
