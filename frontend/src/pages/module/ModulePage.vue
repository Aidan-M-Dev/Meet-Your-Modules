<template>
  <div class="page-container">
    <div class="content-container">
      <div class="header">
        <router-link to="/" class="back-link">← Back to Search</router-link>
      </div>

      <div v-if="loading" class="loading">Loading module {{ moduleCode }}...</div>
      <div v-else-if="error" class="error">{{ error }}</div>
      <div v-else-if="!currentYearData" class="no-data">
        No data available for this module.
      </div>
      <div v-else class="module-content">
      <!-- Module Header -->
      <div class="module-header">
        <div class="module-title">
          <span class="code">{{ moduleCode }}</span>
          <h1 class="name">{{ moduleName }}</h1>
        </div>
      </div>

      <!-- Current Info Section -->
      <div class="info-section">
        <h2>Current Information ({{ currentYearFormatted }})</h2>

        <div class="info-grid">
          <div class="info-item">
            <div class="info-label">Credits</div>
            <div class="info-value">{{ moduleCredits }}</div>
          </div>

          <div class="info-item" v-if="currentYearData.lecturers && currentYearData.lecturers.length > 0">
            <div class="info-label">Lecturer{{ currentYearData.lecturers.length > 1 ? 's' : '' }}</div>
            <div class="info-value">
              <router-link
                v-for="(lecturer, index) in currentYearData.lecturers"
                :key="lecturer.id"
                :to="`/?q=${encodeURIComponent(lecturer.name)}`"
                class="info-link"
              >
                {{ lecturer.name }}<span v-if="index < currentYearData.lecturers.length - 1">, </span>
              </router-link>
            </div>
          </div>
          <div class="info-item" v-else>
            <div class="info-label">Lecturers</div>
            <div class="info-value text-muted">Not available</div>
          </div>

          <div class="info-item" v-if="currentYearData.courses && currentYearData.courses.length > 0">
            <div class="info-label">Available To</div>
            <div class="info-value">
              <router-link
                v-for="(course, index) in currentYearData.courses"
                :key="course.id"
                :to="`/?course=${encodeURIComponent(course.title)}`"
                class="info-link"
              >
                {{ course.title }}<span v-if="index < currentYearData.courses.length - 1">, </span>
              </router-link>
            </div>
          </div>
        </div>
      </div>

      <!-- Reviews Section -->
      <div class="reviews-section">
        <h2>Reviews ({{ totalReviews }})</h2>
        <div v-if="weightedRating" class="average-rating">
          Average Rating: <strong>{{ weightedRating.toFixed(1) }}/5</strong>
        </div>

        <div v-if="totalReviews === 0" class="no-reviews">
          No reviews yet for this module.
        </div>

        <div v-else class="reviews-container custom-scrollbar">
          <div v-for="yearGroup in reviewsByYear" :key="yearGroup.year" class="year-group">
            <div class="year-header">
              <span class="year">{{ yearGroup.yearFormatted }}</span>
              <span v-if="yearGroup.lecturerChange" class="badge badge-purple">
                👤 Lecturer changed: {{ yearGroup.lecturerChange }}
              </span>
            </div>

            <div class="reviews-list">
              <div v-for="review in yearGroup.reviews" :key="review.id" class="review-card">
                <div class="review-header">
                  <div class="review-rating">
                    <span class="stars">{{ '★'.repeat(review.overall_rating) }}{{ '☆'.repeat(5 - review.overall_rating) }}</span>
                    <span class="rating-number">{{ review.overall_rating }}/5</span>
                  </div>
                  <div class="review-date">
                    {{ new Date(review.created_at).toLocaleDateString() }}
                  </div>
                </div>
                <p class="review-comment">{{ review.comment }}</p>
                <div class="review-footer">
                  <span class="likes">👍 {{ review.like_dislike }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import '/src/assets/shared.css'

export default {
  name: 'ModulePage',
  setup() {
    const route = useRoute()
    const moduleCode = ref(route.params.moduleName)
    const moduleData = ref(null)
    const moduleName = ref('')
    const moduleCredits = ref(0)
    const loading = ref(false)
    const error = ref(null)

    const formatAcademicYear = (year) => {
      const yearNum = parseInt(year)
      const nextYear = yearNum + 1
      return `${yearNum.toString().slice(-2)}/${nextYear.toString().slice(-2)}`
    }

    const currentYear = computed(() => {
      if (!moduleData.value?.yearsInfo) return null
      const years = Object.keys(moduleData.value.yearsInfo).sort((a, b) => b - a)
      return years[0] || null
    })

    const currentYearFormatted = computed(() => {
      return currentYear.value ? formatAcademicYear(currentYear.value) : null
    })

    const currentYearData = computed(() => {
      if (!currentYear.value || !moduleData.value?.yearsInfo) return null
      return moduleData.value.yearsInfo[currentYear.value]
    })

    const weightedRating = computed(() => {
      if (!moduleData.value?.yearsInfo) return null

      const years = Object.keys(moduleData.value.yearsInfo).sort((a, b) => b - a)
      let totalWeightedRating = 0
      let totalWeight = 0

      years.forEach((year, index) => {
        const weight = Math.pow(0.5, index) // Halve weight each year
        const reviews = moduleData.value.yearsInfo[year].reviews || []

        reviews.forEach(review => {
          totalWeightedRating += review.overall_rating * weight
          totalWeight += weight
        })
      })

      return totalWeight > 0 ? totalWeightedRating / totalWeight : null
    })

    const totalReviews = computed(() => {
      if (!moduleData.value?.yearsInfo) return 0
      return Object.values(moduleData.value.yearsInfo)
        .reduce((sum, yearData) => sum + (yearData.reviews?.length || 0), 0)
    })

    const reviewsByYear = computed(() => {
      if (!moduleData.value?.yearsInfo) return []

      const years = Object.keys(moduleData.value.yearsInfo).sort((a, b) => b - a)
      const result = []
      let previousLecturers = null

      years.forEach((year, index) => {
        const yearData = moduleData.value.yearsInfo[year]
        const reviews = yearData.reviews || []

        if (reviews.length === 0) return

        let lecturerChange = null
        const currentLecturers = yearData.lecturers?.map(l => l.name).sort().join(', ')

        if (index > 0 && previousLecturers && currentLecturers && previousLecturers !== currentLecturers) {
          lecturerChange = currentLecturers || 'Not available'
        }

        result.push({
          year,
          yearFormatted: formatAcademicYear(year),
          reviews,
          lecturerChange
        })

        previousLecturers = currentLecturers
      })

      return result
    })

    const fetchModuleData = async (code) => {
      loading.value = true
      error.value = null

      try {
        // First query: search for modules by code
        const searchResponse = await fetch(`/api/searchModulesByCode/${code}`)
        if (!searchResponse.ok) {
          throw new Error(`Failed to search modules: ${searchResponse.statusText}`)
        }
        const searchData = await searchResponse.json()
        const modules = searchData.modules || []

        if (modules.length === 0) {
          moduleData.value = null
          return
        }

        // Store module metadata
        const module = modules[0]
        moduleName.value = module.name
        moduleCredits.value = module.credits

        // Second query: get detailed module info by ID
        const detailsResponse = await fetch(`/api/getModuleInfo/${module.id}`)
        if (!detailsResponse.ok) {
          throw new Error(`Failed to fetch module details: ${detailsResponse.statusText}`)
        }

        const detailsData = await detailsResponse.json()
        moduleData.value = detailsData
      } catch (err) {
        error.value = err.message
        console.error('Error fetching module data:', err)
      } finally {
        loading.value = false
      }
    }

    // Fetch data when component mounts
    onMounted(() => {
      if (moduleCode.value) {
        fetchModuleData(moduleCode.value)
      }
    })

    // Watch for route parameter changes
    watch(() => route.params.moduleName, (newModuleCode) => {
      moduleCode.value = newModuleCode
      if (newModuleCode) {
        fetchModuleData(newModuleCode)
      }
    })

    return {
      moduleCode,
      moduleName,
      moduleCredits,
      moduleData,
      loading,
      error,
      currentYear,
      currentYearFormatted,
      currentYearData,
      weightedRating,
      totalReviews,
      reviewsByYear
    }
  }
}
</script>

<style scoped>
.header {
  margin-bottom: 2rem;
}

.no-data {
  text-align: center;
  padding: 4rem;
}

/* Module Header */
.module-header {
  margin-bottom: 2rem;
  padding: 2rem;
  background: white;
  border-radius: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.code {
  display: inline-block;
  font-size: 0.875rem;
  font-weight: 600;
  color: #3b82f6;
  letter-spacing: 0.05em;
  margin-bottom: 0.5rem;
}

.name {
  font-size: 2.25rem;
  font-weight: 700;
  color: #1f2937;
  margin: 0;
  line-height: 1.2;
}

/* Info Section */
.info-section {
  margin-bottom: 2rem;
  padding: 2rem;
  background: white;
  border-radius: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.info-section h2 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 1.5rem 0;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.info-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.info-value {
  font-size: 1.125rem;
  font-weight: 600;
  color: #1f2937;
}

.info-value.text-muted {
  font-style: italic;
}

/* Reviews Section */
.reviews-section {
  padding: 2rem;
  background: white;
  border-radius: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.reviews-section h2 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 0.5rem 0;
}

.average-rating {
  color: #6b7280;
  font-size: 0.95rem;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e5e7eb;
}

.average-rating strong {
  color: #1f2937;
  font-size: 1.1rem;
}

.no-reviews {
  text-align: center;
  padding: 3rem;
  color: #9ca3af;
  font-size: 1rem;
}

.reviews-container {
  max-height: 600px;
  overflow-y: auto;
  padding-right: 0.5rem;
}

.year-group {
  margin-bottom: 2rem;
}

.year-group:last-child {
  margin-bottom: 0;
}

.year-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
  padding-bottom: 0.75rem;
  border-bottom: 2px solid #e5e7eb;
}

.year {
  font-size: 1.25rem;
  font-weight: 700;
  color: #1f2937;
}


.reviews-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.review-card {
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 1.25rem;
  transition: box-shadow 0.2s;
}

.review-card:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.review-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.review-rating {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.stars {
  color: #fbbf24;
  font-size: 1rem;
}

.rating-number {
  font-size: 0.875rem;
  font-weight: 600;
  color: #6b7280;
}

.review-date {
  font-size: 0.875rem;
  color: #9ca3af;
}

.review-comment {
  color: #374151;
  line-height: 1.6;
  margin: 0 0 0.75rem 0;
}

.review-footer {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.likes {
  font-size: 0.875rem;
  color: #6b7280;
}

@media (max-width: 768px) {
  .info-grid {
    grid-template-columns: 1fr;
  }

  .name {
    font-size: 1.75rem;
  }
}
</style>
