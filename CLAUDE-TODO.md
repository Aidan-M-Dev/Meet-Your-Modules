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

### [TEST-003] Frontend Component Tests - AdminPage
**Type**: Technical Debt
**Priority**: P2 (Medium)
**Status**: Backlog
**Estimated Effort**: L
**Dependencies**: [MYM-001] (Admin Authentication)

**Description**:
Add comprehensive unit tests for AdminPage.vue component, including review moderation functionality, lecturer/course management, and admin actions.

**Acceptance Criteria**:
- [ ] Test reviews list loading and display
- [ ] Test review approval/rejection actions
- [ ] Test lecturer management (add/view/delete)
- [ ] Test course management (add/view/delete)
- [ ] Test admin authentication checks
- [ ] Test error handling
- [ ] Mock API calls appropriately
- [ ] Test permission-based UI rendering

**Related Files**:
- `frontend/src/pages/admin/AdminPage.vue`
- `frontend/src/__tests__/AdminPage.test.js` - New file

**Testing**:
- [ ] Unit tests with Vitest
- [ ] Component mounting with @vue/test-utils
- [ ] Admin action tests
- [ ] Coverage > 70% (lower due to auth dependency)

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
- [ ] Admin login page at `/admin/login` (no obvious button/link - admins navigate directly)
- [ ] Session/JWT-based authentication
- [ ] Admin-only route guards for `/admin` pages
- [ ] Admin middleware for all `/api/admin/*` endpoints
- [ ] Senior admin can create/delete admin accounts
- [ ] Standard admin can only moderate reviews
- [ ] Admin management page (senior admins only)
- [ ] Audit log for admin actions (who accepted/rejected what)
- [ ] Obvious logout button on admin pages
- [ ] No "Admin" links visible to regular users

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

### [MYM-008] Report Reviews with Categorized Reasons
**Type**: Feature
**Priority**: P1 (High)
**Status**: Backlog
**Estimated Effort**: S
**Dependencies**: None

**Description**:
Enhance reporting system to require users to select a specific reason when reporting reviews. This helps admins prioritize and understand report patterns.

**Acceptance Criteria**:
- [ ] Report modal/dialog with reason selection (required)
- [ ] Four report categories: "Offensive", "Attacking a person", "Untrue", "Not relevant"
- [ ] Store report reason in database
- [ ] Display report reasons to admins in moderation panel
- [ ] Group reported reviews by reason type
- [ ] Update `reviews` table to track report reasons (array or separate table)

**Technical Notes**:
- Add `report_reasons` JSON column to reviews table OR create `review_reports` table
- Report reasons table: `id`, `review_id`, `session_id`, `reason`, `created_at`
- Update `/api/reportReview` endpoint to accept reason parameter
- Show reason breakdown in admin panel (e.g., "3 reports: 2x Offensive, 1x Untrue")

**Related Files**:
- `backend/sql_statements/07_report_reasons.sql` - Migration
- `backend/db.py` - Update `report_review()` function
- `backend/app.py` - Update `/api/reportReview` endpoint
- `frontend/src/pages/module/ModulePage.vue` - Add report modal
- `frontend/src/pages/admin/AdminPage.vue` - Display reasons

**Testing**:
- [ ] Cannot report without selecting a reason
- [ ] Report reasons stored correctly
- [ ] Admin can see breakdown of report reasons
- [ ] Multiple reports with different reasons tracked

---

### [MYM-009] AI-Generated Review Summaries
**Type**: Feature
**Priority**: P2 (Medium)
**Status**: Backlog
**Estimated Effort**: L
**Dependencies**: None

**Description**:
Generate AI-powered summaries of all reviews for each module to help students quickly understand general trends. Summaries are cached and only regenerated when there are new reviews (with 30-minute cooldown).

**Acceptance Criteria**:
- [ ] Generate short, factual bullet-point summaries using Google Gemini
- [ ] Cache summaries in database with timestamp
- [ ] Regenerate only when: (1) new reviews exist AND (2) 30+ mins since last generation
- [ ] Non-blocking: summary loads asynchronously, doesn't delay page
- [ ] Display loading skeleton while generating
- [ ] Fallback if AI fails: show message or skip summary
- [ ] Summary focuses on: common themes, workload, difficulty, teaching quality
- [ ] Maximum 3-5 bullet points

**Technical Notes**:
- Add `module_summaries` table: `module_id`, `summary`, `generated_at`, `review_count_at_generation`
- Backend checks if summary needs refresh before serving module page
- Generate in background task (or accept slight delay on first load)
- Use prompt like: "Summarize these module reviews in 3-5 factual bullet points covering workload, difficulty, and teaching quality"
- Consider rate limits on Google Gemini API

**Related Files**:
- `backend/sql_statements/08_module_summaries.sql` - Migration
- `backend/lib.py` - Add `generate_module_summary()` function
- `backend/db.py` - Add summary management functions
- `backend/app.py` - Add `/api/getModuleSummary/{module_id}` endpoint
- `frontend/src/pages/module/ModulePage.vue` - Display summary section

**Testing**:
- [ ] Summary generates correctly for modules with reviews
- [ ] Summary doesn't regenerate within 30 minutes
- [ ] Summary regenerates when new reviews added (after 30 min cooldown)
- [ ] Page loads even if summary generation fails
- [ ] Summary is factual and helpful

**Performance**:
- Consider caching strategy (Redis or PostgreSQL)
- Background job queue for generation (optional)

---

### [MYM-010] Admin Review Management Interface
**Type**: Feature
**Priority**: P1 (High)
**Status**: Backlog
**Estimated Effort**: M
**Dependencies**: [MYM-001]

**Description**:
Create a comprehensive admin interface for searching, filtering, and managing ALL reviews (not just pending/reported). Admins should be able to find and manipulate any review with a common, reusable component.

**Acceptance Criteria**:
- [ ] Admin page showing all reviews (paginated)
- [ ] Search reviews by: module code, module name, review text, date range
- [ ] Filter by: status (published/pending/rejected), rating, academic year
- [ ] Sort by: date, rating, report count, likes/dislikes
- [ ] Reusable `ReviewCard` component for displaying reviews
- [ ] Actions on each review: Accept, Reject, Delete (with confirmation)
- [ ] Edit review text inline (admin override)
- [ ] View full review history/audit trail
- [ ] Bulk actions: select multiple reviews, accept/reject all

**Technical Notes**:
- Create `frontend/src/components/admin/ReviewCard.vue` - reusable component
- Use same component in pending, rejected, and all-reviews pages
- Add `/api/admin/allReviews` endpoint with search/filter parameters
- Consider full-text search on PostgreSQL (or use ILIKE for simplicity)
- Add audit trail when admin edits review content

**Related Files**:
- `frontend/src/components/admin/ReviewCard.vue` - New component
- `frontend/src/pages/admin/AllReviewsPage.vue` - New page
- `backend/app.py` - Add `/api/admin/allReviews` endpoint
- `backend/db.py` - Add `search_all_reviews()` function
- Update existing admin pages to use `ReviewCard` component

**Testing**:
- [ ] Search finds reviews correctly
- [ ] Filters work in combination
- [ ] Bulk actions work correctly
- [ ] Review edits are audited
- [ ] Pagination works smoothly

---

### [MYM-011] Admin Module Page with Review Freeze
**Type**: Feature
**Priority**: P2 (Medium)
**Status**: Backlog
**Estimated Effort**: M
**Dependencies**: [MYM-001], [MYM-010]

**Description**:
Create an admin-only version of the module page where admins can freeze reviews (prevent new submissions) and manipulate existing reviews in context.

**Acceptance Criteria**:
- [ ] Admin module page at `/admin/module/:code`
- [ ] Toggle to freeze/unfreeze reviews for specific module iteration
- [ ] Visual indicator when reviews are frozen
- [ ] All existing reviews displayed with admin controls inline
- [ ] Use `ReviewCard` component from [MYM-010]
- [ ] Quickly accept/reject/edit reviews without leaving page
- [ ] Show freeze status to users (e.g., "Reviews closed for this module")
- [ ] Frozen modules don't show review submission form

**Technical Notes**:
- Add `is_frozen` boolean to `module_iterations` table
- Add `/api/admin/freezeModule/{iteration_id}` endpoint
- Check freeze status in `/api/submitReview` endpoint
- Display freeze banner on public module page
- Admin module page combines public view with admin controls

**Related Files**:
- `backend/sql_statements/09_freeze_modules.sql` - Migration
- `backend/db.py` - Add freeze/unfreeze functions
- `backend/app.py` - Add freeze endpoints, check in submit
- `frontend/src/pages/admin/AdminModulePage.vue` - New component
- `frontend/src/pages/module/ModulePage.vue` - Show freeze status

**Testing**:
- [ ] Frozen modules reject new review submissions
- [ ] Freeze status displayed correctly to users
- [ ] Admin can unfreeze modules
- [ ] Admin controls work on admin module page

---

### [MYM-012] Site Information Pop-up
**Type**: Feature
**Priority**: P2 (Medium)
**Status**: Backlog
**Estimated Effort**: XS
**Dependencies**: [MYM-007]

**Description**:
Add an expandable/collapsible information pop-up on the main page that auto-expands on first visit (start of anonymous session) and can be manually toggled afterwards.

**Acceptance Criteria**:
- [ ] Pop-up component with expand/collapse button
- [ ] Auto-expands on first session visit (track in session storage)
- [ ] Contains placeholder "lorem ipsum" text (to be updated later)
- [ ] Stays collapsed on subsequent page loads
- [ ] Positioned unobtrusively (corner or bottom)
- [ ] Smooth expand/collapse animation
- [ ] "Don't show again" option (optional)

**Technical Notes**:
- Use localStorage or session storage to track if user has seen it
- Alternative: use anonymous session from [MYM-007]
- Position: fixed bottom-right or top-right corner
- Use Tailwind transitions for animation

**Related Files**:
- `frontend/src/components/InfoPopup.vue` - New component
- `frontend/src/pages/search/SearchPage.vue` - Add popup

**Testing**:
- [ ] Popup auto-expands on first visit
- [ ] Stays collapsed on subsequent visits
- [ ] Expand/collapse works smoothly
- [ ] Doesn't block important UI elements

---

### [MYM-013] Seasonal Easter Eggs on Logo
**Type**: Feature
**Priority**: P3 (Low)
**Status**: Backlog
**Estimated Effort**: S
**Dependencies**: None

**Description**:
Add seasonal/holiday easter eggs to the "O" in the site logo (e.g., Christmas ornament, Halloween pumpkin, graduation cap).

**Acceptance Criteria**:
- [ ] System detects current date/season
- [ ] Swaps "O" logo for themed version on special dates
- [ ] Predefined seasons/holidays: Christmas, Halloween, Easter, Graduation (June), etc.
- [ ] Themed SVG/images for each season
- [ ] Easy to add new seasonal themes
- [ ] Performance: minimal overhead, no API calls

**Technical Notes**:
- Create date-checking function in frontend
- Store themed "O" images in `/frontend/public/assets/seasonal/`
- Configuration file for dates: `{ start: '12-20', end: '12-26', image: 'christmas-o.svg' }`
- Component checks dates on mount
- Consider caching current theme in localStorage

**Related Files**:
- `frontend/src/components/Logo.vue` - Update logo component
- `frontend/src/utils/seasonalThemes.js` - Date configuration
- `frontend/public/assets/seasonal/` - Themed images

**Testing**:
- [ ] Correct theme displays for date ranges
- [ ] Falls back to normal "O" outside special dates
- [ ] Easy to add new themes
- [ ] No performance impact

**Future Ideas**:
- School-specific themes (e.g., university anniversary)
- User toggle to disable easter eggs

---

## 🐛 Bug Backlog

**✅ Recently Fixed:**
- [BUG-001] Review Submission Without Iteration - Backend validates iteration exists, frontend checks availableYears
- [BUG-002] Weighted Rating With No Reviews - Shows "No ratings yet" when weightedRating is null
- [BUG-004] Duplicate Lecturers in Search Results - Uses DISTINCT in lecturer query

---



### [BUG-003] Course Filter Doesn't Persist on Navigation
**Type**: Bug
**Priority**: P3 (Low)
**Status**: Backlog
**Estimated Effort**: XS
**Dependencies**: [MYM-007]

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

## 🔧 Technical Debt

**✅ Recently Completed:**
- [TECH-002] Add Proper Logging - `logger.py` implemented and used throughout application
- [TECH-003] Input Validation & Sanitization - `validators.py` with comprehensive validation, rate limiting enabled
- [TECH-004] Database Connection Pooling - Implemented in `db.py` with psycopg2.pool
- [TECH-005] Environment-Based Configuration - `config.py` with Development/Testing/Production configs
- [TECH-006] API Versioning - All routes use `/api/v1/` prefix
- [TECH-007] Unit Test Suite - Comprehensive test suite with 85%+ coverage (pytest + Vitest)
- [TECH-008] Error Handling Standardization - `errors.py` with standardized error handlers

---

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

**Last Updated**: 2025-12-11
**Maintained By**: Claude AI instances (manager & developer)
**Template Version**: 1.0

**Recent Updates (2025-12-11)**:
- Marked 3 bugs as fixed (BUG-001, BUG-002, BUG-004)
- Marked 7 technical debt items as completed (TECH-002 through TECH-008)
- All bugs were already resolved in previous work
- 85%+ test coverage achieved with comprehensive test suite
