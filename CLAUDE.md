# CLAUDE.md - AI Assistant Guide for Meet Your Modules

> **Purpose**: This document provides Claude AI instances with structured context about the Meet Your Modules project for efficient development, debugging, and feature implementation.

---

## 🎯 Project Summary

**Meet Your Modules** is a full-stack university module review platform (Rate My Professor for courses) enabling students to search modules, view historical data, submit reviews, and benefit from AI-powered content moderation.

**Stack**: Flask (Python) + Vue 3 + PostgreSQL + Docker + Google Gemini AI
**License**: MIT (2025 Aidan M)
**Origin**: DurHack 2025 Hackathon Project

---

## 📁 Critical File Reference

### Backend (`/backend/`)
| File | Purpose | Key Functions |
|------|---------|---------------|
| `app.py` | Flask API server | All API endpoints, CORS config, route handlers |
| `db.py` | Database layer | `search_modules()`, `get_module_info()`, `submit_review()`, `get_pending_reviews()` |
| `lib.py` | Utilities | `sentiment_review()` (AI moderation), `programme_specification_pdf_parser()` |
| `sentiment_analysis_prompt.txt` | AI prompt | Gemini prompt for review validation |
| `requirements.txt` | Dependencies | Flask, psycopg2-binary, google-generativeai, pdfplumber |

### Frontend (`/frontend/src/`)
| File | Purpose | Key Components |
|------|---------|----------------|
| `pages/search/SearchPage.vue` | Search interface | Debounced search, course filtering |
| `pages/module/ModulePage.vue` | Module details | Review display, submission form, weighted ratings |
| `pages/admin/AdminPage.vue` | Moderation panel | Pending/rejected review management |
| `router/index.js` | Route config | `/`, `/module/:code`, `/admin` |
| `main.js` | App entry | Vue initialization, router setup |

### Database (`/backend/sql_statements/`)
| File | Purpose |
|------|---------|
| `01_schema.sql` | Complete database schema (8 tables) |
| `02_lecturers_function.sql` | Stored procedure for lecturer queries |
| `03_courses_function.sql` | Stored procedure for course queries |
| `04_test_data.sql` | Sample data for development |

### Infrastructure
| File | Purpose |
|------|---------|
| `docker-compose.yml` | Multi-container orchestration (postgres, backend, frontend) |
| `.env.example` | Environment variable template |
| `backend/Dockerfile` | Python Flask container |
| `frontend/Dockerfile` | Node.js Vite container |

---

## 🗄️ Database Schema Quick Reference

### Core Entities
```
departments (id, code, name)
  └─> modules (id, code, name, credits, department_id)
        └─> module_iterations (id, module_id, academic_year)
              ├─> module_iterations_lecturers_links (lecturer_id, module_iteration_id)
              ├─> module_iterations_courses_links (course_id, module_iteration_id)
              └─> reviews (id, module_iteration_id, rating, comment, status, likes, dislikes, report_count, report_tolerance)

lecturers (id, name)
courses (id, code, name)
```

### Review Status Values
- `published` - Visible to all users
- `automatic_review` - AI flagged, pending manual review
- `reported` - User reported (report_count >= report_tolerance)
- `rejected` - Admin rejected, archived

---

## 🔌 API Endpoints Reference

### Public Endpoints
```
GET  /api/health
GET  /api/searchModules?q={query}&course={course_code}
GET  /api/searchModulesByCode/{code}
GET  /api/getModuleInfo/{module_id}
GET  /api/courses
GET  /api/likeReview/{review_id}/{true|false}
GET  /api/reportReview/{review_id}
POST /api/submitReview/{iteration_id}
     Body: { rating: number, comment: string }
```

### Admin Endpoints
```
GET  /api/admin/pendingReviews
GET  /api/admin/rejectedReviews
POST /api/admin/acceptReview/{review_id}
POST /api/admin/rejectReview/{review_id}
```

---

## 🏗️ System Architecture

### Request Flow: Search → View → Review

```
[User] → SearchPage.vue
         ↓ (debounced 300ms)
         GET /api/searchModules?q=computing
         ↓
         db.search_modules() → PostgreSQL
         ↓
         [Results with current year data]
         ↓
[User clicks module] → ModulePage.vue
         ↓
         GET /api/searchModulesByCode/COMP1001
         ↓ (get module_id)
         GET /api/getModuleInfo/{id}
         ↓
         db.get_module_info() → Complex JOIN query
         ↓
         [Module details + reviews by year]
         ↓
[User submits review] → POST /api/submitReview/{iteration_id}
         ↓
         lib.sentiment_review() → Google Gemini API
         ↓
         If appropriate: status='published'
         If inappropriate: status='automatic_review'
         ↓
         db.submit_review() → INSERT INTO reviews
         ↓
         [Review visible OR pending moderation]
```

### Admin Moderation Flow

```
[AI flags review] OR [User reports review]
         ↓
status = 'automatic_review' OR 'reported'
         ↓
AdminPage.vue → GET /api/admin/pendingReviews
         ↓
[Admin reviews content]
         ↓
POST /api/admin/acceptReview/{id}     POST /api/admin/rejectReview/{id}
         ↓                                    ↓
status='published'                    status='rejected'
report_tolerance += 2                 (archived)
```

---

## 🔧 Development Commands

### Docker (Recommended)
```bash
# Start all services
docker-compose up --build

# Rebuild specific service
docker-compose up --build backend

# View logs
docker-compose logs -f backend

# Stop all services
docker-compose down
```

**Service URLs:**
- Frontend: http://localhost:5173
- Backend: http://localhost:5000
- PostgreSQL: localhost:5432

### Manual Development

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

---

## 🔐 Environment Variables

Required in `.env` file (see `.env.example`):

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# Google AI (for review moderation)
GOOGLE_API_KEY=your_gemini_api_key_here

# CORS Configuration
FRONTEND_ADDRESS=http://localhost
FRONTEND_PORT=5173

# Backend Configuration
BACKEND_ADDRESS=http://localhost
BACKEND_PORT=5000
```

**⚠️ Important**: Google API key is REQUIRED for review submission (AI moderation)

---

## 💡 Key Implementation Patterns

### 1. Debounced Search
```javascript
// SearchPage.vue - 300ms delay prevents excessive API calls
let timeout;
const onSearch = () => {
  clearTimeout(timeout);
  timeout = setTimeout(() => {
    // Actual search logic
  }, 300);
};
```

### 2. Weighted Rating Calculation
```javascript
// ModulePage.vue - Recent reviews weighted more heavily
const weightedAverage = computed(() => {
  const currentYear = new Date().getFullYear();
  let weightedSum = 0;
  let totalWeight = 0;

  reviews.forEach(review => {
    const yearDiff = currentYear - review.academic_year;
    const weight = Math.exp(-0.2 * yearDiff); // Exponential decay
    weightedSum += review.rating * weight;
    totalWeight += weight;
  });

  return totalWeight > 0 ? weightedSum / totalWeight : 0;
});
```

### 3. AI Sentiment Analysis with Retry
```python
# lib.py - Retries up to 3 times for binary response
def sentiment_review(review):
    for attempt in range(3):
        response = model.generate_content(f"{prompt}\n\nReview: {review}")
        if response.text.strip().lower() in ['yes', 'no']:
            return response.text.strip().lower() == 'yes'
    return False  # Default to rejection if unclear
```

### 4. Report Tolerance System
```python
# db.py - Accepted reviews get +2 tolerance
def accept_review(review_id):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE reviews
                SET status = 'published',
                    report_tolerance = report_tolerance + 2
                WHERE id = %s
            """, (review_id,))
```

---

## 🐛 Common Issues & Solutions

### Issue: Review submission fails
**Check:**
1. `GOOGLE_API_KEY` environment variable is set
2. Backend logs for API errors
3. Database connection is active
4. `module_iteration_id` exists in database

### Issue: Database connection refused
**Solutions:**
```bash
# Check PostgreSQL is running
docker-compose ps

# Restart database
docker-compose restart postgres

# Check connection string in .env
DATABASE_URL=postgresql://user:password@postgres:5432/dbname
```

### Issue: Frontend can't reach backend
**Check:**
1. Vite proxy config in `vite.config.js` points to correct backend URL
2. CORS configuration in `app.py` allows frontend origin
3. Backend is running on port 5000
4. Environment variables `FRONTEND_ADDRESS` and `FRONTEND_PORT` are correct

### Issue: Changes not reflecting
**Frontend:**
```bash
# Clear Vite cache
rm -rf frontend/node_modules/.vite
npm run dev
```

**Backend:**
```bash
# Restart Flask (it auto-reloads in debug mode)
# Or rebuild Docker container
docker-compose up --build backend
```

---

## 🧪 Testing Approach

### Manual Testing Checklist
- [ ] Search modules by name/code/lecturer
- [ ] Filter by course
- [ ] View module details across multiple years
- [ ] Submit review (should trigger AI moderation)
- [ ] Like/dislike reviews
- [ ] Report inappropriate review
- [ ] Admin: View pending reviews
- [ ] Admin: Accept/reject reviews
- [ ] Verify weighted rating calculation
- [ ] Check lecturer change detection

### Database Testing
```sql
-- Verify module iterations exist
SELECT mi.id, m.code, mi.academic_year
FROM module_iterations mi
JOIN modules m ON m.id = mi.module_id
LIMIT 10;

-- Check review statuses
SELECT status, COUNT(*)
FROM reviews
GROUP BY status;

-- Find reported reviews
SELECT * FROM reviews
WHERE report_count >= report_tolerance;
```

---

## 📝 Code Modification Guidelines

### When Adding New Endpoints

1. **Define route in `app.py`:**
```python
@app.route('/api/newEndpoint', methods=['GET'])
def new_endpoint():
    result = db.new_database_function()
    return jsonify(result)
```

2. **Add database function in `db.py`:**
```python
def new_database_function():
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM table")
            return cur.fetchall()
```

3. **Update frontend API calls:**
```javascript
// In appropriate Vue component
const fetchData = async () => {
  const response = await fetch('/api/newEndpoint');
  const data = await response.json();
  // Handle data
};
```

### When Adding New Database Tables

1. **Create migration in `sql_statements/`:**
```sql
-- 05_new_table.sql
CREATE TABLE new_table (
    id SERIAL PRIMARY KEY,
    -- columns
);
```

2. **Update `docker-compose.yml` if needed:**
```yaml
volumes:
  - ./backend/sql_statements:/docker-entrypoint-initdb.d/
```

3. **Restart database to apply:**
```bash
docker-compose down
docker-compose up --build postgres
```

### When Adding New Vue Pages

1. **Create component in `frontend/src/pages/`:**
```vue
<template>
  <!-- Component template -->
</template>

<script setup>
// Component logic
</script>
```

2. **Add route in `router/index.js`:**
```javascript
{
  path: '/new-page',
  name: 'NewPage',
  component: () => import('../pages/NewPage.vue')
}
```

3. **Add navigation link if needed:**
```vue
<router-link to="/new-page">New Page</router-link>
```

---

## 🚀 Deployment Considerations

### Current State
- Development configuration (Docker Compose)
- Frontend uses Vite dev server (not production build)
- No authentication system (admin auth planned, not implemented)
- No HTTPS configuration
- Anonymous review submission (by design - no user accounts needed)

### For Production (Not Implemented)
**Would Need:**
- [ ] Admin authentication with role hierarchy (standard admin + senior admin)
- [ ] Production build of frontend (`npm run build`)
- [ ] Nginx/reverse proxy setup
- [ ] HTTPS certificates
- [ ] Environment-based configuration
- [ ] Database backup strategy
- [ ] Logging and monitoring
- [ ] Rate limiting on API endpoints
- [ ] Input validation and sanitization (partially implemented)
- [ ] Responsive mobile design optimization

**Design Philosophy:**
- **No user accounts**: Students can submit reviews anonymously without login
- **Anonymous sessions**: Lightweight browser sessions for UX (preserve filters) and abuse prevention (duplicate likes)
- **Admin-only auth**: Only moderators need authentication (with senior admin role for managing admins)
- **Mobile-friendly**: Responsive web design, no dedicated mobile app

---

## 🎓 Domain Knowledge

### Academic Year Format
- Format: `2024/2025` (string)
- Current year calculated in frontend: `new Date().getFullYear()`

### Module Codes
- Format: Varies by university (e.g., `COMP1001`, `CS101`)
- Case-insensitive search implemented

### Lecturer Assignment
- Many-to-many relationship (module iteration ↔ lecturers)
- Same lecturer can teach multiple iterations
- Multiple lecturers can teach same iteration

### Review Rating System
- Scale: 1-5 stars (integer)
- Displayed as filled/outlined stars in UI
- Weighted average favors recent years

---

## 🔍 Quick Debugging Commands

### Check Backend Health
```bash
curl http://localhost:5000/api/health
```

### Search Modules
```bash
curl "http://localhost:5000/api/searchModules?q=computing"
```

### View PostgreSQL Logs
```bash
docker-compose logs postgres
```

### Connect to PostgreSQL
```bash
docker-compose exec postgres psql -U user -d dbname
```

### Restart Single Service
```bash
docker-compose restart backend
```

---

## 📚 External Dependencies & Docs

- **Flask**: https://flask.palletsprojects.com/
- **Vue 3**: https://vuejs.org/guide/
- **PostgreSQL**: https://www.postgresql.org/docs/
- **Tailwind CSS**: https://tailwindcss.com/docs
- **Vite**: https://vitejs.dev/guide/
- **Google Generative AI**: https://ai.google.dev/docs
- **pdfplumber**: https://github.com/jsvine/pdfplumber

---

## ⚡ Quick Start for New Claude Instances

1. **Read this file completely**
2. **Verify environment**: Check `.env` file exists with required variables
3. **Start services**: `docker-compose up --build`
4. **Access frontend**: http://localhost:5173
5. **Test API**: `curl http://localhost:5000/api/health`
6. **Review schema**: Read `/backend/sql_statements/01_schema.sql`
7. **Check current task**: See `CLAUDE-TODO.md`

---

## 🤝 Working with This Codebase

### Best Practices
- **Always read files before editing** - Don't assume structure
- **Test database changes** - Use `04_test_data.sql` as reference
- **Check API responses** - Use browser DevTools or curl
- **Verify CORS** - Ensure frontend origin is allowed
- **Review logs** - Check Docker logs for errors
- **Commit frequently** - Clear commit messages
- **Update this doc** - When adding major features

### Anti-Patterns to Avoid
- ❌ Modifying database schema without migration files
- ❌ Adding endpoints without database functions
- ❌ Skipping AI moderation for reviews
- ❌ Hardcoding URLs/ports (use environment variables)
- ❌ Ignoring error handling
- ❌ Creating new files when editing existing ones works

---

**Last Updated**: 2025-12-10
**Maintained By**: Claude AI instances working on this project
**Questions?** Refer to README.md or analyze source code directly
