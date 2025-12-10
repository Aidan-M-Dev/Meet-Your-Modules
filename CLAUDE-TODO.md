# CLAUDE-TODO.md - Task Management for AI Instances

> **Purpose**: This file provides a structured format for tracking features, bugs, and technical debt. Designed for use by manager Claude instances to create scrum-style tickets and by developer instances to track progress.

---

## 📋 How to Use This File

### For Manager Instances
1. **Review current state** of TODO sections below
2. **Create tickets** from "Feature Backlog" or "Bug Backlog"
3. **Assign priority** (P0-P3) based on impact and dependencies
4. **Move items** between sections as work progresses
5. **Update status** when work is completed
6. **Delete completed** items entirely (they're preserved in git history)

### For Developer Instances
1. **Check "In Progress"** section for current work
2. **Update status** as you work on tasks
3. **Move to "Ready for Review"** when complete
4. **Add new bugs/tasks** as discovered
5. **Link commits** to task IDs in commit messages

### Ticket Format
```markdown
### [TICKET-ID] Ticket Title
**Type**: Feature | Bug | Technical Debt | Documentation
**Priority**: P0 (Critical) | P1 (High) | P2 (Medium) | P3 (Low)
**Status**: Backlog | In Progress | Ready for Review | Done | Blocked
**Assignee**: @claude-instance-name (optional)
**Estimated Effort**: XS | S | M | L | XL
**Dependencies**: [TICKET-IDs] (if applicable)

**Description**:
[Clear description of what needs to be done]

**Acceptance Criteria**:
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

**Technical Notes**:
- Implementation details
- Files affected
- Database changes needed

**Related Files**:
- `path/to/file1.py`
- `path/to/file2.vue`

**Testing**:
- [ ] Unit tests
- [ ] Integration tests
- [ ] Manual testing steps

**Links**:
- Related issues/PRs
- Documentation references
```

---

## 🚦 Current Sprint

**Sprint Goal**: Establish production-ready foundation with admin security and mobile responsiveness
**Sprint Duration**: TBD
**Start Date**: TBD
**End Date**: TBD

### In Progress

*(No items currently)*

---

### Ready for Review

*(No items currently)*

---

### Blocked

*(No items currently)*

---

## 📦 Feature Backlog

### [MYM-001] Admin Authentication with Role Hierarchy
**Type**: Feature
**Priority**: P0 (Critical)
**Status**: Backlog
**Estimated Effort**: L
**Dependencies**: None

**Description**:
Secure admin panel with role-based access control. Currently, admin panel is publicly accessible at `/admin`. System needs two admin roles: standard admins (can moderate reviews) and senior admins (can add/remove other admins).

**Note**: Regular users do NOT need accounts - they submit reviews anonymously. Only admins need authentication.

**Acceptance Criteria**:
- [ ] `admins` table with username, password_hash, role (standard/senior)
- [ ] Admin login page at `/admin/login`
- [ ] Session/JWT-based authentication
- [ ] Admin-only route guards for `/admin` pages
- [ ] Admin middleware for all `/api/admin/*` endpoints
- [ ] Senior admin can create/delete admin accounts
- [ ] Standard admin can only moderate reviews
- [ ] Admin management page (senior admins only)
- [ ] Audit log for admin actions (who accepted/rejected what)
- [ ] Logout functionality

**Technical Notes**:
- Install `flask-jwt-extended` or use Flask sessions
- Use bcrypt for password hashing
- Add `admins` table (NOT users - no user accounts)
- Create Vue composable for admin auth state
- Add route guards in Vue Router for `/admin` routes
- Consider initial seed admin in SQL or env variable

**Related Files**:
- `backend/app.py` - Add admin auth endpoints & middleware
- `backend/db.py` - Add admin management functions
- `backend/sql_statements/05_admins_schema.sql` - New migration
- `frontend/src/pages/admin/LoginPage.vue` - New component
- `frontend/src/pages/admin/ManageAdminsPage.vue` - New component (senior only)
- `frontend/src/composables/useAdminAuth.js` - New auth composable
- `frontend/src/router/index.js` - Add admin route guards

**Testing**:
- [ ] Login with wrong password fails
- [ ] Standard admin cannot access admin management
- [ ] Senior admin can create new admins
- [ ] Protected endpoints reject unauthenticated requests
- [ ] Session persists across page refreshes
- [ ] Admin actions are logged correctly

---

### [MYM-002] Email Notifications for Admin
**Type**: Feature
**Priority**: P2 (Medium)
**Status**: Backlog
**Estimated Effort**: S
**Dependencies**: None

**Description**:
Send email notifications to admins when reviews are reported or flagged by AI. Currently, `notify_admin()` function exists but is not implemented.

**Acceptance Criteria**:
- [ ] Email service configured (SendGrid, AWS SES, or SMTP)
- [ ] Email template for flagged reviews
- [ ] Batched notifications (not per-review)
- [ ] Admin email preferences
- [ ] Unsubscribe functionality

**Technical Notes**:
- Install `flask-mail` or use external service
- Implement `lib.notify_admin()` function
- Add `SMTP_*` environment variables
- Consider daily digest instead of immediate emails

**Related Files**:
- `backend/lib.py:38` - Implement `notify_admin()`
- `backend/app.py` - Call notify on flag/report
- `.env.example` - Add email configuration

---

### [MYM-003] Advanced Search Filters
**Type**: Feature
**Priority**: P2 (Medium)
**Status**: Backlog
**Estimated Effort**: M
**Dependencies**: None

**Description**:
Enhance search with filters for credits, department, academic year, and rating range.

**Acceptance Criteria**:
- [ ] Filter by module credits (10, 20, 40, etc.)
- [ ] Filter by department
- [ ] Filter by academic year availability
- [ ] Filter by minimum rating
- [ ] Combine multiple filters
- [ ] Clear all filters button
- [ ] Filter state in URL query params

**Related Files**:
- `frontend/src/pages/search/SearchPage.vue`
- `backend/db.py` - Update `search_modules()`
- `backend/app.py` - Accept filter parameters

---

### [MYM-004] Module Comparison Tool
**Type**: Feature
**Priority**: P3 (Low)
**Status**: Backlog
**Estimated Effort**: L
**Dependencies**: None

**Description**:
Allow users to select 2-3 modules and view side-by-side comparison of ratings, lecturers, and reviews.

**Acceptance Criteria**:
- [ ] "Add to Compare" button on search results
- [ ] Comparison page at `/compare`
- [ ] Side-by-side module information
- [ ] Rating comparison chart
- [ ] Review sentiment comparison
- [ ] Export comparison as PDF

**Related Files**:
- `frontend/src/pages/compare/ComparePage.vue` - New component
- `frontend/src/composables/useComparison.js` - Comparison state
- `backend/app.py` - Bulk module fetch endpoint

---

### [MYM-005] Analytics Dashboard
**Type**: Feature
**Priority**: P3 (Low)
**Status**: Backlog
**Estimated Effort**: XL
**Dependencies**: None

**Description**:
Admin dashboard showing system usage statistics, popular modules, review trends, and moderation metrics.

**Acceptance Criteria**:
- [ ] Total reviews, modules, users
- [ ] Most reviewed modules
- [ ] Review submission over time graph
- [ ] Moderation statistics (AI accuracy, report rates)
- [ ] Department-wise breakdown
- [ ] Export data as CSV

**Related Files**:
- `frontend/src/pages/admin/AnalyticsPage.vue` - New component
- `backend/app.py` - Analytics API endpoints
- `backend/db.py` - Analytics queries

---

### [MYM-006] Responsive Mobile Design
**Type**: Feature
**Priority**: P1 (High)
**Status**: Backlog
**Estimated Effort**: M
**Dependencies**: None

**Description**:
Ensure excellent mobile experience through responsive web design. No dedicated mobile app needed - site should work perfectly on mobile browsers.

**Acceptance Criteria**:
- [ ] All pages responsive on mobile (320px+)
- [ ] Touch-friendly buttons and form elements
- [ ] Mobile-optimized search interface
- [ ] Easy-to-read review cards on small screens
- [ ] Mobile-friendly admin panel
- [ ] Test on iOS Safari and Android Chrome
- [ ] Hamburger menu for navigation (if needed)
- [ ] Proper viewport meta tags
- [ ] Fast loading on mobile networks

**Technical Notes**:
- Already using Tailwind CSS with responsive utilities
- May need to adjust spacing, font sizes, touch targets
- Test with Chrome DevTools mobile emulation
- Consider lazy loading for review lists

**Related Files**:
- `frontend/src/pages/search/SearchPage.vue` - Mobile search UX
- `frontend/src/pages/module/ModulePage.vue` - Mobile review display
- `frontend/src/pages/admin/AdminPage.vue` - Mobile admin panel
- `frontend/index.html` - Viewport meta tags

**Testing**:
- [ ] Test on iPhone (Safari)
- [ ] Test on Android (Chrome)
- [ ] Test landscape and portrait orientations
- [ ] Verify touch targets are 44x44px minimum
- [ ] Check text readability without zooming

---

### [MYM-007] Anonymous User Sessions
**Type**: Feature
**Priority**: P1 (High)
**Status**: Backlog
**Estimated Effort**: M
**Dependencies**: None

**Description**:
Implement lightweight anonymous user sessions to preserve search preferences and prevent abuse (duplicate likes/reports). Users do NOT need to create accounts or login - this is purely for tracking browser sessions.

**Acceptance Criteria**:
- [ ] Generate anonymous session ID on first visit (cookie or localStorage)
- [ ] Preserve search filters (course, query) in session
- [ ] Track which reviews user has liked/disliked (prevent duplicate votes)
- [ ] Track which reviews user has reported (prevent spam reporting)
- [ ] Session persists across page refreshes
- [ ] No personally identifiable information stored
- [ ] Session expires after 30 days of inactivity
- [ ] Backend validates session for like/report endpoints

**Technical Notes**:
- Use HTTP-only cookies for session ID (more secure than localStorage)
- Store session data in PostgreSQL or Redis
- Session table: `id`, `session_id`, `created_at`, `last_active`, `liked_reviews[]`, `reported_reviews[]`, `search_preferences`
- Alternative: Use localStorage for preferences only, backend tracks IPs for abuse prevention
- Consider privacy implications - GDPR compliance if needed

**Related Files**:
- `backend/app.py` - Session middleware, update like/report endpoints
- `backend/db.py` - Session management functions
- `backend/sql_statements/06_sessions_schema.sql` - New migration
- `frontend/src/composables/useSession.js` - Session state management
- `frontend/src/pages/search/SearchPage.vue` - Load/save search preferences

**Testing**:
- [ ] Search preferences persist after navigation
- [ ] User cannot like same review twice
- [ ] User cannot report same review twice
- [ ] Session survives page refresh
- [ ] New browser/incognito gets fresh session
- [ ] Old sessions cleaned up automatically

**Privacy Notes**:
- No user accounts, no email, no personal data
- Session IDs are random, not tied to identity
- Used only for UX and abuse prevention
- Add privacy policy note if needed

---

## 🐛 Bug Backlog

### [BUG-001] Review Submission Without Iteration
**Type**: Bug
**Priority**: P1 (High)
**Status**: Backlog
**Estimated Effort**: S
**Dependencies**: None

**Description**:
If a module has no iteration for selected academic year, review submission fails silently.

**Acceptance Criteria**:
- [ ] Check if iteration exists before showing review form
- [ ] If missing, show "Cannot review - year not available"
- [ ] Or create iteration on-demand with admin approval

**Related Files**:
- `frontend/src/pages/module/ModulePage.vue`
- `backend/app.py` - Add validation to `/api/submitReview`

**Testing**:
- [ ] Try submitting review for non-existent year
- [ ] Verify error message appears
- [ ] Verify no database insertion

---

### [BUG-002] Weighted Rating With No Reviews
**Type**: Bug
**Priority**: P2 (Medium)
**Status**: Backlog
**Estimated Effort**: XS
**Dependencies**: None

**Description**:
Weighted rating calculation shows NaN or 0 when module has no reviews. Should show "No ratings yet".

**Acceptance Criteria**:
- [ ] Display "No ratings yet" when reviews.length === 0
- [ ] Hide star display until first review

**Related Files**:
- `frontend/src/pages/module/ModulePage.vue`

---

### [BUG-003] Course Filter Doesn't Persist on Navigation
**Type**: Bug
**Priority**: P3 (Low)
**Status**: Backlog
**Estimated Effort**: XS
**Dependencies**: None

**Description**:
When user filters by course, navigates to module, then goes back, filter is reset.

**Note**: This will be addressed by [MYM-007] Anonymous User Sessions, which persists search preferences.

**Acceptance Criteria**:
- [ ] Store filter in URL query params OR session storage
- [ ] Restore filter from URL/session on page load
- [ ] Persist across navigation

**Related Files**:
- `frontend/src/pages/search/SearchPage.vue`
- `frontend/src/router/index.js`

---

### [BUG-004] Duplicate Lecturers in Search Results
**Type**: Bug
**Priority**: P2 (Medium)
**Status**: Backlog
**Estimated Effort**: XS
**Dependencies**: None

**Description**:
Search results sometimes show duplicate lecturer names when they teach multiple iterations.

**Acceptance Criteria**:
- [ ] Deduplicate lecturers by ID in `search_modules()`
- [ ] Show only current year lecturers
- [ ] Verify no duplicates in UI

**Related Files**:
- `backend/db.py` - Fix `search_modules()` query

---

## 🔧 Technical Debt

### [TECH-001] Migrate to Production Build
**Type**: Technical Debt
**Priority**: P0 (Critical)
**Status**: Backlog
**Estimated Effort**: M
**Dependencies**: None

**Description**:
Currently using Vite dev server for frontend. Need production build with proper optimization.

**Acceptance Criteria**:
- [ ] Run `npm run build` in Docker
- [ ] Serve static files from Flask or Nginx
- [ ] Configure asset caching headers
- [ ] Minimize bundle size
- [ ] Enable gzip compression
- [ ] Update docker-compose for production

**Related Files**:
- `frontend/Dockerfile`
- `docker-compose.yml`
- `backend/app.py` - Serve static files

---

### [TECH-002] Add Proper Logging
**Type**: Technical Debt
**Priority**: P1 (High)
**Status**: Backlog
**Estimated Effort**: S
**Dependencies**: None

**Description**:
Replace print statements with proper logging framework for debugging and monitoring.

**Acceptance Criteria**:
- [ ] Use Python `logging` module
- [ ] Log levels (DEBUG, INFO, WARNING, ERROR)
- [ ] Log to file and console
- [ ] Structured logging (JSON format)
- [ ] Log rotation

**Related Files**:
- `backend/app.py`
- `backend/db.py`
- `backend/lib.py`

---

### [TECH-003] Input Validation & Sanitization
**Type**: Technical Debt
**Priority**: P0 (Critical)
**Status**: Backlog
**Estimated Effort**: M
**Dependencies**: None

**Description**:
Add comprehensive input validation to prevent SQL injection, XSS, and other attacks.

**Acceptance Criteria**:
- [ ] Validate all API inputs
- [ ] Use parameterized queries (already done)
- [ ] Sanitize HTML in reviews
- [ ] Rate limiting on API endpoints
- [ ] CSRF protection
- [ ] Input length limits

**Technical Notes**:
- Install `flask-limiter` for rate limiting
- Use `bleach` or `html.escape()` for sanitization
- Add request validation decorators

**Related Files**:
- `backend/app.py` - All endpoints
- `backend/db.py` - Already uses parameterized queries

---

### [TECH-004] Database Connection Pooling
**Type**: Technical Debt
**Priority**: P2 (Medium)
**Status**: Backlog
**Estimated Effort**: S
**Dependencies**: None

**Description**:
Implement connection pooling for better database performance under load.

**Acceptance Criteria**:
- [ ] Use `psycopg2.pool.SimpleConnectionPool`
- [ ] Configure min/max connections
- [ ] Handle pool exhaustion gracefully
- [ ] Add connection health checks

**Related Files**:
- `backend/db.py` - Replace `get_db_connection()`

---

### [TECH-005] Environment-Based Configuration
**Type**: Technical Debt
**Priority**: P1 (High)
**Status**: Backlog
**Estimated Effort**: S
**Dependencies**: None

**Description**:
Separate development and production configurations.

**Acceptance Criteria**:
- [ ] Create `config.py` with DevelopmentConfig and ProductionConfig
- [ ] Use `FLASK_ENV` to switch configs
- [ ] Different CORS policies per environment
- [ ] Different database URLs
- [ ] Environment-specific secrets

**Related Files**:
- `backend/config.py` - New file
- `backend/app.py` - Use config object
- `.env.example` - Add `FLASK_ENV`

---

### [TECH-006] API Versioning
**Type**: Technical Debt
**Priority**: P3 (Low)
**Status**: Backlog
**Estimated Effort**: S
**Dependencies**: None

**Description**:
Implement API versioning to allow backward compatibility for future changes.

**Acceptance Criteria**:
- [ ] Prefix all routes with `/api/v1/`
- [ ] Support multiple versions simultaneously
- [ ] Deprecation warnings for old versions

**Related Files**:
- `backend/app.py` - Update all routes
- `frontend/` - Update all API calls

---

### [TECH-007] Unit Test Suite
**Type**: Technical Debt
**Priority**: P1 (High)
**Status**: Backlog
**Estimated Effort**: L
**Dependencies**: None

**Description**:
Add comprehensive unit and integration tests for backend and frontend.

**Acceptance Criteria**:
- [ ] Backend: pytest for all db functions
- [ ] Backend: Test all API endpoints
- [ ] Backend: Mock Google API calls
- [ ] Frontend: Vitest for components
- [ ] Frontend: Test search, module view, review submission
- [ ] CI/CD integration (GitHub Actions)

**Related Files**:
- `backend/test_app.py` - New file
- `backend/test_db.py` - New file
- `frontend/src/__tests__/` - New directory

---

### [TECH-008] Error Handling Standardization
**Type**: Technical Debt
**Priority**: P2 (Medium)
**Status**: Backlog
**Estimated Effort**: M
**Dependencies**: None

**Description**:
Standardize error responses across all API endpoints.

**Acceptance Criteria**:
- [ ] Consistent error response format: `{error: string, code: string}`
- [ ] Proper HTTP status codes
- [ ] Error codes for different failure types
- [ ] Frontend error handling utilities

**Related Files**:
- `backend/app.py` - Error handlers
- `frontend/src/utils/errorHandler.js` - New file

---

## 📊 Priority Definitions

- **P0 (Critical)**: Blocks production deployment or major functionality
- **P1 (High)**: Important feature or significant bug
- **P2 (Medium)**: Nice to have, improves UX
- **P3 (Low)**: Future enhancement, not urgent

## 📏 Effort Estimation

- **XS**: < 2 hours
- **S**: 2-4 hours
- **M**: 4-8 hours
- **L**: 1-2 days
- **XL**: 2+ days

---

## 🔄 Workflow

```
Backlog → In Progress → Ready for Review → Delete (work complete)
                ↓
             Blocked
```

**Note**: Completed tickets are deleted from this file to save space. All work is preserved in git commit history.

---

## 📝 Notes for Manager Instances

### Sprint Planning
1. Review backlog and prioritize based on:
   - User impact
   - Technical dependencies
   - Security concerns
   - Effort vs. value
2. Group related tickets (e.g., all auth-related)
3. Balance P0/P1 with P2/P3 items
4. Consider developer bandwidth

### Ticket Creation Best Practices
- **Be specific**: Clear acceptance criteria
- **Link dependencies**: Use [TICKET-ID] references
- **Estimate effort**: Use fibonacci-like scale
- **Add context**: Include "why" not just "what"
- **Test criteria**: Define how to verify completion

### Regular Maintenance
- **Weekly**: Review "In Progress" status
- **Bi-weekly**: Groom backlog, update priorities
- **As needed**: Delete completed items to keep file lean
- **Quarterly**: Review technical debt

---

**Last Updated**: 2025-12-10
**Maintained By**: Claude AI instances (manager & developer)
**Template Version**: 1.0
