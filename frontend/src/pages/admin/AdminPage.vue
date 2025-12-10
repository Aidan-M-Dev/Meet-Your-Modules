<template>
  <div class="page-container">
    <div class="content-container">
      <div class="header">
        <router-link to="/" class="back-link">← Back to Home</router-link>
        <h1>Admin Portal</h1>
      </div>

      <!-- Pending Reviews Section -->
      <div class="admin-card">
        <h2>Pending Reviews ({{ pendingReviews.length }})</h2>

        <div class="filter-group">
          <label for="pending-search">Search Pending Reviews: </label>
          <input
            id="pending-search"
            v-model="pendingSearchQuery"
            type="text"
            placeholder="Search by module code, name, or comment..."
            class="filter-input"
          />
        </div>

        <div v-if="loadingPending" class="loading">Loading pending reviews...</div>
        <div v-else-if="pendingError" class="error">{{ pendingError }}</div>
        <div v-else-if="filteredPendingReviews.length === 0 && pendingReviews.length === 0" class="no-content">
          No pending reviews to moderate
        </div>
        <div v-else-if="filteredPendingReviews.length === 0" class="no-content">
          No pending reviews match your search
        </div>
        <div v-else class="reviews-list">
          <div v-for="review in filteredPendingReviews" :key="review.id" class="review-item">
            <div class="review-header">
              <div class="review-module">
                <router-link :to="`/module/${review.module_id}`" class="module-link">
                  {{ review.module_code }} - {{ review.module_name }}
                </router-link>
                <span class="review-year">{{ formatAcademicYear(review.academic_year_start_year) }}</span>
              </div>
              <div class="review-rating">
                <span class="stars">{{ '★'.repeat(review.overall_rating) }}{{ '☆'.repeat(5 - review.overall_rating) }}</span>
                <span class="rating-number">{{ review.overall_rating }}/5</span>
              </div>
            </div>

            <p class="review-comment">{{ review.comment }}</p>

            <div class="review-meta">
              <span class="status-badge" :class="`status-${review.moderation_status}`">
                {{ review.moderation_status }}
              </span>
              <span class="review-date">{{ new Date(review.created_at).toLocaleString() }}</span>
            </div>

            <div class="review-actions">
              <button @click="acceptReview(review.id)" class="btn-accept" :disabled="processingReview === review.id">
                ✓ Accept
              </button>
              <button @click="rejectReview(review.id)" class="btn-reject" :disabled="processingReview === review.id">
                ✗ Reject
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Rejected Reviews Section -->
      <div class="admin-card">
        <h2>Rejected Reviews</h2>

        <div class="filter-group">
          <label for="rejected-search">Search Rejected Reviews: </label>
          <input
            id="rejected-search"
            v-model="rejectedSearchQuery"
            type="text"
            placeholder="Search by module code, name, or comment..."
            class="filter-input"
          />
        </div>

        <div v-if="loadingRejected" class="loading">Loading rejected reviews...</div>
        <div v-else-if="rejectedError" class="error">{{ rejectedError }}</div>
        <div v-else-if="filteredRejectedReviews.length === 0 && rejectedReviews.length === 0" class="no-content">
          No rejected reviews
        </div>
        <div v-else-if="filteredRejectedReviews.length === 0" class="no-content">
          No rejected reviews match your search
        </div>
        <div v-else class="reviews-list">
          <div v-for="review in filteredRejectedReviews" :key="review.id" class="review-item rejected">
            <div class="review-header">
              <div class="review-module">
                <router-link :to="`/module/${review.module_id}`" class="module-link">
                  {{ review.module_code }} - {{ review.module_name }}
                </router-link>
                <span class="review-year">{{ formatAcademicYear(review.academic_year_start_year) }}</span>
              </div>
              <div class="review-rating">
                <span class="stars">{{ '★'.repeat(review.overall_rating) }}{{ '☆'.repeat(5 - review.overall_rating) }}</span>
                <span class="rating-number">{{ review.overall_rating }}/5</span>
              </div>
            </div>

            <p class="review-comment">{{ review.comment }}</p>

            <div class="review-meta">
              <span class="review-date">{{ new Date(review.created_at).toLocaleString() }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- PDF Upload Section -->
      <div class="admin-card">
        <h2>Upload Programme Specification PDF</h2>
        <p class="section-description">
          Upload a programme specification PDF to automatically extract and add module information to the database.
        </p>

        <div class="upload-section">
          <div class="file-input-wrapper">
            <input
              type="file"
              id="pdf-file"
              ref="fileInput"
              @change="handleFileSelect"
              accept=".pdf"
              class="file-input"
            />
            <label for="pdf-file" class="file-label">
              <span v-if="!selectedFile">Choose PDF File</span>
              <span v-else>{{ selectedFile.name }}</span>
            </label>
          </div>

          <button
            @click="uploadPDF"
            :disabled="!selectedFile || uploadingPDF"
            class="btn-upload"
          >
            {{ uploadingPDF ? 'Uploading...' : 'Upload & Process PDF' }}
          </button>
        </div>

        <div v-if="uploadError" class="error upload-error">{{ uploadError }}</div>
        <div v-if="uploadSuccess" class="success upload-success">{{ uploadSuccess }}</div>

        <div v-if="uploadResult" class="upload-result">
          <h3>Parsed PDF Data</h3>
          <div class="result-summary">
            <p><strong>Programme:</strong> {{ uploadResult.programme?.title }}</p>
            <p><strong>Department:</strong> {{ uploadResult.department?.name }}</p>
            <p><strong>Academic Year:</strong> {{ uploadResult.programme?.academic_year }}</p>
            <div v-if="uploadResult.modules_by_year">
              <p><strong>Modules Found:</strong></p>
              <ul class="modules-list">
                <li v-for="(yearData, yearKey) in uploadResult.modules_by_year" :key="yearKey">
                  <strong>{{ yearKey }}:</strong> {{ yearData.modules?.length || 0 }} modules
                </li>
              </ul>
            </div>
          </div>
          <details class="raw-data">
            <summary>View Raw Data</summary>
            <pre>{{ JSON.stringify(uploadResult, null, 2) }}</pre>
          </details>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import '/src/assets/shared.css'

export default {
  name: 'AdminPage',
  setup() {
    const pendingReviews = ref([])
    const rejectedReviews = ref([])
    const loadingPending = ref(false)
    const loadingRejected = ref(false)
    const pendingError = ref(null)
    const rejectedError = ref(null)
    const processingReview = ref(null)
    const pendingSearchQuery = ref('')
    const rejectedSearchQuery = ref('')

    // PDF Upload state
    const selectedFile = ref(null)
    const fileInput = ref(null)
    const uploadingPDF = ref(false)
    const uploadError = ref(null)
    const uploadSuccess = ref(null)
    const uploadResult = ref(null)

    const formatAcademicYear = (year) => {
      const yearNum = parseInt(year)
      const nextYear = yearNum + 1
      return `${yearNum.toString().slice(-2)}/${nextYear.toString().slice(-2)} AY`
    }

    const filteredPendingReviews = computed(() => {
      if (!pendingSearchQuery.value.trim()) {
        return pendingReviews.value
      }

      const search = pendingSearchQuery.value.toLowerCase()
      return pendingReviews.value.filter(review =>
        review.module_code.toLowerCase().includes(search) ||
        review.module_name.toLowerCase().includes(search) ||
        review.comment.toLowerCase().includes(search)
      )
    })

    const filteredRejectedReviews = computed(() => {
      if (!rejectedSearchQuery.value.trim()) {
        return rejectedReviews.value
      }

      const search = rejectedSearchQuery.value.toLowerCase()
      return rejectedReviews.value.filter(review =>
        review.module_code.toLowerCase().includes(search) ||
        review.module_name.toLowerCase().includes(search) ||
        review.comment.toLowerCase().includes(search)
      )
    })

    const fetchPendingReviews = async () => {
      loadingPending.value = true
      pendingError.value = null

      try {
        const response = await fetch('/api/v1/admin/pendingReviews')
        if (!response.ok) {
          throw new Error('Failed to fetch pending reviews')
        }
        const data = await response.json()
        pendingReviews.value = data.reviews || []
      } catch (err) {
        pendingError.value = err.message
        console.error('Error fetching pending reviews:', err)
      } finally {
        loadingPending.value = false
      }
    }

    const fetchRejectedReviews = async () => {
      loadingRejected.value = true
      rejectedError.value = null

      try {
        const response = await fetch('/api/v1/admin/rejectedReviews')
        if (!response.ok) {
          throw new Error('Failed to fetch rejected reviews')
        }
        const data = await response.json()
        rejectedReviews.value = data.reviews || []
      } catch (err) {
        rejectedError.value = err.message
        console.error('Error fetching rejected reviews:', err)
      } finally {
        loadingRejected.value = false
      }
    }

    const acceptReview = async (reviewId) => {
      if (!confirm('Accept this review and publish it?')) {
        return
      }

      processingReview.value = reviewId

      try {
        const response = await fetch(`/api/admin/acceptReview/${reviewId}`, {
          method: 'POST'
        })

        if (!response.ok) {
          throw new Error('Failed to accept review')
        }

        // Remove from pending list
        pendingReviews.value = pendingReviews.value.filter(r => r.id !== reviewId)

        alert('Review accepted and published successfully!')
      } catch (err) {
        console.error('Error accepting review:', err)
        alert('Failed to accept review')
      } finally {
        processingReview.value = null
      }
    }

    const rejectReview = async (reviewId) => {
      if (!confirm('Reject this review? It will be moved to the rejected list.')) {
        return
      }

      processingReview.value = reviewId

      try {
        const response = await fetch(`/api/admin/rejectReview/${reviewId}`, {
          method: 'POST'
        })

        if (!response.ok) {
          throw new Error('Failed to reject review')
        }

        // Move from pending to rejected
        const review = pendingReviews.value.find(r => r.id === reviewId)
        if (review) {
          pendingReviews.value = pendingReviews.value.filter(r => r.id !== reviewId)
          rejectedReviews.value.unshift(review)
        }

        alert('Review rejected successfully!')
      } catch (err) {
        console.error('Error rejecting review:', err)
        alert('Failed to reject review')
      } finally {
        processingReview.value = null
      }
    }

    const handleFileSelect = (event) => {
      const file = event.target.files[0]
      if (file && file.type === 'application/pdf') {
        selectedFile.value = file
        uploadError.value = null
        uploadSuccess.value = null
        uploadResult.value = null
      } else {
        uploadError.value = 'Please select a valid PDF file'
        selectedFile.value = null
      }
    }

    const uploadPDF = async () => {
      if (!selectedFile.value) return

      uploadingPDF.value = true
      uploadError.value = null
      uploadSuccess.value = null
      uploadResult.value = null

      try {
        const formData = new FormData()
        formData.append('pdf', selectedFile.value)

        const response = await fetch('/api/admin/uploadProgrammeSpec', {
          method: 'POST',
          body: formData
        })

        if (!response.ok) {
          const errorData = await response.json()
          throw new Error(errorData.error || 'Failed to upload and process PDF')
        }

        const data = await response.json()
        uploadSuccess.value = 'PDF processed successfully!'
        uploadResult.value = data

        // Clear the file input
        selectedFile.value = null
        if (fileInput.value) {
          fileInput.value.value = ''
        }
      } catch (err) {
        uploadError.value = err.message
        console.error('Error uploading PDF:', err)
      } finally {
        uploadingPDF.value = false
      }
    }

    onMounted(() => {
      fetchPendingReviews()
      fetchRejectedReviews()
    })

    return {
      pendingReviews,
      rejectedReviews,
      loadingPending,
      loadingRejected,
      pendingError,
      rejectedError,
      processingReview,
      pendingSearchQuery,
      rejectedSearchQuery,
      filteredPendingReviews,
      filteredRejectedReviews,
      formatAcademicYear,
      acceptReview,
      rejectReview,
      // PDF Upload
      selectedFile,
      fileInput,
      uploadingPDF,
      uploadError,
      uploadSuccess,
      uploadResult,
      handleFileSelect,
      uploadPDF
    }
  }
}
</script>

<style scoped>
h1 {
  font-size: 2.5rem;
  font-weight: 700;
  color: #1f2937;
  margin: 1rem 0;
}

.filter-group {
  margin-bottom: 1.5rem;
}

.filter-group label {
  display: block;
  font-size: 0.875rem;
  font-weight: 600;
  color: #374151;
  margin-bottom: 0.5rem;
}

.filter-input {
  width: 100%;
  max-width: 700px;
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 1rem;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.filter-input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.section-description {
  color: #6b7280;
  margin-bottom: 1.5rem;
  line-height: 1.6;
}

.upload-section {
  display: flex;
  gap: 1rem;
  align-items: center;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.file-input-wrapper {
  flex: 1;
  min-width: 250px;
}

.file-input {
  display: none;
}

.file-label {
  display: block;
  padding: 0.75rem 1rem;
  background: white;
  border: 2px dashed #d1d5db;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  text-align: center;
  color: #6b7280;
}

.file-label:hover {
  border-color: #3b82f6;
  color: #3b82f6;
  background: #f9fafb;
}

.btn-upload {
  padding: 0.75rem 1.5rem;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-upload:hover:not(:disabled) {
  background: #2563eb;
}

.btn-upload:disabled {
  background: #9ca3af;
  cursor: not-allowed;
}

.upload-error {
  padding: 0.75rem;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 8px;
  color: #dc2626;
  margin-bottom: 1rem;
}

.upload-success {
  padding: 0.75rem;
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  border-radius: 8px;
  color: #16a34a;
  margin-bottom: 1rem;
}

.upload-result {
  margin-top: 1.5rem;
  padding: 1.5rem;
  background: #f9fafb;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
}

.upload-result h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 1rem 0;
}

.result-summary p {
  margin: 0.5rem 0;
  color: #374151;
}

.result-summary strong {
  color: #1f2937;
  font-weight: 600;
}

.modules-list {
  margin: 0.5rem 0 0 1.5rem;
  color: #374151;
}

.modules-list li {
  margin: 0.25rem 0;
}

.raw-data {
  margin-top: 1rem;
  padding: 1rem;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
}

.raw-data summary {
  cursor: pointer;
  font-weight: 600;
  color: #3b82f6;
  user-select: none;
}

.raw-data summary:hover {
  color: #2563eb;
}

.raw-data pre {
  margin-top: 1rem;
  padding: 1rem;
  background: #f9fafb;
  border-radius: 6px;
  overflow-x: auto;
  font-size: 0.875rem;
  line-height: 1.5;
  color: #374151;
}
</style>
