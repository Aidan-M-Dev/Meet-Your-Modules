import google.generativeai as genai
from enum import Enum
import os
from logger import setup_logger

# Set up logger
logger = setup_logger(__name__)

MODEL_ID = "gemini-2.5-flash-lite"

f = open("sentiment_analysis_prompt.txt", "r")
master_prompt = f.read()
f.close()

def sentiment_review(text):
    logger.debug(f"Analyzing review sentiment (length: {len(text)} chars)")
    full_prompt = master_prompt + text
    count = 0
    while count < 3:
        response = query(full_prompt)
        if response == "Yes":
            logger.info("AI sentiment analysis: Review approved (appropriate)")
            return True
        elif response == "No":
            logger.warning("AI sentiment analysis: Review flagged (inappropriate content)")
            return False
        count += 1
        logger.debug(f"AI returned non-binary answer, retrying (attempt {count}/3)")
    logger.error("AI sentiment analysis failed after 3 attempts - not returning binary answer")
    raise Exception("Gen AI not raising binary answers.")

def query(prompt):
    genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
    model = genai.GenerativeModel(MODEL_ID)
    response = model.generate_content(prompt)
    return response.text


def notify_admins_of_reported_review(review_id):
    """
    Skeleton function to notify admins of a reported review.

    Args:
        review_id (int): The review ID
    """
    # TODO: Implement admin notification system
    # This could send emails, create notifications in admin panel, etc.
    logger.warning(f"ADMIN NOTIFICATION: Review {review_id} has been reported and requires moderation")
    pass

def programme_specification_pdf_parser(file_path):  # pragma: no cover
    """
    Parse an Imperial College Programme Specification PDF and extract structured data.

    These PDFs have a standard format:
    - Page 1: Programme Information table
    - Later pages: Module tables organized by year (Year 1 - FHEQ Level X, etc.)

    Args:
        file_path (str): Path to the PDF file

    Returns:
        dict: JSON-formatted dictionary containing programme, department, and module information
    """
    import pdfplumber
    import re
    import json

    result = {
        "programme": {},
        "department": {},
        "courses": [],
        "modules_by_year": {}
    }

    # Extract programme information from filename
    # Format: CODE-Award-Title-YYYY-YY.pdf
    # Example: G610-MEng-Computing-(Security-and-Reliability)-2024-25.pdf
    import os
    filename = os.path.basename(file_path)
    filename_without_ext = filename.replace('.pdf', '')

    # Extract code (first part before first dash)
    code_match = re.match(r'^([A-Z]\d{3})', filename_without_ext)
    if code_match:
        result["programme"]["code"] = code_match.group(1)

    # Extract academic year (YYYY-YY at the end)
    year_match = re.search(r'(\d{4})-\d{2}$', filename_without_ext)
    if year_match:
        result["programme"]["academic_year"] = year_match.group(1)

    # Extract title (everything between code and year)
    # Remove code first
    title_part = filename_without_ext
    if code_match:
        title_part = title_part[len(code_match.group(1)):].lstrip('-')

    # Remove year pattern (YYYY-YY) from the end if present
    title_part = re.sub(r'-\d{4}-\d{2}$', '', title_part)

    # Clean up the title - remove parentheses, convert dashes to spaces
    title = title_part.replace('(', '').replace(')', '').replace('-', ' ').strip()
    result["programme"]["title"] = title

    with pdfplumber.open(file_path) as pdf:
        # ===== EXTRACT DEPARTMENT INFORMATION FROM PAGE 1 =====
        first_page = pdf.pages[0]
        first_page_text = first_page.extract_text()

        # Extract Department
        dept_match = re.search(r'Department\s+([^\n]+)', first_page_text)
        if dept_match:
            dept_name = dept_match.group(1).strip()
            # Clean up common suffixes
            dept_name = re.sub(r'\s+(Faculty|Ownership|External Reference).*$', '', dept_name)
            result["department"]["name"] = dept_name

        # Extract Faculty
        faculty_match = re.search(r'Faculty\s+(Faculty of [^\n]+)', first_page_text)
        if faculty_match:
            result["department"]["faculty"] = faculty_match.group(1).strip()

        # Extract academic year from "Programme Specification YYYY-YY"
        year_match = re.search(r'Programme Specification (\d{4})-(\d{2})', first_page_text)
        if year_match:
            result["programme"]["academic_year"] = year_match.group(1)

        # ===== EXTRACT MODULE TABLES FROM ALL PAGES =====
        current_year = None
        current_fheq = None

        for page in pdf.pages:
            page_text = page.extract_text()

            # Check if this page has year headers
            # A page can have multiple year headers if content for different years appears
            year_headers_on_page = list(re.finditer(r'Year (\d+)\s*[-–]\s*FHEQ Level (\d+)', page_text))

            # If there are year headers on this page, initialize years as needed
            for match in year_headers_on_page:
                year_num = int(match.group(1))
                fheq_num = int(match.group(2))
                year_key = f"year_{year_num}"

                if year_key not in result["modules_by_year"]:
                    result["modules_by_year"][year_key] = {
                        "year": year_num,
                        "fheq_level": fheq_num,
                        "modules": []
                    }

            # Update current_year based on headers found
            if len(year_headers_on_page) == 1:
                # Single year header - use it for the whole page
                match = year_headers_on_page[0]
                current_year = int(match.group(1))
                current_fheq = int(match.group(2))
            elif len(year_headers_on_page) > 1:
                # Multiple year headers - we'll determine per table
                # But initialize current_year to the first one if not set
                if current_year is None:
                    current_year = int(year_headers_on_page[0].group(1))
                    current_fheq = int(year_headers_on_page[0].group(2))
            # If no year headers, current_year stays as it was (carries over from previous page)

            # Skip if we haven't found any year header yet
            if current_year is None:
                continue

            # Extract all tables from this page
            tables = page.extract_tables()

            for table in tables:
                if not table or len(table) < 2:
                    continue

                # If there are multiple year headers on the page, we need to determine
                # which year this table belongs to by checking text above the table
                if len(year_headers_on_page) > 1:
                    # Find the table position in the text (approximate)
                    # Look for year headers that appear before this table
                    table_first_cell = str(table[0][0]) if table[0] else ""
                    if table_first_cell:
                        # Find position of table start in page text
                        table_pos = page_text.find(table_first_cell)
                        if table_pos > 0:
                            # Find the last year header before this position
                            for match in reversed(year_headers_on_page):
                                if match.start() < table_pos:
                                    current_year = int(match.group(1))
                                    current_fheq = int(match.group(2))

                                    # Initialize storage for this year
                                    year_key = f"year_{current_year}"
                                    if year_key not in result["modules_by_year"]:
                                        result["modules_by_year"][year_key] = {
                                            "year": current_year,
                                            "fheq_level": current_fheq,
                                            "modules": []
                                        }
                                    break

                # Look for the module table header
                header_idx = None
                for idx, row in enumerate(table):
                    if row and any('Module Title' in str(cell) for cell in row if cell):
                        header_idx = idx
                        break

                if header_idx is None:
                    continue

                # Get column indices from header
                header = table[header_idx]
                code_idx = next((i for i, cell in enumerate(header) if cell and 'Code' in cell), 0)
                title_idx = next((i for i, cell in enumerate(header) if cell and 'Module Title' in cell), 1)
                type_idx = next((i for i, cell in enumerate(header) if cell and 'Core' in cell or cell and 'Compulsory' in cell or cell and 'Elective' in cell), 2)
                term_idx = next((i for i, cell in enumerate(header) if cell and 'Term' in cell), 4)
                credits_idx = next((i for i, cell in enumerate(header) if cell and 'Credits' in cell), 5)

                # Process module rows
                for row in table[header_idx + 1:]:
                    if not row or len(row) <= code_idx:
                        continue

                    code = str(row[code_idx]).strip() if row[code_idx] else ""

                    # Skip if not a valid module code or is a summary row
                    if not code or not re.match(r'^[A-Z]{4}\d{5}$', code):
                        continue

                    module = {
                        "code": code,
                        "title": str(row[title_idx]).strip().replace("\n", " ") if len(row) > title_idx and row[title_idx] else "",
                        "type": str(row[type_idx]).strip() if len(row) > type_idx and row[type_idx] else "Core",
                        "term": str(row[term_idx]).strip() if len(row) > term_idx and row[term_idx] else "",
                        "credits": None
                    }

                    # Extract credits
                    if len(row) > credits_idx and row[credits_idx]:
                        try:
                            credits_str = str(row[credits_idx]).strip()
                            credits_match = re.search(r'(\d+(?:\.\d+)?)', credits_str)
                            if credits_match:
                                module["credits"] = float(credits_match.group(1))
                        except:
                            pass

                    # Add module if we have the essentials
                    if module["code"] and module["title"]:
                        # Determine the correct year for this module
                        # Use module code to infer year if possible (more reliable than position)
                        module_year = current_year

                        # Extract FHEQ level from module code (e.g., COMP40001 -> 4, AERO70010 -> 7)
                        code_level_match = re.search(r'[A-Z]{4}(\d)0', module["code"])
                        if code_level_match:
                            fheq_from_code = int(code_level_match.group(1))
                            # Map FHEQ level to year: Level 4=Year1, 5=Year2, 6=Year3, 7=Year4
                            year_from_code = fheq_from_code - 3
                            if f"year_{year_from_code}" in result["modules_by_year"]:
                                module_year = year_from_code

                        year_key = f"year_{module_year}"
                        result["modules_by_year"][year_key]["modules"].append(module)

        # ===== EXTRACT COURSE/AWARD INFORMATION =====
        # Look for the award table on page 1
        first_page_tables = first_page.extract_tables()
        for table in first_page_tables:
            if not table:
                continue

            # Look for Award column
            for row in table:
                if row and len(row) > 0 and row[0] and 'MEng' in str(row[0]):
                    result["courses"].append({
                        "title": result["programme"].get("title", ""),
                        "code": result["programme"].get("code", ""),
                        "level": "MEng",
                        "department": result["department"].get("name", "")
                    })
                    break
                elif row and len(row) > 0 and row[0] and 'BEng' in str(row[0]):
                    result["courses"].append({
                        "title": result["programme"].get("title", ""),
                        "code": result["programme"].get("code", ""),
                        "level": "BEng",
                        "department": result["department"].get("name", "")
                    })
                    break

    return result
    