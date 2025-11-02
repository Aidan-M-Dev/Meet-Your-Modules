<template>
  <div class="page-container">
    <div class="search-container">
      <h1>Search Modules</h1>

      <div class="search-box">
        <input
          v-model="searchQuery"
          @input="handleSearch"
          type="text"
          placeholder="Search by module name or code..."
          class="input search-input"
          autofocus
        />
        <button v-if="searchQuery" @click="clearSearch" class="clear-button">
          ✕
        </button>
      </div>

      <div class="filters">
        <div class="filter-group">
          <label for="course-filter">Filter by Course:</label>
          <div class="filter-input-wrapper">
            <input
              id="course-filter"
              v-model="courseQuery"
              @input="applyFilters"
              @focus="courseInputFocused = true"
              @blur="handleCourseBlur"
              type="text"
              placeholder="Enter course name..."
              class="filter-input"
            />
            <div v-if="courseInputFocused && courseQuery && filteredCourses.length > 0" class="course-dropdown">
              <div
                v-for="course in filteredCourses.slice(0, 5)"
                :key="course.id"
                @mousedown.prevent="selectCourse(course.title)"
                class="course-option"
              >
                {{ course.title }}
              </div>
              <div v-if="filteredCourses.length > 5" class="course-more">
                +{{ filteredCourses.length - 5 }} more courses
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-if="loading" class="loading">
        Searching...
      </div>

      <div v-else-if="error" class="error">
        {{ error }}
      </div>

      <div v-else-if="(searchQuery || courseQuery) && filteredResults.length === 0 && allResults.length > 0" class="no-results">
        No modules match your filters. Try adjusting your search.
      </div>

      <div v-else-if="(searchQuery || courseQuery) && allResults.length === 0" class="no-results">
        <span v-if="searchQuery">No modules found matching "{{ searchQuery }}"</span>
        <span v-else>No modules found</span>
      </div>

      <div v-else-if="filteredResults.length > 0" class="results">
        <p class="results-count">
          Found {{ filteredResults.length }} module{{ filteredResults.length !== 1 ? 's' : '' }}
          <span v-if="filteredResults.length < allResults.length" class="filtered-count">
            (filtered from {{ allResults.length }})
          </span>
        </p>

        <div class="results-list">
          <router-link
            v-for="module in filteredResults"
            :key="module.id"
            :to="`/module/${module.id}`"
            class="module-card"
          >
            <div class="module-code">{{ module.code }}</div>
            <div class="module-name">{{ module.name }}</div>
            <div class="module-meta">
              <span class="module-credits">{{ module.credits }} credits</span>
              <span v-if="module.current_lecturers && module.current_lecturers.length > 0" class="module-lecturers">
                {{ module.current_lecturers.map(l => l.name).join(', ') }}
              </span>
            </div>
          </router-link>
        </div>
      </div>

      <div v-else class="search-prompt">
        <p>Enter a module name or code to search</p>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import '/src/assets/shared.css'

export default {
  name: 'SearchPage',
  setup() {
    const route = useRoute()
    const router = useRouter()
    const searchQuery = ref('')
    const allResults = ref([])
    const courses = ref([])
    const courseQuery = ref('')
    const courseInputFocused = ref(false)
    const loading = ref(false)
    const error = ref(null)
    let searchTimeout = null

    const filteredResults = computed(() => {
      let filtered = allResults.value

      // Filter by course name
      if (courseQuery.value.trim()) {
        const courseSearch = courseQuery.value.toLowerCase()
        filtered = filtered.filter(module =>
          module.current_courses &&
          module.current_courses.some(c =>
            c.title.toLowerCase().includes(courseSearch)
          )
        )
      }

      return filtered
    })

    const filteredCourses = computed(() => {
      if (!courseQuery.value.trim()) return []
      const search = courseQuery.value.toLowerCase()
      return courses.value.filter(course =>
        course.title.toLowerCase().includes(search)
      )
    })

    const fetchCourses = async () => {
      try {
        const response = await fetch('/api/courses')
        if (!response.ok) {
          throw new Error('Failed to fetch courses')
        }
        const data = await response.json()
        courses.value = data.courses || []
      } catch (err) {
        console.error('Error fetching courses:', err)
      }
    }

    const performSearch = async (query) => {
      // If neither search query nor course filter, clear results
      if (!query.trim() && !courseQuery.value.trim()) {
        allResults.value = []
        return
      }

      loading.value = true
      error.value = null

      try {
        // Use '*' as query if only filtering by course
        const searchQuery = query.trim() || '*'
        const response = await fetch(`/api/searchModules?q=${encodeURIComponent(searchQuery)}`)

        if (!response.ok) {
          throw new Error(`Search failed: ${response.statusText}`)
        }

        const data = await response.json()
        allResults.value = data.modules || []
      } catch (err) {
        error.value = err.message
        console.error('Search error:', err)
      } finally {
        loading.value = false
      }
    }

    const updateURL = (query) => {
      if (query.trim()) {
        router.push({ query: { q: query } })
      } else {
        router.push({ query: {} })
      }
    }

    const handleSearch = () => {
      // Debounce search - wait 300ms after user stops typing
      clearTimeout(searchTimeout)
      searchTimeout = setTimeout(() => {
        updateURL(searchQuery.value)
        performSearch(searchQuery.value)
      }, 300)
    }

    const applyFilters = () => {
      // Trigger search if course filter is being used
      if (courseQuery.value.trim() && !searchQuery.value.trim()) {
        performSearch('')
      }
    }

    const selectCourse = (courseTitle) => {
      courseQuery.value = courseTitle
      courseInputFocused.value = false
      applyFilters()
    }

    const handleCourseBlur = () => {
      // Delay to allow click event to fire first
      setTimeout(() => {
        courseInputFocused.value = false
      }, 200)
    }

    const clearSearch = () => {
      searchQuery.value = ''
      allResults.value = []
      courseQuery.value = ''
      error.value = null
      router.push({ query: {} })
    }

    // Search from URL on mount
    onMounted(async () => {
      await fetchCourses()

      const queryParam = route.query.q
      const courseParam = route.query.course

      if (courseParam) {
        courseQuery.value = courseParam
      }

      if (queryParam) {
        searchQuery.value = queryParam
        performSearch(queryParam)
      } else if (courseParam) {
        performSearch('')
      }
    })

    return {
      searchQuery,
      allResults,
      filteredResults,
      filteredCourses,
      courseQuery,
      courseInputFocused,
      loading,
      error,
      handleSearch,
      applyFilters,
      selectCourse,
      handleCourseBlur,
      clearSearch
    }
  }
}
</script>

<style scoped>
.search-container {
  max-width: 800px;
  margin: 0 auto;
}

h1 {
  font-size: 2.5rem;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 2rem;
  text-align: center;
}

.search-box {
  position: relative;
  margin-bottom: 1.5rem;
}

.search-input {
  padding-right: 3rem;
}

.clear-button {
  position: absolute;
  right: 1rem;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: #9ca3af;
  font-size: 1.5rem;
  cursor: pointer;
  padding: 0.5rem;
  line-height: 1;
  transition: color 0.2s;
}

.clear-button:hover {
  color: #6b7280;
}

.filters {
  margin-bottom: 2rem;
  padding: 1.25rem;
  background: white;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  width: 100%;
}

.filter-group label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #6b7280;
}

.filter-select,
.filter-input {
  padding: 0.625rem 0.875rem;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 0.95rem;
  background: white;
  transition: border-color 0.2s, box-shadow 0.2s;
  width: 100%;
  box-sizing: border-box;
}

.filter-select:focus,
.filter-input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.error {
  text-align: center;
}

.no-results {
  text-align: center;
  padding: 3rem;
  color: #6b7280;
  font-size: 1.125rem;
}

.search-prompt {
  text-align: center;
  padding: 4rem 2rem;
  color: #9ca3af;
  font-size: 1.125rem;
}

.results-count {
  color: #6b7280;
  margin-bottom: 1rem;
  font-size: 0.875rem;
}

.filtered-count {
  color: #9ca3af;
  font-size: 0.8rem;
}

.results-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.module-card {
  display: block;
  background: white;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  padding: 1.5rem;
  text-decoration: none;
  transition: all 0.2s;
}

.module-card:hover {
  border-color: #3b82f6;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.module-code {
  font-size: 0.875rem;
  font-weight: 600;
  color: #3b82f6;
  margin-bottom: 0.5rem;
  letter-spacing: 0.05em;
}

.module-name {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 0.5rem;
}

.module-meta {
  display: flex;
  gap: 1rem;
  align-items: center;
  flex-wrap: wrap;
}

.module-credits {
  font-size: 0.875rem;
  color: #6b7280;
}

.module-lecturers {
  font-size: 0.875rem;
  color: #7c3aed;
  font-style: italic;
}
</style>
