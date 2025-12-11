"""
Tests for PDF parser functionality in lib.py

These tests verify the programme_specification_pdf_parser function which extracts
structured data from Imperial College Programme Specification PDFs.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, mock_open
from pathlib import Path


# ============================================================================
# Filename Parsing Tests
# ============================================================================

def test_parse_filename_standard_format():
    """Test parsing programme code, title, and year from standard filename."""
    from lib import programme_specification_pdf_parser

    # Mock PDF with minimal content
    with patch('pdfplumber.open') as mock_pdf:
        mock_page = Mock()
        mock_page.extract_text.return_value = "Programme Specification 2024-25"
        mock_page.extract_tables.return_value = []
        mock_pdf.return_value.__enter__.return_value.pages = [mock_page]

        result = programme_specification_pdf_parser(
            "G610-MEng-Computing-Security-and-Reliability-2024-25.pdf"
        )

        assert result["programme"]["code"] == "G610"
        assert result["programme"]["academic_year"] == "2024"
        assert "Computing Security and Reliability" in result["programme"]["title"]


def test_parse_filename_with_parentheses():
    """Test that parentheses are removed from programme title."""
    from lib import programme_specification_pdf_parser

    with patch('pdfplumber.open') as mock_pdf:
        mock_page = Mock()
        mock_page.extract_text.return_value = "Programme Specification 2024-25"
        mock_page.extract_tables.return_value = []
        mock_pdf.return_value.__enter__.return_value.pages = [mock_page]

        result = programme_specification_pdf_parser(
            "G400-BEng-Computer-Science-(Software-Engineering)-2024-25.pdf"
        )

        # Parentheses should be removed
        assert "(" not in result["programme"]["title"]
        assert ")" not in result["programme"]["title"]
        assert "Software Engineering" in result["programme"]["title"]


def test_parse_filename_code_extraction():
    """Test extraction of programme code (letter + 3 digits)."""
    from lib import programme_specification_pdf_parser

    with patch('pdfplumber.open') as mock_pdf:
        mock_page = Mock()
        mock_page.extract_text.return_value = "Programme Specification 2023-24"
        mock_page.extract_tables.return_value = []
        mock_pdf.return_value.__enter__.return_value.pages = [mock_page]

        result = programme_specification_pdf_parser("H123-MEng-Test-2023-24.pdf")

        assert result["programme"]["code"] == "H123"


# ============================================================================
# Department and Faculty Parsing Tests
# ============================================================================

def test_parse_department_from_page_text():
    """Test extraction of department name from page 1."""
    from lib import programme_specification_pdf_parser

    with patch('pdfplumber.open') as mock_pdf:
        mock_page = Mock()
        mock_page.extract_text.return_value = """
        Programme Specification 2024-25
        Department Computing
        Faculty Faculty of Engineering
        """
        mock_page.extract_tables.return_value = []
        mock_pdf.return_value.__enter__.return_value.pages = [mock_page]

        result = programme_specification_pdf_parser("G400-BSc-Test-2024-25.pdf")

        assert result["department"]["name"] == "Computing"
        assert result["department"]["faculty"] == "Faculty of Engineering"


def test_parse_department_with_suffix_removal():
    """Test that common suffixes are removed from department name."""
    from lib import programme_specification_pdf_parser

    with patch('pdfplumber.open') as mock_pdf:
        mock_page = Mock()
        mock_page.extract_text.return_value = """
        Department Computing Faculty of Engineering
        """
        mock_page.extract_tables.return_value = []
        mock_pdf.return_value.__enter__.return_value.pages = [mock_page]

        result = programme_specification_pdf_parser("G400-Test-2024-25.pdf")

        # "Faculty of Engineering" suffix should be removed
        assert result["department"]["name"] == "Computing"


def test_parse_academic_year_from_text():
    """Test extraction of academic year from 'Programme Specification YYYY-YY'."""
    from lib import programme_specification_pdf_parser

    with patch('pdfplumber.open') as mock_pdf:
        mock_page = Mock()
        mock_page.extract_text.return_value = "Programme Specification 2025-26"
        mock_page.extract_tables.return_value = []
        mock_pdf.return_value.__enter__.return_value.pages = [mock_page]

        result = programme_specification_pdf_parser("G400-Test-2024-25.pdf")

        # Should use year from text, not filename
        assert result["programme"]["academic_year"] == "2025"


# ============================================================================
# Module Table Parsing Tests
# ============================================================================

def test_parse_module_table_basic():
    """Test parsing a basic module table."""
    from lib import programme_specification_pdf_parser

    with patch('pdfplumber.open') as mock_pdf:
        mock_page = Mock()
        mock_page.extract_text.return_value = """
        Year 1 - FHEQ Level 4
        Some content
        """

        # Mock module table
        mock_page.extract_tables.return_value = [
            [
                ['Code', 'Module Title', 'Core/Elective', 'Term', 'Credits'],
                ['COMP40001', 'Introduction to Programming', 'Core', 'Autumn', '6.0'],
                ['COMP40002', 'Data Structures', 'Core', 'Spring', '7.5']
            ]
        ]

        mock_pdf.return_value.__enter__.return_value.pages = [mock_page]

        result = programme_specification_pdf_parser("G400-Test-2024-25.pdf")

        assert "year_1" in result["modules_by_year"]
        assert result["modules_by_year"]["year_1"]["year"] == 1
        assert result["modules_by_year"]["year_1"]["fheq_level"] == 4
        assert len(result["modules_by_year"]["year_1"]["modules"]) == 2

        first_module = result["modules_by_year"]["year_1"]["modules"][0]
        assert first_module["code"] == "COMP40001"
        assert first_module["title"] == "Introduction to Programming"
        assert first_module["type"] == "Core"
        assert first_module["term"] == "Autumn"
        assert first_module["credits"] == 6.0


def test_parse_module_code_validation():
    """Test that only valid module codes (4 letters + 5 digits) are accepted."""
    from lib import programme_specification_pdf_parser

    with patch('pdfplumber.open') as mock_pdf:
        mock_page = Mock()
        mock_page.extract_text.return_value = "Year 1 - FHEQ Level 4"

        # Mix of valid and invalid module codes
        mock_page.extract_tables.return_value = [
            [
                ['Code', 'Module Title', 'Core/Elective', 'Term', 'Credits'],
                ['COMP40001', 'Valid Module', 'Core', 'Autumn', '6.0'],
                ['INVALID', 'Invalid Code', 'Core', 'Autumn', '6.0'],  # Too short
                ['COMP-123', 'Invalid Format', 'Core', 'Spring', '6.0'],  # Contains dash
                ['', 'No Code', 'Core', 'Spring', '6.0'],  # Empty
                ['MATH50002', 'Another Valid Module', 'Elective', 'Spring', '7.5']
            ]
        ]

        mock_pdf.return_value.__enter__.return_value.pages = [mock_page]

        result = programme_specification_pdf_parser("G400-Test-2024-25.pdf")

        # Should only have 2 valid modules
        assert len(result["modules_by_year"]["year_1"]["modules"]) == 2
        codes = [m["code"] for m in result["modules_by_year"]["year_1"]["modules"]]
        assert "COMP40001" in codes
        assert "MATH50002" in codes
        assert "INVALID" not in codes


def test_parse_fheq_level_from_module_code():
    """Test that FHEQ level is correctly inferred from module code."""
    from lib import programme_specification_pdf_parser

    with patch('pdfplumber.open') as mock_pdf:
        # Page with Year 1 header
        mock_page1 = Mock()
        mock_page1.extract_text.return_value = "Year 1 - FHEQ Level 4"
        mock_page1.extract_tables.return_value = [
            [
                ['Code', 'Module Title', 'Core/Elective', 'Term', 'Credits'],
                ['COMP40001', 'Level 4 Module', 'Core', 'Autumn', '6.0']
            ]
        ]

        # Page with Year 3 header
        mock_page2 = Mock()
        mock_page2.extract_text.return_value = "Year 3 - FHEQ Level 6"
        mock_page2.extract_tables.return_value = [
            [
                ['Code', 'Module Title', 'Core/Elective', 'Term', 'Credits'],
                ['COMP60001', 'Level 6 Module', 'Core', 'Autumn', '6.0']
            ]
        ]

        mock_pdf.return_value.__enter__.return_value.pages = [mock_page1, mock_page2]

        result = programme_specification_pdf_parser("G400-Test-2024-25.pdf")

        # Check Year 1 (FHEQ Level 4)
        assert "year_1" in result["modules_by_year"]
        assert result["modules_by_year"]["year_1"]["fheq_level"] == 4
        assert result["modules_by_year"]["year_1"]["modules"][0]["code"] == "COMP40001"

        # Check Year 3 (FHEQ Level 6)
        assert "year_3" in result["modules_by_year"]
        assert result["modules_by_year"]["year_3"]["fheq_level"] == 6
        assert result["modules_by_year"]["year_3"]["modules"][0]["code"] == "COMP60001"


def test_parse_module_credits_extraction():
    """Test extraction of credits as float from various formats."""
    from lib import programme_specification_pdf_parser

    with patch('pdfplumber.open') as mock_pdf:
        mock_page = Mock()
        mock_page.extract_text.return_value = "Year 1 - FHEQ Level 4"

        mock_page.extract_tables.return_value = [
            [
                ['Code', 'Module Title', 'Core/Elective', 'Term', 'Credits'],
                ['COMP40001', 'Module 1', 'Core', 'Autumn', '6.0'],
                ['COMP40002', 'Module 2', 'Core', 'Spring', '7.5'],
                ['COMP40003', 'Module 3', 'Core', 'Summer', '10'],  # Integer format
                ['COMP40004', 'Module 4', 'Core', 'Autumn', '']  # Empty credits
            ]
        ]

        mock_pdf.return_value.__enter__.return_value.pages = [mock_page]

        result = programme_specification_pdf_parser("G400-Test-2024-25.pdf")

        modules = result["modules_by_year"]["year_1"]["modules"]
        assert modules[0]["credits"] == 6.0
        assert modules[1]["credits"] == 7.5
        assert modules[2]["credits"] == 10.0
        assert modules[3]["credits"] is None  # Empty credits


def test_parse_multiple_years():
    """Test parsing modules from multiple years."""
    from lib import programme_specification_pdf_parser

    with patch('pdfplumber.open') as mock_pdf:
        mock_page1 = Mock()
        mock_page1.extract_text.return_value = "Year 1 - FHEQ Level 4"
        mock_page1.extract_tables.return_value = [
            [
                ['Code', 'Module Title', 'Core/Elective', 'Term', 'Credits'],
                ['COMP40001', 'First Year Module', 'Core', 'Autumn', '6.0']
            ]
        ]

        mock_page2 = Mock()
        mock_page2.extract_text.return_value = "Year 2 - FHEQ Level 5"
        mock_page2.extract_tables.return_value = [
            [
                ['Code', 'Module Title', 'Core/Elective', 'Term', 'Credits'],
                ['COMP50001', 'Second Year Module', 'Core', 'Spring', '7.5']
            ]
        ]

        mock_pdf.return_value.__enter__.return_value.pages = [mock_page1, mock_page2]

        result = programme_specification_pdf_parser("G400-Test-2024-25.pdf")

        assert "year_1" in result["modules_by_year"]
        assert "year_2" in result["modules_by_year"]
        assert len(result["modules_by_year"]) == 2


# ============================================================================
# Course/Award Detection Tests
# ============================================================================

def test_detect_meng_course():
    """Test detection of MEng award from page 1 tables."""
    from lib import programme_specification_pdf_parser

    with patch('pdfplumber.open') as mock_pdf:
        mock_page = Mock()
        mock_page.extract_text.return_value = """
        Programme Specification 2024-25
        Department Computing
        """

        # Award table with MEng
        mock_page.extract_tables.return_value = [
            [
                ['Award', 'Duration'],
                ['MEng', '4 years']
            ]
        ]

        mock_pdf.return_value.__enter__.return_value.pages = [mock_page]

        result = programme_specification_pdf_parser("G400-MEng-Computing-2024-25.pdf")

        assert len(result["courses"]) == 1
        assert result["courses"][0]["level"] == "MEng"


def test_detect_beng_course():
    """Test detection of BEng award from page 1 tables."""
    from lib import programme_specification_pdf_parser

    with patch('pdfplumber.open') as mock_pdf:
        mock_page = Mock()
        mock_page.extract_text.return_value = """
        Programme Specification 2024-25
        Department Computing
        """

        mock_page.extract_tables.return_value = [
            [
                ['Award', 'Duration'],
                ['BEng', '3 years']
            ]
        ]

        mock_pdf.return_value.__enter__.return_value.pages = [mock_page]

        result = programme_specification_pdf_parser("G400-BEng-Computing-2024-25.pdf")

        assert len(result["courses"]) == 1
        assert result["courses"][0]["level"] == "BEng"


# ============================================================================
# Edge Cases and Error Handling Tests
# ============================================================================

def test_empty_pdf():
    """Test handling of PDF with no tables or content."""
    from lib import programme_specification_pdf_parser

    with patch('pdfplumber.open') as mock_pdf:
        mock_page = Mock()
        mock_page.extract_text.return_value = ""
        mock_page.extract_tables.return_value = []
        mock_pdf.return_value.__enter__.return_value.pages = [mock_page]

        result = programme_specification_pdf_parser("Empty-2024-25.pdf")

        # Should return empty structure without crashing
        assert result["programme"] is not None
        assert result["department"] is not None
        assert result["courses"] == []
        assert result["modules_by_year"] == {}


def test_table_without_module_title_header():
    """Test that tables without 'Module Title' header are skipped."""
    from lib import programme_specification_pdf_parser

    with patch('pdfplumber.open') as mock_pdf:
        mock_page = Mock()
        mock_page.extract_text.return_value = "Year 1 - FHEQ Level 4"

        # Table with different headers (not a module table)
        mock_page.extract_tables.return_value = [
            [
                ['Name', 'Value', 'Description'],
                ['Field1', 'Data1', 'Info1'],
                ['Field2', 'Data2', 'Info2']
            ]
        ]

        mock_pdf.return_value.__enter__.return_value.pages = [mock_page]

        result = programme_specification_pdf_parser("G400-Test-2024-25.pdf")

        # Year should be initialized but with no modules
        assert "year_1" in result["modules_by_year"]
        assert len(result["modules_by_year"]["year_1"]["modules"]) == 0


def test_module_title_with_newlines():
    """Test that newlines in module titles are replaced with spaces."""
    from lib import programme_specification_pdf_parser

    with patch('pdfplumber.open') as mock_pdf:
        mock_page = Mock()
        mock_page.extract_text.return_value = "Year 1 - FHEQ Level 4"

        mock_page.extract_tables.return_value = [
            [
                ['Code', 'Module Title', 'Core/Elective', 'Term', 'Credits'],
                ['COMP40001', 'Introduction to\nProgramming', 'Core', 'Autumn', '6.0']
            ]
        ]

        mock_pdf.return_value.__enter__.return_value.pages = [mock_page]

        result = programme_specification_pdf_parser("G400-Test-2024-25.pdf")

        module = result["modules_by_year"]["year_1"]["modules"][0]
        assert "\n" not in module["title"]
        assert "Introduction to Programming" == module["title"]


def test_multiple_year_headers_on_page():
    """Test handling of multiple year headers on a single page."""
    from lib import programme_specification_pdf_parser

    with patch('pdfplumber.open') as mock_pdf:
        mock_page = Mock()
        # Page with both Year 1 and Year 2 content
        mock_page.extract_text.return_value = """
        Year 1 - FHEQ Level 4
        Some content
        COMP40001
        Year 2 - FHEQ Level 5
        More content
        COMP50001
        """

        mock_page.extract_tables.return_value = [
            [
                ['Code', 'Module Title', 'Core/Elective', 'Term', 'Credits'],
                ['COMP40001', 'Year 1 Module', 'Core', 'Autumn', '6.0']
            ],
            [
                ['Code', 'Module Title', 'Core/Elective', 'Term', 'Credits'],
                ['COMP50001', 'Year 2 Module', 'Core', 'Spring', '7.5']
            ]
        ]

        mock_pdf.return_value.__enter__.return_value.pages = [mock_page]

        result = programme_specification_pdf_parser("G400-Test-2024-25.pdf")

        # Both years should be detected and initialized
        assert "year_1" in result["modules_by_year"]
        assert "year_2" in result["modules_by_year"]


# ============================================================================
# Integration-style Tests
# ============================================================================

def test_complete_pdf_parsing():
    """Test parsing a complete programme specification with all elements."""
    from lib import programme_specification_pdf_parser

    with patch('pdfplumber.open') as mock_pdf:
        mock_page = Mock()
        mock_page.extract_text.return_value = """
        Programme Specification 2024-25
        Department Computing
        Faculty Faculty of Engineering
        Year 1 - FHEQ Level 4
        """

        mock_page.extract_tables.return_value = [
            # Award table
            [
                ['Award'],
                ['MEng Computing']
            ],
            # Module table
            [
                ['Code', 'Module Title', 'Core/Elective', 'Term', 'Credits'],
                ['COMP40001', 'Programming I', 'Core', 'Autumn', '6.0'],
                ['COMP40002', 'Algorithms', 'Core', 'Spring', '7.5']
            ]
        ]

        mock_pdf.return_value.__enter__.return_value.pages = [mock_page]

        result = programme_specification_pdf_parser(
            "G400-MEng-Computing-2024-25.pdf"
        )

        # Check all major sections
        assert result["programme"]["code"] == "G400"
        assert result["programme"]["academic_year"] == "2024"
        assert "Computing" in result["programme"]["title"]

        assert result["department"]["name"] == "Computing"
        assert result["department"]["faculty"] == "Faculty of Engineering"

        assert len(result["courses"]) == 1
        assert result["courses"][0]["level"] == "MEng"

        assert "year_1" in result["modules_by_year"]
        assert len(result["modules_by_year"]["year_1"]["modules"]) == 2
