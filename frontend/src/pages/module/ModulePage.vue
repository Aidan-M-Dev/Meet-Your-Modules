<template>
  <div id="module-page">
    <div class="header">
      <router-link to="/" class="back-link">← Back to Search</router-link>
    </div>

    <div v-if="loading" class="loading">Loading module {{ moduleCode }}...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else-if="!currentYearData">
      <p class="no-data">No data available for this module.</p>
    </div>
    <div v-else class="module-content">
      <!-- Module Header -->
      <div class="module-header">
        <div class="module-title">
          <span class="code">{{ moduleCode }}</span>
          <h1 class="name">{{ moduleName }}</h1>
        </div>
        <div v-if="weightedRating" class="rating-badge">
          <div class="rating-value">{{ weightedRating.toFixed(1) }}</div>
          <div class="rating-stars">★★★★★</div>
          <div class="rating-label">Average Rating</div>
        </div>
      </div>

      <!-- Current Info Section -->
      <div class="info-section">
        <h2>Current Information ({{ currentYear }})</h2>

        <div class="info-grid">
          <div class="info-item">
            <div class="info-label">Credits</div>
            <div class="info-value">{{ moduleCredits }}</div>
          </div>

          <div class="info-item" v-if="currentYearData.lecturers && currentYearData.lecturers.length > 0">
            <div class="info-label">Lecturer{{ currentYearData.lecturers.length > 1 ? 's' : '' }}</div>
            <div class="info-value">
              {{ currentYearData.lecturers.map(l => l.name).join(', ') }}
            </div>
          </div>
          <div class="info-item" v-else>
            <div class="info-label">Lecturers</div>
            <div class="info-value text-muted">Not available</div>
          </div>

          <div class="info-item" v-if="currentYearData.courses && currentYearData.courses.length > 0">
            <div class="info-label">Available To</div>
            <div class="info-value">
              {{ currentYearData.courses.map(c => c.title).join(', ') }}
            </div>
          </div>
        </div>
      </div>

      <!-- Reviews Section -->
      <div class="reviews-section">
        <h2>Reviews ({{ totalReviews }})</h2>

        <div v-if="totalReviews === 0" class="no-reviews">
          No reviews yet for this module.
        </div>

        <div v-else class="reviews-container">
          <div v-for="yearGroup in reviewsByYear" :key="yearGroup.year" class="year-group">
            <div class="year-header">
              <span class="year">{{ yearGroup.year }}</span>
              <span v-if="yearGroup.lecturerChange" class="lecturer-change">
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
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'

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

    const currentYear = computed(() => {
      if (!moduleData.value?.yearsInfo) return null
      const years = Object.keys(moduleData.value.yearsInfo).sort((a, b) => b - a)
      return years[0] || null
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
      currentYearData,
      weightedRating,
      totalReviews,
      reviewsByYear
    }
  }
}
</script>

<style scoped>
#module-page {
  min-height: 100vh;
  background-color: #f9fafb;
  padding: 2rem 1rem;
}

.header {
  max-width: 1200px;
  margin: 0 auto 2rem;
}

.back-link {
  display: inline-flex;
  align-items: center;
  color: #3b82f6;
  text-decoration: none;
  font-size: 0.875rem;
  font-weight: 500;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  transition: background-color 0.2s;
}

.back-link:hover {
  background-color: #eff6ff;
}

.loading {
  text-align: center;
  padding: 4rem;
  color: #6b7280;
  font-size: 1.125rem;
}

.error {
  max-width: 1200px;
  margin: 0 auto;
  color: #dc2626;
  background-color: #fef2f2;
  border: 1px solid #fecaca;
  padding: 1.5rem;
  border-radius: 12px;
}

.no-data {
  text-align: center;
  padding: 4rem;
  color: #6b7280;
  font-size: 1.125rem;
}

.module-content {
  max-width: 1200px;
  margin: 0 auto;
}

/* Module Header */
.module-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 2rem;
  margin-bottom: 2rem;
  padding: 2rem;
  background: white;
  border-radius: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.module-title {
  flex: 1;
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

.rating-badge {
  text-align: center;
  padding: 1.5rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  color: white;
  min-width: 120px;
}

.rating-value {
  font-size: 2.5rem;
  font-weight: 700;
  line-height: 1;
  margin-bottom: 0.25rem;
}

.rating-stars {
  font-size: 1rem;
  margin-bottom: 0.25rem;
  opacity: 0.9;
}

.rating-label {
  font-size: 0.75rem;
  opacity: 0.9;
  text-transform: uppercase;
  letter-spacing: 0.05em;
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

.text-muted {
  color: #9ca3af;
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
  margin: 0 0 1.5rem 0;
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

.reviews-container::-webkit-scrollbar {
  width: 8px;
}

.reviews-container::-webkit-scrollbar-track {
  background: #f3f4f6;
  border-radius: 4px;
}

.reviews-container::-webkit-scrollbar-thumb {
  background: #d1d5db;
  border-radius: 4px;
}

.reviews-container::-webkit-scrollbar-thumb:hover {
  background: #9ca3af;
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

.lecturer-change {
  font-size: 0.875rem;
  color: #7c3aed;
  background: #f5f3ff;
  padding: 0.375rem 0.75rem;
  border-radius: 6px;
  font-weight: 500;
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
  .module-header {
    flex-direction: column;
  }

  .rating-badge {
    width: 100%;
  }

  .info-grid {
    grid-template-columns: 1fr;
  }

  .name {
    font-size: 1.75rem;
  }
}
</style>
