# API Documentation

Meet Your Modules REST API provides access to module information, reviews, and admin functionality.

## Base URL

- **Development**: `http://localhost:5000`
- **Production**: `https://yourdomain.com`

## API Versioning

The API uses versioning to ensure backward compatibility. All endpoints are prefixed with `/api/v1/`.

### Current Version: v1

All endpoints are available at `/api/v1/*`.

For backward compatibility, endpoints are also available at `/api/*` (redirects to v1).

**Example**:
- ✅ Recommended: `GET /api/v1/searchModules?q=programming`
- ⚠️ Legacy (still works): `GET /api/searchModules?q=programming`

### Version History

| Version | Status | Release Date | Deprecation Date |
|---------|--------|--------------|------------------|
| v1 | **Current** | 2025-12-10 | - |
| (unversioned) | Legacy (deprecated) | 2025-01-01 | TBD |

---

## Authentication

Most endpoints are public and do not require authentication.

Admin endpoints (`/api/v1/admin/*`) require authentication (to be implemented).

---

## Endpoints

### Health Checks

#### GET /api/v1/health

Check if API server is running.

**Response**: `200 OK`
```json
{
  "status": "ok",
  "version": "v1"
}
```

#### GET /api/v1/health/db

Check database connectivity.

**Response**: `200 OK` or `500 Internal Server Error`
```json
{
  "status": "ok",
  "database": "connected"
}
```

---

### Search

#### GET /api/v1/searchModules

Search for modules by name, code, or lecturer.

**Query Parameters**:
- `q` (string, required): Search query

**Example**:
```
GET /api/v1/searchModules?q=programming
```

**Response**: `200 OK`
```json
{
  "modules": [
    {
      "id": 1,
      "code": "COMP1001",
      "name": "Introduction to Programming",
      "department_name": "Computer Science",
      "current_lecturers": ["Dr. Smith"],
      "weighted_rating": 4.5
    }
  ],
  "status": "success"
}
```

#### GET /api/v1/searchModulesByCode/{code}

Search for modules by exact code match.

**URL Parameters**:
- `code` (string): Module code (e.g., "COMP1001")

**Example**:
```
GET /api/v1/searchModulesByCode/COMP1001
```

**Response**: Same as `/searchModules`

---

### Modules

#### GET /api/v1/getModuleInfo/{module_id}

Get detailed information for a specific module including all iterations.

**URL Parameters**:
- `module_id` (integer): Module ID

**Example**:
```
GET /api/v1/getModuleInfo/1
```

**Response**: `200 OK`
```json
{
  "yearsInfo": {
    "module_id": 1,
    "module_code": "COMP1001",
    "module_name": "Introduction to Programming",
    "credits": 20,
    "department_name": "Computer Science",
    "years": [
      {
        "academic_year": "2024/2025",
        "iteration_id": 10,
        "lecturers": [{"id": 1, "name": "Dr. Smith"}],
        "courses": [{"id": 1, "code": "G400", "name": "Computer Science BSc"}],
        "reviews": [
          {
            "id": 50,
            "rating": 5,
            "comment": "Excellent module!",
            "status": "published",
            "likes": 10,
            "dislikes": 2,
            "report_count": 0
          }
        ]
      }
    ]
  },
  "status": "success"
}
```

**Error Response**: `404 Not Found`
```json
{
  "error": {
    "message": "Module not found",
    "code": "NOT_FOUND"
  },
  "status": "error"
}
```

---

### Courses

#### GET /api/v1/courses

Get all available courses.

**Example**:
```
GET /api/v1/courses
```

**Response**: `200 OK`
```json
{
  "courses": [
    {"id": 1, "code": "G400", "name": "Computer Science BSc"},
    {"id": 2, "code": "G401", "name": "Computer Science MEng"}
  ],
  "status": "success"
}
```

---

### Reviews

#### POST /api/v1/submitReview/{module_iteration_id}

Submit a new review for a module iteration.

**URL Parameters**:
- `module_iteration_id` (integer): Module iteration ID

**Query Parameters**:
- `overall_rating` (integer, 1-5): Rating

**Form Data**:
- `reviewText` (string, min 20 chars): Review text

**Example**:
```
POST /api/v1/submitReview/10?overall_rating=5
Content-Type: application/x-www-form-urlencoded

reviewText=This module was excellent! Very well taught and interesting content.
```

**Response**: `200 OK`
```json
{
  "result": {
    "id": 51,
    "status": "published"
  },
  "status": "success"
}
```

**Note**: Review may be flagged by AI and set to "automatic_review" status.

**Rate Limit**: 5 requests per hour per IP

---

#### GET /api/v1/likeReview/{review_id}/{like_or_dislike}

Like or dislike a review.

**URL Parameters**:
- `review_id` (integer): Review ID
- `like_or_dislike` (boolean): `true` to like, `false` to dislike

**Example**:
```
GET /api/v1/likeReview/51/true
```

**Response**: `200 OK`
```json
{
  "result": {"likes": 11},
  "status": "success"
}
```

**Rate Limit**: 10 requests per minute per IP

---

#### GET /api/v1/reportReview/{review_id}

Report a review as inappropriate.

**URL Parameters**:
- `review_id` (integer): Review ID

**Example**:
```
GET /api/v1/reportReview/51
```

**Response**: `200 OK`
```json
{
  "result": {"report_count": 1},
  "status": "success"
}
```

**Rate Limit**: 5 requests per hour per IP

---

### Admin Endpoints

**Note**: These endpoints require authentication (to be implemented).

#### GET /api/v1/admin/pendingReviews

Get all reviews pending moderation.

**Response**: `200 OK`
```json
{
  "reviews": [
    {
      "id": 52,
      "comment": "Flagged review text",
      "rating": 3,
      "module_code": "COMP1001",
      "status": "automatic_review"
    }
  ],
  "status": "success"
}
```

---

#### GET /api/v1/admin/rejectedReviews

Get all rejected reviews.

**Response**: Same format as `/pendingReviews`

---

#### POST /api/v1/admin/acceptReview/{review_id}

Accept a pending review.

**URL Parameters**:
- `review_id` (integer): Review ID

**Response**: `200 OK`
```json
{
  "result": {"id": 52, "status": "published"},
  "status": "success"
}
```

**Rate Limit**: 100 requests per hour per IP

---

#### POST /api/v1/admin/rejectReview/{review_id}

Reject a pending review.

**URL Parameters**:
- `review_id` (integer): Review ID

**Response**: Same as `/acceptReview`

**Rate Limit**: 100 requests per hour per IP

---

## Error Handling

All errors follow a standardized format:

```json
{
  "error": {
    "message": "Human-readable error message",
    "code": "ERROR_CODE"
  },
  "status": "error"
}
```

### Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `VALIDATION_ERROR` | 400 | Input validation failed |
| `NOT_FOUND` | 404 | Resource not found |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |
| `NOT_IMPLEMENTED` | 501 | Feature not yet implemented |
| `INTERNAL_ERROR` | 500 | Internal server error |
| `DATABASE_ERROR` | 500 | Database operation failed |

### Example Error Response

```json
{
  "error": {
    "message": "Rating must be between 1 and 5",
    "code": "VALIDATION_ERROR"
  },
  "status": "error"
}
```

---

## Rate Limiting

Default rate limits:
- **General**: 200 requests/hour, 50 requests/minute per IP
- **Search**: 30 requests/minute
- **Review submission**: 5 requests/hour
- **Reporting**: 5 requests/hour
- **Admin actions**: 100 requests/hour

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 50
X-RateLimit-Remaining: 49
X-RateLimit-Reset: 1234567890
```

---

## CORS

CORS is configured to allow requests from:
- **Development**: `http://localhost:5173`, `http://127.0.0.1:5173`
- **Production**: Configured frontend domain only

---

## Compression

All responses are gzip compressed (when accepted by client).

Send `Accept-Encoding: gzip` header to receive compressed responses.

---

## Migration Guide

### Migrating from unversioned API to v1

**Old** (deprecated):
```javascript
fetch('/api/searchModules?q=programming')
```

**New** (recommended):
```javascript
fetch('/api/v1/searchModules?q=programming')
```

**Changes**:
- All endpoints now return `"status": "success"` or `"status": "error"`
- Error responses now include `error.code` for machine-readable errors
- Health check now includes `"version": "v1"`

**Backward Compatibility**:
- Old `/api/*` routes still work (redirect to v1)
- No breaking changes in v1 compared to unversioned API

---

## Future Versions

### Planned for v2
- OAuth2 authentication for admin endpoints
- Pagination for search results
- GraphQL endpoint
- WebSocket support for real-time updates

**Deprecation Policy**:
- Old versions supported for 12 months after new version release
- Deprecation warnings included in response headers
- Migration guides provided before deprecation

---

**Last Updated**: 2025-12-10
**Current Version**: v1
**API Documentation**: https://github.com/yourusername/Meet-Your-Modules/blob/main/API.md
