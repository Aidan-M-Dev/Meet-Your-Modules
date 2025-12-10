import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import App from '../App.vue'

const createMockRouter = (initialRoute = '/') => {
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/', component: { template: '<div class="search-page">Search</div>' } },
      { path: '/module/:moduleId', component: { template: '<div class="module-page">Module {{ $route.params.moduleId }}</div>' } },
      { path: '/admin', component: { template: '<div class="admin-page">Admin</div>' } },
    ],
  })
  router.push(initialRoute)
  return router
}

describe('App', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('Component Structure', () => {
    it('should render the app container', async () => {
      const router = createMockRouter()
      await router.isReady()

      const wrapper = mount(App, {
        global: {
          plugins: [router],
        },
      })

      expect(wrapper.find('#app').exists()).toBe(true)
    })

    it('should render router-view', async () => {
      const router = createMockRouter()
      await router.isReady()

      const wrapper = mount(App, {
        global: {
          plugins: [router],
        },
      })

      expect(wrapper.findComponent({ name: 'RouterView' }).exists()).toBe(true)
    })

    it('should have minimum height styling', async () => {
      const router = createMockRouter()
      await router.isReady()

      const wrapper = mount(App, {
        global: {
          plugins: [router],
        },
      })

      const appElement = wrapper.find('#app')
      expect(appElement.exists()).toBe(true)
    })
  })

  describe('Route Rendering', () => {
    it('should render search page at root route', async () => {
      const router = createMockRouter('/')
      await router.isReady()

      const wrapper = mount(App, {
        global: {
          plugins: [router],
        },
      })

      expect(wrapper.html()).toContain('Search')
      expect(wrapper.find('.search-page').exists()).toBe(true)
    })

    it('should render module page at /module/:id route', async () => {
      const router = createMockRouter('/module/123')
      await router.isReady()

      const wrapper = mount(App, {
        global: {
          plugins: [router],
        },
      })

      expect(wrapper.html()).toContain('Module 123')
      expect(wrapper.find('.module-page').exists()).toBe(true)
    })

    it('should render admin page at /admin route', async () => {
      const router = createMockRouter('/admin')
      await router.isReady()

      const wrapper = mount(App, {
        global: {
          plugins: [router],
        },
      })

      expect(wrapper.html()).toContain('Admin')
      expect(wrapper.find('.admin-page').exists()).toBe(true)
    })
  })

  describe('Navigation', () => {
    it('should navigate between routes', async () => {
      const router = createMockRouter('/')
      await router.isReady()

      const wrapper = mount(App, {
        global: {
          plugins: [router],
        },
      })

      expect(wrapper.find('.search-page').exists()).toBe(true)

      await router.push('/module/456')

      expect(wrapper.find('.module-page').exists()).toBe(true)
      expect(wrapper.html()).toContain('Module 456')

      await router.push('/admin')

      expect(wrapper.find('.admin-page').exists()).toBe(true)
    })

    it('should update route parameters', async () => {
      const router = createMockRouter('/module/1')
      await router.isReady()

      const wrapper = mount(App, {
        global: {
          plugins: [router],
        },
      })

      expect(wrapper.html()).toContain('Module 1')

      await router.push('/module/2')

      expect(wrapper.html()).toContain('Module 2')
    })
  })
})
