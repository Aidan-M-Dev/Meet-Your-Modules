<template>
  <div class="page-container">
    <div class="content-container">
      <div class="header">
        <router-link to="/" class="back-link">← Back to Search</router-link>
      </div>

      <div v-if="loading" class="loading">Loading module...</div>
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

          <div class="info-item" v-if="uniqueLecturers.length > 0">
            <div class="info-label">Lecturer{{ uniqueLecturers.length > 1 ? 's' : '' }}</div>
            <div class="info-value">
              <router-link
                v-for="(lecturer, index) in uniqueLecturers"
                :key="lecturer.id"
                :to="`/?q=${encodeURIComponent(lecturer.name)}`"
                class="info-link"
              >
                {{ lecturer.name }}<span v-if="index < uniqueLecturers.length - 1">, </span>
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

      <!-- Write Review Section -->
      <div class="write-review-section" v-if="!showReviewForm">
        <button @click="showReviewForm = true" class="btn-primary">
          ✍️ Write a Review
        </button>
      </div>

      <div class="review-form-section" v-if="showReviewForm">
        <h2>Write a Review</h2>
        <form @submit.prevent="submitReview" class="review-form">
          <div class="form-group">
            <label for="review-year">Academic Year</label>
            <select
              id="review-year"
              v-model="newReview.selectedYear"
              class="filter-select"
              required
            >
              <option v-for="year in availableYears" :key="year" :value="year">
                {{ formatAcademicYear(year) }}
              </option>
            </select>
          </div>

          <div class="form-group">
            <label>Rating</label>
            <div class="star-selector">
              <button
                v-for="star in 5"
                :key="star"
                type="button"
                @click="newReview.rating = star"
                class="star-btn"
                :class="{ active: star <= newReview.rating }"
              >
                {{ star <= newReview.rating ? '★' : '☆' }}
              </button>
            </div>
          </div>

          <div class="form-group">
            <label for="review-comment">Your Review</label>
            <textarea
              id="review-comment"
              v-model="newReview.comment"
              rows="5"
              placeholder="Share your experience with this module..."
              required
              class="review-textarea"
            ></textarea>
          </div>

          <div class="form-actions">
            <button type="submit" class="btn-primary" :disabled="submittingReview">
              {{ submittingReview ? 'Submitting...' : 'Submit Review' }}
            </button>
            <button type="button" @click="cancelReview" class="btn-secondary">
              Cancel
            </button>
          </div>
        </form>
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
                👤 Lecturer(s) changed: {{ yearGroup.lecturerChange }}
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
                  <button @click="likeReview(review.id)" class="review-action-btn like-btn">
                    👍 {{ review.like_dislike }}
                  </button>
                  <button @click="reportReview(review.id)" class="review-action-btn report-btn">
                    🚩 Report
                  </button>
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
    const moduleId = ref(route.params.moduleId)
    const moduleData = ref(null)
    const moduleCode = ref('')
    const moduleName = ref('')
    const moduleCredits = ref(0)
    const loading = ref(false)
    const error = ref(null)
    const showReviewForm = ref(false)
    const submittingReview = ref(false)
    const newReview = ref({
      selectedYear: null,
      rating: 5,
      comment: ''
    })

    const formatAcademicYear = (year) => {
      const yearNum = parseInt(year)
      const nextYear = yearNum + 1
      return `${yearNum.toString().slice(-2)}/${nextYear.toString().slice(-2)} AY`
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

    const uniqueLecturers = computed(() => {
      if (!currentYearData.value?.lecturers) return []

      // Deduplicate lecturers by ID
      const seen = new Set()
      return currentYearData.value.lecturers.filter(lecturer => {
        if (seen.has(lecturer.id)) {
          return false
        }
        seen.add(lecturer.id)
        return true
      })
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

    const availableYears = computed(() => {
      if (!moduleData.value?.yearsInfo) return []
      return Object.keys(moduleData.value.yearsInfo).sort((a, b) => b - a)
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
          lecturerChange = currentLecturers + " --> " + previousLecturers || 'Not available'
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

    const fetchModuleData = async (id) => {
      loading.value = true
      error.value = null

      try {
        // Get complete module info by ID
        const response = await fetch(`/api/getModuleInfo/${id}`)
        if (!response.ok) {
          throw new Error(`Failed to fetch module details: ${response.statusText}`)
        }

        const data = await response.json()

        if (!data.module) {
          moduleData.value = null
          return
        }

        // Store module metadata
        moduleCode.value = data.module.code
        moduleName.value = data.module.name
        moduleCredits.value = data.module.credits

        // Store years info
        moduleData.value = { yearsInfo: data.yearsInfo }
      } catch (err) {
        error.value = err.message
        console.error('Error fetching module data:', err)
      } finally {
        loading.value = false
      }
    }

    // Fetch data when component mounts
    onMounted(() => {
      if (moduleId.value) {
        fetchModuleData(moduleId.value)
      }
    })

    // Watch for route parameter changes
    watch(() => route.params.moduleId, (newModuleId) => {
      moduleId.value = newModuleId
      if (newModuleId) {
        fetchModuleData(newModuleId)
      }
    })

    const likeReview = async (reviewId) => {
      try {
        const response = await fetch(`/api/likeReview/${reviewId}/true`, {
          method: 'GET'
        })

        if (!response.ok) {
          throw new Error('Failed to like review')
        }

        // Refresh module data to get updated like count
        if (moduleId.value) {
          fetchModuleData(moduleId.value)
        }
      } catch (err) {
        console.error('Error liking review:', err)
        alert('Failed to like review')
      }
    }

    const reportReview = async (reviewId) => {
      if (!confirm('Are you sure you want to report this review?')) {
        return
      }

      try {
        const response = await fetch(`/api/reportReview/${reviewId}`, {
          method: 'GET'
        })

        if (!response.ok) {
          throw new Error('Failed to report review')
        }

        alert('Review reported. Thank you for helping maintain quality.')

        // Refresh module data
        if (moduleId.value) {
          fetchModuleData(moduleId.value)
        }
      } catch (err) {
        console.error('Error reporting review:', err)
        alert('Failed to report review')
      }
    }

    const submitReview = async () => {
      if (!newReview.value.comment.trim()) {
        alert('Please write a review comment')
        return
      }

      if (!newReview.value.selectedYear) {
        alert('Please select an academic year')
        return
      }

      const selectedYearData = moduleData.value?.yearsInfo[newReview.value.selectedYear]
      if (!selectedYearData?.iteration_id) {
        alert('Unable to submit review - module iteration not found')
        return
      }

      submittingReview.value = true

      try {
        const formData = new FormData()
        formData.append('reviewText', newReview.value.comment)

        const response = await fetch(
          `/api/submitReview/${selectedYearData.iteration_id}?overall_rating=${newReview.value.rating}`,
          {
            method: 'POST',
            body: formData
          }
        )

        if (!response.ok) {
          throw new Error('Failed to submit review')
        }

        alert('Review submitted successfully!')

        // Reset form
        newReview.value = {
          selectedYear: currentYear.value,
          rating: 5,
          comment: ''
        }
        showReviewForm.value = false

        // Refresh module data to show new review
        if (moduleId.value) {
          fetchModuleData(moduleId.value)
        }
      } catch (err) {
        console.error('Error submitting review:', err)
        alert('Failed to submit review. Please try again.')
      } finally {
        submittingReview.value = false
      }
    }

    const cancelReview = () => {
      newReview.value = {
        selectedYear: currentYear.value,
        rating: 5,
        comment: ''
      }
      showReviewForm.value = false
    }

    // Initialize selectedYear when form is opened
    watch(showReviewForm, (isOpen) => {
      if (isOpen && currentYear.value) {
        newReview.value.selectedYear = currentYear.value
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
      uniqueLecturers,
      weightedRating,
      totalReviews,
      availableYears,
      reviewsByYear,
      showReviewForm,
      submittingReview,
      newReview,
      formatAcademicYear,
      likeReview,
      reportReview,
      submitReview,
      cancelReview
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

@media (max-width: 768px) {
  .info-grid {
    grid-template-columns: 1fr;
  }

  .name {
    font-size: 1.75rem;
  }
}
</style>
