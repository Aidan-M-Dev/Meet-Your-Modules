import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import SearchPage from '../pages/search/SearchPage.vue'

// Mock fetch
global.fetch = vi.fn()

const createMockRouter = (initialRoute = '/') => {
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/', component: { template: '<div>Home</div>' } },
      { path: '/module/:id', component: { template: '<div>Module</div>' } },
    ],
  })
  router.push(initialRoute)
  return router
}

describe('SearchPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    fetch.mockReset()
  })

  describe('Component Mounting', () => {
    it('should render the search page', async () => {
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ courses: [] }),
      })

      const router = createMockRouter()
      await router.isReady()

      const wrapper = mount(SearchPage, {
        global: {
          plugins: [router],
        },
      })

      expect(wrapper.find('h1').text()).toBe('Search Modules')
      expect(wrapper.find('.search-input').exists()).toBe(true)
    })

    it('should autofocus on search input', async () => {
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ courses: [] }),
      })

      const router = createMockRouter()
      await router.isReady()

      const wrapper = mount(SearchPage, {
        global: {
          plugins: [router],
        },
        attachTo: document.body,
      })

      await flushPromises()

      expect(wrapper.find('.search-input').attributes('autofocus')).toBeDefined()
      wrapper.unmount()
    })
  })

  describe('Initial Load', () => {
    it('should fetch courses on mount', async () => {
      const mockCourses = [
        { id: 1, title: 'Computer Science' },
        { id: 2, title: 'Mathematics' },
      ]

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ courses: mockCourses }),
      })

      const router = createMockRouter()
      await router.isReady()

      mount(SearchPage, {
        global: {
          plugins: [router],
        },
      })

      await flushPromises()

      expect(fetch).toHaveBeenCalledWith('/api/v1/courses')
    })

    it('should handle course fetch errors gracefully', async () => {
      const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {})

      fetch.mockRejectedValueOnce(new Error('Network error'))

      const router = createMockRouter()
      await router.isReady()

      const wrapper = mount(SearchPage, {
        global: {
          plugins: [router],
        },
      })

      await flushPromises()

      expect(consoleErrorSpy).toHaveBeenCalled()
      expect(wrapper.find('.error').exists()).toBe(false) // Should not show error for course fetch

      consoleErrorSpy.mockRestore()
    })

    it('should perform search from URL query parameter', async () => {
      const mockModules = [
        { id: 1, code: 'COMP1001', name: 'Programming', credits: 20, current_lecturers: [] },
      ]

      // First call for courses
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ courses: [] }),
      })

      // Second call for search
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ modules: mockModules }),
      })

      const router = createMockRouter('/?q=programming')
      await router.isReady()

      const wrapper = mount(SearchPage, {
        global: {
          plugins: [router],
        },
      })

      await flushPromises()

      expect(fetch).toHaveBeenCalledWith('/api/searchModules?q=programming')
      expect(wrapper.vm.searchQuery).toBe('programming')
    })
  })

  describe('Search Functionality', () => {
    it('should update search query on input', async () => {
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ courses: [] }),
      })

      const router = createMockRouter()
      await router.isReady()

      const wrapper = mount(SearchPage, {
        global: {
          plugins: [router],
        },
      })

      await flushPromises()

      const input = wrapper.find('.search-input')
      await input.setValue('COMP')

      expect(wrapper.vm.searchQuery).toBe('COMP')
    })

    it('should perform search with debouncing', async () => {
      vi.useFakeTimers()

      const mockModules = [
        { id: 1, code: 'COMP1001', name: 'Programming', credits: 20, current_lecturers: [] },
      ]

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ courses: [] }),
      })

      const router = createMockRouter()
      await router.isReady()

      const wrapper = mount(SearchPage, {
        global: {
          plugins: [router],
        },
      })

      await flushPromises()

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ modules: mockModules }),
      })

      const input = wrapper.find('.search-input')
      await input.setValue('COMP')

      // Should not search immediately
      expect(fetch).toHaveBeenCalledTimes(1) // Only courses fetch

      // Fast forward 300ms (debounce time)
      vi.advanceTimersByTime(300)
      await flushPromises()

      expect(fetch).toHaveBeenCalledWith('/api/searchModules?q=COMP')

      vi.useRealTimers()
    })

    it('should display search results', async () => {
      const mockModules = [
        {
          id: 1,
          code: 'COMP1001',
          name: 'Programming',
          credits: 20,
          current_lecturers: [{ name: 'Dr. Smith' }],
          current_courses: [],
        },
        {
          id: 2,
          code: 'COMP1002',
          name: 'Algorithms',
          credits: 20,
          current_lecturers: [],
          current_courses: [],
        },
      ]

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ courses: [] }),
      })

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ modules: mockModules }),
      })

      const router = createMockRouter('/?q=comp')
      await router.isReady()

      const wrapper = mount(SearchPage, {
        global: {
          plugins: [router],
        },
      })

      await flushPromises()

      expect(wrapper.find('.results-count').text()).toContain('Found 2 modules')
      expect(wrapper.findAll('.module-card')).toHaveLength(2)
      expect(wrapper.find('.module-code').text()).toBe('COMP1001')
      expect(wrapper.find('.module-name').text()).toBe('Programming')
    })

    it('should show loading state during search', async () => {
      vi.useFakeTimers()

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ courses: [] }),
      })

      const router = createMockRouter()
      await router.isReady()

      const wrapper = mount(SearchPage, {
        global: {
          plugins: [router],
        },
      })

      await flushPromises()

      // Create a promise we can control
      let resolveSearch
      const searchPromise = new Promise((resolve) => {
        resolveSearch = resolve
      })

      fetch.mockReturnValueOnce(searchPromise)

      // Trigger search via input
      await wrapper.find('.search-input').setValue('test')
      vi.advanceTimersByTime(300)
      await wrapper.vm.$nextTick()

      expect(wrapper.find('.loading').exists()).toBe(true)
      expect(wrapper.find('.loading').text()).toBe('Searching...')

      // Resolve the search
      resolveSearch({
        ok: true,
        json: async () => ({ modules: [] }),
      })

      await flushPromises()

      expect(wrapper.find('.loading').exists()).toBe(false)

      vi.useRealTimers()
    })

    it('should show no results message when no modules found', async () => {
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ courses: [] }),
      })

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ modules: [] }),
      })

      const router = createMockRouter('/?q=nonexistent')
      await router.isReady()

      const wrapper = mount(SearchPage, {
        global: {
          plugins: [router],
        },
      })

      await flushPromises()

      expect(wrapper.find('.no-results').exists()).toBe(true)
      expect(wrapper.find('.no-results').text()).toContain('No modules found matching "nonexistent"')
    })

    it('should display error on search failure', async () => {
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ courses: [] }),
      })

      fetch.mockResolvedValueOnce({
        ok: false,
        statusText: 'Internal Server Error',
      })

      const router = createMockRouter('/?q=test')
      await router.isReady()

      const wrapper = mount(SearchPage, {
        global: {
          plugins: [router],
        },
      })

      await flushPromises()

      expect(wrapper.find('.error').exists()).toBe(true)
      expect(wrapper.find('.error').text()).toContain('Search failed')
    })
  })

  describe('Clear Search', () => {
    it('should show clear button when search query exists', async () => {
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ courses: [] }),
      })

      const router = createMockRouter()
      await router.isReady()

      const wrapper = mount(SearchPage, {
        global: {
          plugins: [router],
        },
      })

      await flushPromises()

      expect(wrapper.find('.clear-button').exists()).toBe(false)

      await wrapper.find('.search-input').setValue('COMP')

      expect(wrapper.find('.clear-button').exists()).toBe(true)
    })

    it('should clear search when clear button clicked', async () => {
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ courses: [] }),
      })

      const router = createMockRouter()
      await router.isReady()

      const wrapper = mount(SearchPage, {
        global: {
          plugins: [router],
        },
      })

      await flushPromises()

      await wrapper.find('.search-input').setValue('COMP')
      wrapper.vm.allResults = [{ id: 1, code: 'COMP1001' }]

      await wrapper.find('.clear-button').trigger('click')

      expect(wrapper.vm.searchQuery).toBe('')
      expect(wrapper.vm.allResults).toEqual([])
      expect(wrapper.vm.courseQuery).toBe('')
      expect(wrapper.vm.error).toBeNull()
    })
  })

  describe('Course Filtering', () => {
    it('should display course filter input', async () => {
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ courses: [] }),
      })

      const router = createMockRouter()
      await router.isReady()

      const wrapper = mount(SearchPage, {
        global: {
          plugins: [router],
        },
      })

      await flushPromises()

      expect(wrapper.find('#course-filter').exists()).toBe(true)
      expect(wrapper.find('label[for="course-filter"]').text()).toBe('Filter by Course:')
    })

    it('should filter results by course', async () => {
      const mockCourses = [
        { id: 1, title: 'Computer Science' },
        { id: 2, title: 'Mathematics' },
      ]

      const mockModules = [
        {
          id: 1,
          code: 'COMP1001',
          name: 'Programming',
          credits: 20,
          current_lecturers: [],
          current_courses: [{ title: 'Computer Science' }],
        },
        {
          id: 2,
          code: 'MATH1001',
          name: 'Calculus',
          credits: 20,
          current_lecturers: [],
          current_courses: [{ title: 'Mathematics' }],
        },
      ]

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ courses: mockCourses }),
      })

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ modules: mockModules }),
      })

      const router = createMockRouter('/?q=*')
      await router.isReady()

      const wrapper = mount(SearchPage, {
        global: {
          plugins: [router],
        },
      })

      await flushPromises()

      expect(wrapper.vm.filteredResults).toHaveLength(2)

      await wrapper.find('#course-filter').setValue('Computer')

      expect(wrapper.vm.filteredResults).toHaveLength(1)
      expect(wrapper.vm.filteredResults[0].code).toBe('COMP1001')
    })

    it('should show course dropdown when focused and typing', async () => {
      const mockCourses = [
        { id: 1, title: 'Computer Science' },
        { id: 2, title: 'Computer Engineering' },
        { id: 3, title: 'Mathematics' },
      ]

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ courses: mockCourses }),
      })

      const router = createMockRouter()
      await router.isReady()

      const wrapper = mount(SearchPage, {
        global: {
          plugins: [router],
        },
      })

      await flushPromises()

      const courseInput = wrapper.find('#course-filter')
      await courseInput.trigger('focus')
      await courseInput.setValue('Computer')

      expect(wrapper.find('.course-dropdown').exists()).toBe(true)
      expect(wrapper.findAll('.course-option')).toHaveLength(2)
    })

    it('should select course from dropdown', async () => {
      vi.useFakeTimers()

      const mockCourses = [
        { id: 1, title: 'Computer Science' },
      ]

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ courses: mockCourses }),
      })

      const router = createMockRouter()
      await router.isReady()

      const wrapper = mount(SearchPage, {
        global: {
          plugins: [router],
        },
      })

      await flushPromises()

      const courseInput = wrapper.find('#course-filter')
      await courseInput.trigger('focus')
      await courseInput.setValue('Computer')

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ modules: [] }),
      })

      await wrapper.find('.course-option').trigger('mousedown')

      expect(wrapper.vm.courseQuery).toBe('Computer Science')
      expect(wrapper.vm.courseInputFocused).toBe(false)

      vi.useRealTimers()
    })

    it('should limit course dropdown to 5 items', async () => {
      const mockCourses = Array.from({ length: 10 }, (_, i) => ({
        id: i + 1,
        title: `Course ${i + 1}`,
      }))

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ courses: mockCourses }),
      })

      const router = createMockRouter()
      await router.isReady()

      const wrapper = mount(SearchPage, {
        global: {
          plugins: [router],
        },
      })

      await flushPromises()

      const courseInput = wrapper.find('#course-filter')
      await courseInput.trigger('focus')
      await courseInput.setValue('Course')

      expect(wrapper.findAll('.course-option')).toHaveLength(5)
      expect(wrapper.find('.course-more').exists()).toBe(true)
      expect(wrapper.find('.course-more').text()).toBe('+5 more courses')
    })
  })

  describe('Module Cards', () => {
    it('should display module information correctly', async () => {
      const mockModules = [
        {
          id: 1,
          code: 'COMP1001',
          name: 'Programming',
          credits: 20,
          current_lecturers: [{ name: 'Dr. Smith' }, { name: 'Prof. Jones' }],
          current_courses: [],
        },
      ]

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ courses: [] }),
      })

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ modules: mockModules }),
      })

      const router = createMockRouter('/?q=prog')
      await router.isReady()

      const wrapper = mount(SearchPage, {
        global: {
          plugins: [router],
        },
      })

      await flushPromises()

      const card = wrapper.find('.module-card')
      expect(card.find('.module-code').text()).toBe('COMP1001')
      expect(card.find('.module-name').text()).toBe('Programming')
      expect(card.find('.module-credits').text()).toBe('20 credits')
      expect(card.find('.module-lecturers').text()).toBe('Dr. Smith, Prof. Jones')
    })

    it('should link to module detail page', async () => {
      const mockModules = [
        {
          id: 123,
          code: 'COMP1001',
          name: 'Programming',
          credits: 20,
          current_lecturers: [],
          current_courses: [],
        },
      ]

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ courses: [] }),
      })

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ modules: mockModules }),
      })

      const router = createMockRouter('/?q=comp')
      await router.isReady()

      const wrapper = mount(SearchPage, {
        global: {
          plugins: [router],
        },
      })

      await flushPromises()

      const card = wrapper.find('.module-card')
      expect(card.attributes('href')).toBe('/module/123')
    })
  })

  describe('URL Updates', () => {
    it('should update URL with search query', async () => {
      vi.useFakeTimers()

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ courses: [] }),
      })

      const router = createMockRouter()
      await router.isReady()

      const wrapper = mount(SearchPage, {
        global: {
          plugins: [router],
        },
      })

      await flushPromises()

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ modules: [] }),
      })

      await wrapper.find('.search-input').setValue('COMP')

      vi.advanceTimersByTime(300)
      await flushPromises()

      expect(router.currentRoute.value.query.q).toBe('COMP')

      vi.useRealTimers()
    })

    it('should clear URL query when search is cleared', async () => {
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ courses: [] }),
      })

      const router = createMockRouter('/?q=test')
      await router.isReady()

      const wrapper = mount(SearchPage, {
        global: {
          plugins: [router],
        },
      })

      await flushPromises()

      wrapper.vm.clearSearch()
      await flushPromises()

      expect(router.currentRoute.value.query.q).toBeUndefined()
    })
  })
})
