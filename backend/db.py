"""Database helper functions for module_guide."""

import os
import psycopg2
from psycopg2.extras import RealDictCursor

from lib import notify_admins_of_reported_review

DATABASE_URL = os.getenv("DATABASE_URL")


def get_db_connection():
    """Create a new database connection."""
    conn = psycopg2.connect(DATABASE_URL)
    return conn


def search_modules_by_code(module_code):
    """
    Search for modules by their code.

    Args:
        module_code (str): The module code to search for

    Returns:
        list: List of module dictionaries matching the code
    """
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("SELECT * FROM modules WHERE code = %s", (module_code,))
    modules = cur.fetchall()

    cur.close()
    conn.close()

    return modules


def search_modules_by_name(search_term):
    """
    Search for modules by name, code, or lecturer using case-insensitive pattern matching.
    Returns modules with their current year courses and lecturers for filtering.

    Args:
        search_term (str): The search term to match against module names, codes, or lecturers.
                          Use '*' to return all modules.

    Returns:
        list: List of module dictionaries with courses and lecturers
    """
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    # If search term is '*', return all modules
    if search_term == '*':
        cur.execute("SELECT * FROM modules ORDER BY code")
        modules = cur.fetchall()
    else:
        # Use ILIKE for case-insensitive pattern matching
        # Search across module name, code, and lecturer names
        search_pattern = f"%{search_term}%"
        cur.execute("""
            SELECT DISTINCT m.*
            FROM modules m
            LEFT JOIN module_iterations mi ON m.id = mi.module_id
            LEFT JOIN module_iterations_lecturers_links mil ON mi.id = mil.module_iteration_id
            LEFT JOIN lecturers l ON mil.lecturer_id = l.id
            WHERE
              m.name ILIKE %s OR
              m.code ILIKE %s OR
              l.name ILIKE %s
            ORDER BY m.code
        """, (search_pattern, search_pattern, search_pattern))
        modules = cur.fetchall()

    # Get the most recent year from module_iterations
    cur.execute("SELECT MAX(academic_year_start_year) FROM module_iterations")
    result = cur.fetchone()
    current_year = result['max'] if result and result['max'] else None

    # Enrich each module with current year courses and lecturers
    enriched_modules = []
    for module in modules:
        if current_year:
            # Get current year iteration
            cur.execute(
                "SELECT id FROM module_iterations WHERE module_id = %s AND academic_year_start_year = %s",
                (module['id'], current_year)
            )
            iteration = cur.fetchone()

            if iteration:
                # Get courses for this iteration
                cur.execute("""
                    SELECT c.id, c.title
                    FROM courses c
                    INNER JOIN module_iterations_courses_links micl ON c.id = micl.course_id
                    WHERE micl.module_iteration_id = %s
                """, (iteration['id'],))
                courses = cur.fetchall()

                # Get lecturers for this iteration
                cur.execute("""
                    SELECT l.id, l.name
                    FROM lecturers l
                    INNER JOIN module_iterations_lecturers_links mil ON l.id = mil.lecturer_id
                    WHERE mil.module_iteration_id = %s
                """, (iteration['id'],))
                lecturers = cur.fetchall()

                enriched_module = dict(module)
                enriched_module['current_courses'] = courses
                enriched_module['current_lecturers'] = lecturers
                enriched_modules.append(enriched_module)
            else:
                enriched_module = dict(module)
                enriched_module['current_courses'] = []
                enriched_module['current_lecturers'] = []
                enriched_modules.append(enriched_module)
        else:
            enriched_module = dict(module)
            enriched_module['current_courses'] = []
            enriched_module['current_lecturers'] = []
            enriched_modules.append(enriched_module)

    cur.close()
    conn.close()

    return enriched_modules


def get_all_courses():
    """
    Get all courses.

    Returns:
        list: List of all course dictionaries
    """
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("SELECT * FROM courses ORDER BY title")
    courses = cur.fetchall()

    cur.close()
    conn.close()

    return courses


def get_module_by_id(module_id):
    """
    Get a module by its ID.

    Args:
        module_id (int): The module ID

    Returns:
        dict: Module data or None if not found
    """
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("SELECT * FROM modules WHERE id = %s", (module_id,))
    module = cur.fetchone()

    cur.close()
    conn.close()

    return module


def get_module_iterations(module_id):
    """
    Get all iterations of a module.

    Args:
        module_id (int): The module ID

    Returns:
        list: List of module iteration dictionaries
    """
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("SELECT * FROM module_iterations WHERE module_id = %s", (module_id,))
    iterations = cur.fetchall()

    cur.close()
    conn.close()

    return iterations


def get_lecturers_for_iteration(module_iteration_id):
    """
    Get lecturers for a specific module iteration.

    Args:
        module_iteration_id (int): The module iteration ID

    Returns:
        list: List of lecturer dictionaries
    """
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("SELECT * FROM lecturers_from_module_iteration(%s)", (module_iteration_id,))
    lecturers = cur.fetchall()

    cur.close()
    conn.close()

    return lecturers


def get_courses_for_iteration(module_iteration_id):
    """
    Get courses for a specific module iteration.

    Args:
        module_iteration_id (int): The module iteration ID

    Returns:
        list: List of course dictionaries
    """
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("SELECT * FROM courses_from_module_iteration(%s)", (module_iteration_id,))
    courses = cur.fetchall()

    cur.close()
    conn.close()

    return courses


def get_published_reviews_for_iteration(module_iteration_id):
    """
    Get published reviews for a specific module iteration.

    Args:
        module_iteration_id (int): The module iteration ID

    Returns:
        list: List of review dictionaries
    """
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute(
        "SELECT * FROM reviews WHERE module_iteration_id = %s AND moderation_status = %s",
        (module_iteration_id, 'published')
    )
    reviews = cur.fetchall()

    cur.close()
    conn.close()

    return reviews


def get_module_info_with_iterations(module_id):
    """
    Get complete module information including all iterations, lecturers, courses, and reviews.

    Args:
        module_id (int): The module ID

    Returns:
        dict: Dictionary with module metadata and yearsInfo structure or None if module not found
    """
    module = get_module_by_id(module_id)

    if not module:
        return None

    iterations = get_module_iterations(module_id)

    years_info = {}
    for iteration in iterations:
        year = iteration['academic_year_start_year']

        lecturers = get_lecturers_for_iteration(iteration['id'])
        courses = get_courses_for_iteration(iteration['id'])
        reviews = get_published_reviews_for_iteration(iteration['id'])

        if year not in years_info:
            years_info[year] = {
                "iteration_id": iteration['id'],
                "lecturers": lecturers,
                "courses": courses,
                "reviews": reviews
            }

    return {
        "module": {
            "id": module['id'],
            "code": module['code'],
            "name": module['name'],
            "credits": module['credits']
        },
        "yearsInfo": years_info
    }

def like_or_dislike_review(review_id, like_or_dislike=True):
    """
    Increment or decrement the like count for a review.

    Args:
        review_id (int): The review ID
        like_or_dislike (bool): True to like, False to dislike

    Returns:
        int: The new like count
    """
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    if like_or_dislike:
        cur.execute(
            "UPDATE reviews SET like_dislike = like_dislike + 1 WHERE id = %s RETURNING like_dislike",
            (review_id,)
        )
    else:
        cur.execute(
            "UPDATE reviews SET like_dislike = like_dislike - 1 WHERE id = %s RETURNING like_dislike",
            (review_id,)
        )

    result = cur.fetchone()

    conn.commit()
    cur.close()
    conn.close()

    return result['like_dislike'] if result else None

def report_review(review_id):
    """
    Report a review by setting its moderation status to 'reported'.
    This will notify admins for review.

    Args:
        review_id (int): The review ID

    Returns:
        bool: True if successful
    """
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute(
        "UPDATE reviews SET report_count = report_count + 1 WHERE id = %s",
        (review_id,)
    )

    cur.execute(
        "SELECT report_count, report_tolerance FROM reviews WHERE id = %s",
        (review_id,)
    )

    result = cur.fetchone()

    if result['report_count'] >= result['report_tolerance']:
        cur.execute(
            "UPDATE reviews SET moderation_status = %s WHERE id = %s",
            ('reported', review_id)
        )

        notify_admins_of_reported_review(review_id)

    conn.commit()
    cur.close()
    conn.close()

    return True

def submit_review(module_iteration_id, text, rating, reasonable):
    """
    Submit a new review for a module iteration.

    Args:
        module_iteration_id (int): The module iteration ID
        text (str): Review comment
        rating (int): Overall rating (1-5)
        reasonable (bool): Whether the review passed sentiment analysis

    Returns:
        bool: True if successful
    """
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute(
        "INSERT INTO reviews (module_iteration_id, overall_rating, comment, moderation_status, like_dislike) VALUES (%s, %s, %s, %s, 0)",
        (module_iteration_id, rating, text, 'published' if reasonable else 'automatic_review')
    )

    conn.commit()
    cur.close()
    conn.close()

    return True


def get_pending_reviews():
    """
    Get all reviews that need moderation (not published).

    Returns:
        list: List of review dictionaries with module info
    """
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT
            r.*,
            m.code as module_code,
            m.name as module_name,
            mi.academic_year_start_year
        FROM reviews r
        INNER JOIN module_iterations mi ON r.module_iteration_id = mi.id
        INNER JOIN modules m ON mi.module_id = m.id
        WHERE r.moderation_status != 'published' AND r.moderation_status != 'rejected'
        ORDER BY r.created_at DESC
    """)
    reviews = cur.fetchall()

    cur.close()
    conn.close()

    return reviews


def get_rejected_reviews():
    """
    Get all rejected reviews.

    Returns:
        list: List of rejected review dictionaries with module info
    """
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT
            r.*,
            m.code as module_code,
            m.name as module_name,
            mi.academic_year_start_year
        FROM reviews r
        INNER JOIN module_iterations mi ON r.module_iteration_id = mi.id
        INNER JOIN modules m ON mi.module_id = m.id
        WHERE r.moderation_status = 'rejected'
        ORDER BY r.created_at DESC
    """)
    reviews = cur.fetchall()

    cur.close()
    conn.close()

    return reviews


def accept_review(review_id):
    """
    Accept a review - publish it and increase report tolerance by 2.

    Args:
        review_id (int): The review ID

    Returns:
        bool: True if successful
    """
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute(
        "UPDATE reviews SET moderation_status = 'published', report_tolerance = report_tolerance + 2 WHERE id = %s",
        (review_id,)
    )

    conn.commit()
    cur.close()
    conn.close()

    return True


def reject_review(review_id):
    """
    Reject a review - set status to rejected.

    Args:
        review_id (int): The review ID

    Returns:
        bool: True if successful
    """
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute(
        "UPDATE reviews SET moderation_status = 'rejected' WHERE id = %s",
        (review_id,)
    )

    conn.commit()
    cur.close()
    conn.close()

    return True

def process_programme_spec_data(pdf_data):
    """
    Process and store programme specification data extracted from PDF.

    Args:
        pdf_data (dict): Dictionary containing programme, department, and module data

    Returns:
        dict: Summary of what was added/updated
    """
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    result = {
        "programme": pdf_data.get("programme", {}),
        "department": pdf_data.get("department", {}),
        "modules_added": 0,
        "modules_updated": 0,
        "errors": []
    }

    try:
        # 1. Insert or get department
        department_id = None
        if pdf_data.get("department", {}).get("name"):
            dept_name = pdf_data["department"]["name"]

            # Check if department exists
            cur.execute("SELECT id FROM departments WHERE name = %s", (dept_name,))
            dept = cur.fetchone()

            if dept:
                department_id = dept['id']
            else:
                # Insert new department
                cur.execute(
                    "INSERT INTO departments (name) VALUES (%s) RETURNING id",
                    (dept_name,)
                )
                department_id = cur.fetchone()['id']

        # 2. Insert or get course
        course_id = None
        if pdf_data.get("courses") and len(pdf_data["courses"]) > 0:
            course_data = pdf_data["courses"][0]
            course_title = course_data.get("title", "")

            # Check if course exists
            cur.execute("SELECT id FROM courses WHERE title = %s", (course_title,))
            course = cur.fetchone()

            if course:
                course_id = course['id']
            else:
                # Insert new course
                cur.execute(
                    "INSERT INTO courses (home_department_id, title) VALUES (%s, %s) RETURNING id",
                    (department_id, course_title)
                )
                course_id = cur.fetchone()['id']

        # 3. Process modules
        academic_year = pdf_data.get("programme", {}).get("academic_year")

        for year_key, year_data in pdf_data.get("modules_by_year", {}).items():
            for module_data in year_data.get("modules", []):
                try:
                    module_code = module_data.get("code")
                    module_name = module_data.get("title")
                    credits = module_data.get("credits", 0)

                    if not module_code or not module_name:
                        continue

                    # Check if module exists
                    cur.execute("SELECT id FROM modules WHERE code = %s", (module_code,))
                    existing_module = cur.fetchone()

                    if existing_module:
                        module_id = existing_module['id']
                        # Update module info
                        cur.execute(
                            "UPDATE modules SET name = %s, credits = %s, department_id = %s WHERE id = %s",
                            (module_name, credits, department_id, module_id)
                        )
                        result["modules_updated"] += 1
                    else:
                        # Insert new module
                        cur.execute(
                            "INSERT INTO modules (department_id, code, name, credits) VALUES (%s, %s, %s, %s) RETURNING id",
                            (department_id, module_code, module_name, credits)
                        )
                        module_id = cur.fetchone()['id']
                        result["modules_added"] += 1

                    # Create module iteration if academic year is provided
                    if academic_year and module_id:
                        # Check if this iteration already exists
                        cur.execute(
                            "SELECT id FROM module_iterations WHERE module_id = %s AND academic_year_start_year = %s",
                            (module_id, academic_year)
                        )
                        iteration = cur.fetchone()

                        if not iteration:
                            # Insert module iteration
                            cur.execute(
                                "INSERT INTO module_iterations (module_id, academic_year_start_year) VALUES (%s, %s) RETURNING id",
                                (module_id, academic_year)
                            )
                            iteration_id = cur.fetchone()['id']

                            # Link course to iteration if we have a course
                            if course_id and iteration_id:
                                cur.execute(
                                    "INSERT INTO module_iterations_courses_links (module_iteration_id, course_id) VALUES (%s, %s) ON CONFLICT DO NOTHING",
                                    (iteration_id, course_id)
                                )

                except Exception as e:
                    result["errors"].append(f"Error processing module {module_code}: {str(e)}")
                    continue

        conn.commit()

    except Exception as e:
        conn.rollback()
        raise Exception(f"Database error: {str(e)}")
    finally:
        cur.close()
        conn.close()

    return result
