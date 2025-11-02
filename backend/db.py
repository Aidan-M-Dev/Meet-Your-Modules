"""Database helper functions for module_guide."""

import os
import psycopg2
from psycopg2.extras import RealDictCursor

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
        search_term (str): The search term to match against module names, codes, or lecturers

    Returns:
        list: List of module dictionaries with courses and lecturers
    """
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

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
        dict: Dictionary with yearsInfo structure or None if module not found
    """
    module = get_module_by_id(module_id)

    if not module:
        return None

    iterations = get_module_iterations(module_id)

    years_info = {}
    for iteration in iterations:
        year = iteration['academic_year_start_year']
        term = iteration['term']

        lecturers = get_lecturers_for_iteration(iteration['id'])
        courses = get_courses_for_iteration(iteration['id'])
        reviews = get_published_reviews_for_iteration(iteration['id'])

        if year not in years_info:
            years_info[year] = {
                "term": term,
                "lecturers": lecturers,
                "courses": courses,
                "reviews": reviews
            }

    return years_info
