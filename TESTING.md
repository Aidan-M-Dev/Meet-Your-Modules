# Testing Guide

This document outlines the testing infrastructure and procedures for Meet Your Modules.

## Table of Contents

- [Overview](#overview)
- [Backend Testing (Python)](#backend-testing-python)
- [Frontend Testing (JavaScript)](#frontend-testing-javascript)
- [Continuous Integration](#continuous-integration)
- [Writing Tests](#writing-tests)
- [Test Coverage](#test-coverage)

---

## Overview

Meet Your Modules uses comprehensive testing to ensure code quality and prevent regressions:

- **Backend**: pytest with coverage reporting
- **Frontend**: Vitest with Vue Test Utils
- **CI/CD**: GitHub Actions for automated testing on push/PR

### Test Structure

```
backend/
├── conftest.py           # Shared pytest fixtures
├── pytest.ini            # Pytest configuration
├── test_app.py           # API endpoint tests
└── test_db.py            # Database function tests

frontend/
├── vitest.config.js      # Vitest configuration
└── src/
    └── __tests__/
        └── errorHandler.test.js    # Error handling tests
```

---

## Backend Testing (Python)

### Running Tests

```bash
# Run all backend tests
cd backend
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest test_app.py

# Run specific test
pytest test_app.py::test_health_endpoint

# Run with coverage report
pytest --cov=. --cov-report=html

# View coverage report
open htmlcov/index.html
```

### Test Configuration

**pytest.ini** configures:
- Test discovery patterns (`test_*.py`)
- Coverage settings
- Output verbosity
- Slowest test duration reporting

### Test Fixtures

Located in `conftest.py`:

| Fixture | Description |
|---------|-------------|
| `app` | Flask application instance for testing |
| `client` | Test client for making API requests |
| `db_connection` | Database connection with automatic rollback |
| `db_cursor` | Database cursor (RealDictCursor) |
| `mock_google_api` | Mocked Google Gemini API |
| `mock_db_connection` | Mocked database connection for unit tests |
| `sample_module` | Sample module data |
| `sample_review` | Sample review data |

### Example Test

```python
def test_search_modules_by_code(client):
    """Test searching for modules by code."""
    with patch('app.search_modules_by_code') as mock_search:
        mock_search.return_value = [
            {'id': 1, 'code': 'COMP1001', 'name': 'Programming'}
        ]

        response = client.get('/api/searchModulesByCode/COMP1001')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'modules' in data
        assert len(data['modules']) == 1
```

### Test Categories

**test_db.py** tests:
- Connection pool initialization
- Database queries (search, get module info, etc.)
- Review submission and moderation
- Admin functions (accept/reject reviews)
- Error handling and rollback

**test_app.py** tests:
- All API endpoints (`/api/*`)
- Request validation
- Response format (standardized errors)
- Rate limiting
- CORS headers
- Compression

### Mocking Google API

```python
def test_submit_review(client, mock_google_api):
    """Test review submission with mocked AI."""
    mock_google_api.generate_content.return_value.text = "yes"

    response = client.post(
        '/api/submitReview/1?overall_rating=5',
        data={'reviewText': 'Great module!'}
    )
    assert response.status_code == 200
```

---

## Frontend Testing (JavaScript)

### Running Tests

```bash
# Run all frontend tests
cd frontend
npm test

# Run tests in watch mode
npm test

# Run tests once (CI mode)
npm test -- --run

# Run with UI
npm run test:ui

# Run with coverage
npm run test:coverage
```

### Test Configuration

**vitest.config.js** configures:
- Test environment (happy-dom for DOM simulation)
- Coverage provider (v8)
- Coverage reporting (text, JSON, HTML)
- Path aliases (`@/` → `src/`)

### Example Test

```javascript
import { describe, it, expect } from 'vitest'
import { ErrorCode, parseErrorResponse } from '../utils/errorHandler'

describe('parseErrorResponse', () => {
  it('should parse standardized error format', async () => {
    const mockResponse = {
      json: async () => ({
        error: {
          message: 'Module not found',
          code: 'NOT_FOUND'
        },
        status: 'error'
      })
    }

    const result = await parseErrorResponse(mockResponse)

    expect(result.message).toBe('Module not found')
    expect(result.code).toBe('NOT_FOUND')
  })
})
```

### Testing Vue Components

```javascript
import { mount } from '@vue/test-utils'
import MyComponent from '../components/MyComponent.vue'

describe('MyComponent', () => {
  it('renders properly', () => {
    const wrapper = mount(MyComponent, {
      props: {
        msg: 'Hello Vitest'
      }
    })
    expect(wrapper.text()).toContain('Hello Vitest')
  })
})
```

---

## Continuous Integration

### GitHub Actions Workflow

`.github/workflows/test.yml` runs on:
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop`

### CI Pipeline

```
┌─────────────────────┐
│  Push/PR Trigger    │
└──────────┬──────────┘
           │
           ├──────────────────┬──────────────────┐
           │                  │                  │
           ▼                  ▼                  ▼
    ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
    │  Backend    │   │  Frontend   │   │  Lint &     │
    │  Tests      │   │  Tests      │   │  Format     │
    └─────────────┘   └─────────────┘   └─────────────┘
           │                  │                  │
           ├──────────────────┼──────────────────┘
           │
           ▼
    ┌─────────────┐
    │  Upload     │
    │  Coverage   │
    │  (Codecov)  │
    └─────────────┘
```

### Backend CI Steps

1. Set up Python 3.11
2. Start PostgreSQL service
3. Install dependencies
4. Initialize test database (run SQL scripts)
5. Run pytest with coverage
6. Upload coverage to Codecov

### Frontend CI Steps

1. Set up Node.js 18
2. Install dependencies (`npm ci`)
3. Run Vitest tests
4. Generate coverage report
5. Upload coverage to Codecov

### Viewing CI Results

- ✅ Green check: All tests passed
- ❌ Red X: Tests failed (click to see details)
- 🟡 Yellow dot: Tests running

---

## Writing Tests

### Best Practices

1. **Test Names**: Use descriptive names (`test_submit_review_with_valid_data`)
2. **Arrange-Act-Assert**: Structure tests clearly
   ```python
   # Arrange
   data = {'rating': 5, 'comment': 'Great!'}

   # Act
   result = submit_review(1, data)

   # Assert
   assert result['status'] == 'published'
   ```
3. **Mock External Services**: Always mock Google API, external APIs
4. **Use Fixtures**: Reuse common test data with fixtures
5. **Test Edge Cases**: Empty inputs, invalid data, boundary values
6. **Test Error Handling**: Ensure errors are caught and handled properly

### What to Test

**Backend:**
- ✅ All API endpoints return correct status codes
- ✅ Input validation works correctly
- ✅ Database queries return expected data
- ✅ Errors are handled and formatted correctly
- ✅ Rate limiting works
- ✅ Authentication/authorization (when implemented)

**Frontend:**
- ✅ Components render correctly
- ✅ User interactions trigger expected behavior
- ✅ API errors are handled gracefully
- ✅ Forms validate input
- ✅ Router navigation works

### What NOT to Test

- ❌ Third-party library internals (Vue, Flask, etc.)
- ❌ Database engine behavior (PostgreSQL internals)
- ❌ Browser behavior (unless testing browser compatibility)

---

## Test Coverage

### Viewing Coverage

**Backend:**
```bash
cd backend
pytest --cov=. --cov-report=html
open htmlcov/index.html
```

**Frontend:**
```bash
cd frontend
npm run test:coverage
open coverage/index.html
```

### Coverage Goals

- **Overall**: > 80%
- **Critical paths**: > 90% (API endpoints, database functions)
- **Utility functions**: > 80%
- **UI components**: > 60% (harder to test, less critical)

### Coverage Reports

Coverage reports show:
- **Lines covered**: Percentage of code executed during tests
- **Branches covered**: Percentage of if/else paths tested
- **Functions covered**: Percentage of functions called

Example:
```
Name                Stmts   Miss  Cover
---------------------------------------
app.py                150     15    90%
db.py                 120      8    93%
errors.py              45      2    96%
validators.py          60      5    92%
---------------------------------------
TOTAL                 375     30    92%
```

---

## Adding New Tests

### Backend Test (pytest)

1. Create test file: `test_<module>.py`
2. Import modules and fixtures:
   ```python
   import pytest
   from module import function_to_test
   ```
3. Write test function:
   ```python
   def test_my_function(client):
       """Test description."""
       # Test code
   ```
4. Run tests: `pytest test_<module>.py`

### Frontend Test (Vitest)

1. Create test file in `src/__tests__/`: `<component>.test.js`
2. Import test utilities:
   ```javascript
   import { describe, it, expect } from 'vitest'
   ```
3. Write test:
   ```javascript
   describe('MyFunction', () => {
     it('should do something', () => {
       // Test code
     })
   })
   ```
4. Run tests: `npm test`

---

## Debugging Tests

### Backend (pytest)

```bash
# Run with verbose output
pytest -v

# Stop on first failure
pytest -x

# Run with debugger
pytest --pdb

# Show print statements
pytest -s

# Run only failed tests from last run
pytest --lf
```

### Frontend (Vitest)

```bash
# Run in watch mode
npm test

# Run with UI
npm run test:ui

# Run single test file
npm test errorHandler.test.js

# Debug in browser
npm run test:ui
# Then click on test in UI
```

---

## Common Issues

### Issue: Tests fail in CI but pass locally

**Solution**: Ensure environment variables are set correctly in GitHub Actions

### Issue: Database connection errors in tests

**Solution**: Check `TEST_DATABASE_URL` is set and PostgreSQL service is running

### Issue: Mock not working

**Solution**: Verify import path and ensure mock is applied before function is called

### Issue: Coverage report missing files

**Solution**: Check `.coveragerc` or `pytest.ini` to ensure files aren't excluded

---

## References

- [pytest documentation](https://docs.pytest.org/)
- [Vitest documentation](https://vitest.dev/)
- [Vue Test Utils](https://test-utils.vuejs.org/)
- [GitHub Actions](https://docs.github.com/en/actions)

---

**Last Updated**: 2025-12-10
**Maintained By**: Meet Your Modules Development Team
