import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import ModulePage from '../pages/module/ModulePage.vue'

// Mock fetch and alert
global.fetch = vi.fn()
global.alert = vi.fn()
global.confirm = vi.fn()

const createMockRouter = (initialRoute = '/module/1') => {
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/', component: { template: '<div>Home</div>' } },
      { path: '/module/:moduleId', component: ModulePage },
    ],
  })
  router.push(initialRoute)
  return router
}

const mockModuleData = {
  module: {
    id: 1,
    code: 'COMP1001',
    name: 'Programming I',
    credits: 20,
  },
  yearsInfo: {
    2024: {
      iteration_id: 1,
      lecturers: [
        { id: 1, name: 'Dr. Smith' },
        { id: 2, name: 'Prof. Jones' },
      ],
      courses: [
        { id: 1, title: 'Computer Science' },
      ],
      reviews: [
        {
          id: 1,
          overall_rating: 5,
          comment: 'Great module!',
          created_at: '2024-01-15T10:00:00Z',
          like_dislike: 10,
        },
        {
          id: 2,
          overall_rating: 4,
          comment: 'Very good but challenging',
          created_at: '2024-02-20T14:30:00Z',
          like_dislike: 5,
        },
      ],
    },
    2023: {
      iteration_id: 2,
      lecturers: [
        { id: 3, name: 'Dr. Brown' },
      ],
      courses: [
        { id: 1, title: 'Computer Science' },
      ],
      reviews: [
        {
          id: 3,
          overall_rating: 3,
          comment: 'Decent module',
          created_at: '2023-03-10T09:00:00Z',
          like_dislike: 2,
        },
      ],
    },
  },
}

describe('ModulePage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    fetch.mockReset()
    alert.mockReset()
    confirm.mockReset()
  })

  describe('Component Mounting and Initial Load', () => {
    it('should render loading state initially', async () => {
      const router = createMockRouter('/module/1')
      await router.isReady()

      const resolvePromise = new Promise(() => {}) // Never resolves

      fetch.mockReturnValueOnce(resolvePromise)

      const wrapper = mount(ModulePage, {
        global: {
          plugins: [router],
        },
      })

      await wrapper.vm.$nextTick()

      expect(wrapper.find('.loading').exists()).toBe(true)
      expect(wrapper.find('.loading').text()).toBe('Loading module...')
    })

    it('should fetch and display module data', async () => {
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockModuleData,
      })

      const router = createMockRouter('/module/1')
      await router.isReady()

      const wrapper = mount(ModulePage, {
        global: {
          plugins: [router],
        },
      })

      await flushPromises()

      expect(fetch).toHaveBeenCalledWith('/api/getModuleInfo/1')
      expect(wrapper.find('.code').text()).toBe('COMP1001')
      expect(wrapper.find('.name').text()).toBe('Programming I')
      expect(wrapper.text()).toContain('20')
    })

    it('should display error message on fetch failure', async () => {
      fetch.mockResolvedValueOnce({
        ok: false,
        statusText: 'Not Found',
      })

      const router = createMockRouter('/module/999')
      await router.isReady()

      const wrapper = mount(ModulePage, {
        global: {
          plugins: [router],
        },
      })

      await flushPromises()

      expect(wrapper.find('.error').exists()).toBe(true)
      expect(wrapper.find('.error').text()).toContain('Failed to fetch module details')
    })

    it('should display no data message when module has no data', async () => {
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ module: null }),
      })

      const router = createMockRouter('/module/1')
      await router.isReady()

      const wrapper = mount(ModulePage, {
        global: {
          plugins: [router],
        },
      })

      await flushPromises()

      expect(wrapper.find('.no-data').exists()).toBe(true)
      expect(wrapper.find('.no-data').text()).toBe('No data available for this module.')
    })

    it('should have a back link to search', async () => {
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockModuleData,
      })

      const router = createMockRouter('/module/1')
      await router.isReady()

      const wrapper = mount(ModulePage, {
        global: {
          plugins: [router],
        },
      })

      await flushPromises()

      const backLink = wrapper.find('.back-link')
      expect(backLink.exists()).toBe(true)
      expect(backLink.text()).toBe('← Back to Search')
      expect(backLink.attributes('href')).toBe('/')
    })
  })

  describe('Module Information Display', () => {
    it('should display current year information', async () => {
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockModuleData,
      })

      const router = createMockRouter('/module/1')
      await router.isReady()

      const wrapper = mount(ModulePage, {
        global: {
          plugins: [router],
        },
      })

      await flushPromises()

      expect(wrapper.text()).toContain('Current Information (24/25 AY)')
      expect(wrapper.text()).toContain('Credits')
      expect(wrapper.text()).toContain('20')
    })

    it('should display lecturers with links', async () => {
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockModuleData,
      })

      const router = createMockRouter('/module/1')
      await router.isReady()

      const wrapper = mount(ModulePage, {
        global: {
          plugins: [router],
        },
      })

      await flushPromises()

      expect(wrapper.text()).toContain('Lecturers')
      expect(wrapper.text()).toContain('Dr. Smith')
      expect(wrapper.text()).toContain('Prof. Jones')

      const lecturerLinks = wrapper.findAll('.info-link')
      expect(lecturerLinks.length).toBeGreaterThan(0)
    })

    it('should display courses with links', async () => {
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockModuleData,
      })

      const router = createMockRouter('/module/1')
      await router.isReady()

      const wrapper = mount(ModulePage, {
        global: {
          plugins: [router],
        },
      })

      await flushPromises()

      expect(wrapper.text()).toContain('Available To')
      expect(wrapper.text()).toContain('Computer Science')
    })

    it('should handle missing lecturers gracefully', async () => {
      const dataWithoutLecturers = {
        ...mockModuleData,
        yearsInfo: {
          2024: {
            ...mockModuleData.yearsInfo[2024],
            lecturers: [],
          },
        },
      }

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => dataWithoutLecturers,
      })

      const router = createMockRouter('/module/1')
      await router.isReady()

      const wrapper = mount(ModulePage, {
        global: {
          plugins: [router],
        },
      })

      await flushPromises()

      expect(wrapper.text()).toContain('Lecturers')
      expect(wrapper.text()).toContain('Not available')
    })
  })

  describe('Reviews Display', () => {
    it('should display review count', async () => {
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockModuleData,
      })

      const router = createMockRouter('/module/1')
      await router.isReady()

      const wrapper = mount(ModulePage, {
        global: {
          plugins: [router],
        },
      })

      await flushPromises()

      expect(wrapper.text()).toContain('Reviews (3)')
    })

    it('should display average rating', async () => {
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockModuleData,
      })

      const router = createMockRouter('/module/1')
      await router.isReady()

      const wrapper = mount(ModulePage, {
        global: {
          plugins: [router],
        },
      })

      await flushPromises()

      expect(wrapper.find('.average-rating').exists()).toBe(true)
      expect(wrapper.text()).toContain('Average Rating:')
    })

    it('should display reviews grouped by year', async () => {
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockModuleData,
      })

      const router = createMockRouter('/module/1')
      await router.isReady()

      const wrapper = mount(ModulePage, {
        global: {
          plugins: [router],
        },
      })

      await flushPromises()

      const yearGroups = wrapper.findAll('.year-group')
      expect(yearGroups).toHaveLength(2)

      expect(wrapper.text()).toContain('24/25 AY')
      expect(wrapper.text()).toContain('23/24 AY')
    })

    it('should display individual review details', async () => {
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockModuleData,
      })

      const router = createMockRouter('/module/1')
      await router.isReady()

      const wrapper = mount(ModulePage, {
        global: {
          plugins: [router],
        },
      })

      await flushPromises()

      expect(wrapper.text()).toContain('Great module!')
      expect(wrapper.text()).toContain('Very good but challenging')
      expect(wrapper.text()).toContain('Decent module')

      const reviewCards = wrapper.findAll('.review-card')
      expect(reviewCards.length).toBeGreaterThan(0)

      // Check star ratings
      const stars = wrapper.findAll('.stars')
      expect(stars.length).toBeGreaterThan(0)
    })

    it('should show lecturer change badge', async () => {
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockModuleData,
      })

      const router = createMockRouter('/module/1')
      await router.isReady()

      const wrapper = mount(ModulePage, {
        global: {
          plugins: [router],
        },
      })

      await flushPromises()

      const badges = wrapper.findAll('.badge-purple')
      expect(badges.length).toBeGreaterThan(0)
      expect(wrapper.text()).toContain('Lecturer(s) changed')
    })

    it('should display no reviews message when there are no reviews', async () => {
      const dataWithoutReviews = {
        ...mockModuleData,
        yearsInfo: {
          2024: {
            ...mockModuleData.yearsInfo[2024],
            reviews: [],
          },
        },
      }

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => dataWithoutReviews,
      })

      const router = createMockRouter('/module/1')
      await router.isReady()

      const wrapper = mount(ModulePage, {
        global: {
          plugins: [router],
        },
      })

      await flushPromises()

      expect(wrapper.find('.no-reviews').exists()).toBe(true)
      expect(wrapper.text()).toContain('No reviews yet for this module')
    })
  })

  describe('Review Actions', () => {
    it('should handle like button click', async () => {
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockModuleData,
      })

      const router = createMockRouter('/module/1')
      await router.isReady()

      const wrapper = mount(ModulePage, {
        global: {
          plugins: [router],
        },
      })

      await flushPromises()

      // Mock the like API call
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: true }),
      })

      // Mock refetch of module data
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockModuleData,
      })

      const likeBtn = wrapper.find('.like-btn')
      await likeBtn.trigger('click')

      await flushPromises()

      expect(fetch).toHaveBeenCalledWith('/api/likeReview/1/true', { method: 'GET' })
    })

    it('should handle report button click with confirmation', async () => {
      confirm.mockReturnValueOnce(true)

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockModuleData,
      })

      const router = createMockRouter('/module/1')
      await router.isReady()

      const wrapper = mount(ModulePage, {
        global: {
          plugins: [router],
        },
      })

      await flushPromises()

      // Mock the report API call
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: true }),
      })

      // Mock refetch of module data
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockModuleData,
      })

      const reportBtn = wrapper.find('.report-btn')
      await reportBtn.trigger('click')

      await flushPromises()

      expect(confirm).toHaveBeenCalledWith('Are you sure you want to report this review?')
      expect(fetch).toHaveBeenCalledWith('/api/reportReview/1', { method: 'GET' })
      expect(alert).toHaveBeenCalledWith('Review reported. Thank you for helping maintain quality.')
    })

    it('should not report when user cancels confirmation', async () => {
      confirm.mockReturnValueOnce(false)

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockModuleData,
      })

      const router = createMockRouter('/module/1')
      await router.isReady()

      const wrapper = mount(ModulePage, {
        global: {
          plugins: [router],
        },
      })

      await flushPromises()

      const initialFetchCount = fetch.mock.calls.length

      const reportBtn = wrapper.find('.report-btn')
      await reportBtn.trigger('click')

      expect(confirm).toHaveBeenCalled()
      expect(fetch.mock.calls.length).toBe(initialFetchCount) // No additional API calls
    })
  })

  describe('Review Form', () => {
    it('should show write review button', async () => {
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockModuleData,
      })

      const router = createMockRouter('/module/1')
      await router.isReady()

      const wrapper = mount(ModulePage, {
        global: {
          plugins: [router],
        },
      })

      await flushPromises()

      const writeBtn = wrapper.find('.write-review-section .btn-primary')
      expect(writeBtn.exists()).toBe(true)
      expect(writeBtn.text()).toContain('Write a Review')
    })

    it('should display review form when write button clicked', async () => {
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockModuleData,
      })

      const router = createMockRouter('/module/1')
      await router.isReady()

      const wrapper = mount(ModulePage, {
        global: {
          plugins: [router],
        },
      })

      await flushPromises()

      expect(wrapper.find('.review-form-section').exists()).toBe(false)

      await wrapper.find('.write-review-section .btn-primary').trigger('click')

      expect(wrapper.find('.review-form-section').exists()).toBe(true)
      expect(wrapper.find('#review-year').exists()).toBe(true)
      expect(wrapper.find('#review-comment').exists()).toBe(true)
    })

    it('should have available years in dropdown', async () => {
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockModuleData,
      })

      const router = createMockRouter('/module/1')
      await router.isReady()

      const wrapper = mount(ModulePage, {
        global: {
          plugins: [router],
        },
      })

      await flushPromises()

      await wrapper.find('.write-review-section .btn-primary').trigger('click')

      const yearSelect = wrapper.find('#review-year')
      const options = yearSelect.findAll('option')

      expect(options).toHaveLength(2)
      expect(options[0].text()).toBe('24/25 AY')
      expect(options[1].text()).toBe('23/24 AY')
    })

    it('should allow star rating selection', async () => {
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockModuleData,
      })

      const router = createMockRouter('/module/1')
      await router.isReady()

      const wrapper = mount(ModulePage, {
        global: {
          plugins: [router],
        },
      })

      await flushPromises()

      await wrapper.find('.write-review-section .btn-primary').trigger('click')

      const starButtons = wrapper.findAll('.star-btn')
      expect(starButtons).toHaveLength(5)

      await starButtons[2].trigger('click') // Click 3rd star

      expect(wrapper.vm.newReview.rating).toBe(3)
    })

    it('should submit review successfully', async () => {
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockModuleData,
      })

      const router = createMockRouter('/module/1')
      await router.isReady()

      const wrapper = mount(ModulePage, {
        global: {
          plugins: [router],
        },
      })

      await flushPromises()

      await wrapper.find('.write-review-section .btn-primary').trigger('click')

      // Fill in form
      await wrapper.find('#review-year').setValue('2024')
      await wrapper.find('#review-comment').setValue('This is a great module!')

      // Mock submit API call
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: true }),
      })

      // Mock refetch of module data
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockModuleData,
      })

      await wrapper.find('.review-form').trigger('submit')

      await flushPromises()

      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/submitReview/1'),
        expect.objectContaining({
          method: 'POST',
        })
      )
      expect(alert).toHaveBeenCalledWith('Review submitted successfully!')
      expect(wrapper.find('.review-form-section').exists()).toBe(false)
    })

    it('should validate review comment before submission', async () => {
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockModuleData,
      })

      const router = createMockRouter('/module/1')
      await router.isReady()

      const wrapper = mount(ModulePage, {
        global: {
          plugins: [router],
        },
      })

      await flushPromises()

      await wrapper.find('.write-review-section .btn-primary').trigger('click')

      // Try to submit without comment
      await wrapper.find('.review-form').trigger('submit')

      await flushPromises()

      expect(alert).toHaveBeenCalledWith('Please write a review comment')
    })

    it('should cancel review form', async () => {
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockModuleData,
      })

      const router = createMockRouter('/module/1')
      await router.isReady()

      const wrapper = mount(ModulePage, {
        global: {
          plugins: [router],
        },
      })

      await flushPromises()

      await wrapper.find('.write-review-section .btn-primary').trigger('click')

      expect(wrapper.find('.review-form-section').exists()).toBe(true)

      await wrapper.find('.btn-secondary').trigger('click')

      expect(wrapper.find('.review-form-section').exists()).toBe(false)
      expect(wrapper.vm.newReview.comment).toBe('')
    })

    it('should handle review submission error', async () => {
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockModuleData,
      })

      const router = createMockRouter('/module/1')
      await router.isReady()

      const wrapper = mount(ModulePage, {
        global: {
          plugins: [router],
        },
      })

      await flushPromises()

      await wrapper.find('.write-review-section .btn-primary').trigger('click')

      await wrapper.find('#review-year').setValue('2024')
      await wrapper.find('#review-comment').setValue('Test review')

      // Mock failed submit API call
      fetch.mockResolvedValueOnce({
        ok: false,
        json: async () => ({ error: 'Validation failed' }),
      })

      await wrapper.find('.review-form').trigger('submit')

      await flushPromises()

      expect(alert).toHaveBeenCalledWith('Validation failed')
    })

    it('should show notice when no years available for review', async () => {
      const dataWithoutYears = {
        module: mockModuleData.module,
        yearsInfo: {},
      }

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => dataWithoutYears,
      })

      const router = createMockRouter('/module/1')
      await router.isReady()

      const wrapper = mount(ModulePage, {
        global: {
          plugins: [router],
        },
      })

      await flushPromises()

      // When yearsInfo is empty, currentYearData will be null, triggering no-data message instead
      expect(wrapper.find('.no-data').exists()).toBe(true)
      expect(wrapper.text()).toContain('No data available for this module')
    })
  })

  describe('Route Changes', () => {
    it('should refetch data when route parameter changes', async () => {
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockModuleData,
      })

      const router = createMockRouter('/module/1')
      await router.isReady()

      const wrapper = mount(ModulePage, {
        global: {
          plugins: [router],
        },
      })

      await flushPromises()

      expect(fetch).toHaveBeenCalledWith('/api/getModuleInfo/1')

      // Change route
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ ...mockModuleData, module: { ...mockModuleData.module, id: 2 } }),
      })

      await router.push('/module/2')
      await flushPromises()

      expect(fetch).toHaveBeenCalledWith('/api/getModuleInfo/2')
    })
  })
})
