import { describe, it, expect, beforeEach } from 'vitest'
import { createRouter, createMemoryHistory } from 'vue-router'
import SearchPage from '../pages/search/SearchPage.vue'
import ModulePage from '../pages/module/ModulePage.vue'
import AdminPage from '../pages/admin/AdminPage.vue'

// Mock fetch for components that need it
global.fetch = () => Promise.resolve({
  ok: true,
  json: async () => ({ courses: [], modules: [] }),
})

const createTestRouter = () => {
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      {
        path: '/',
        name: 'search',
        component: SearchPage,
      },
      {
        path: '/module/:moduleId',
        name: 'module',
        component: ModulePage,
        props: true,
      },
      {
        path: '/admin',
        name: 'admin',
        component: AdminPage,
      },
    ],
  })
}

describe('Router Configuration', () => {
  let router

  beforeEach(() => {
    router = createTestRouter()
  })

  describe('Route Definitions', () => {
    it('should have search route at /', () => {
      const searchRoute = router.getRoutes().find(r => r.path === '/')
      expect(searchRoute).toBeDefined()
      expect(searchRoute.name).toBe('search')
      expect(searchRoute.components.default).toBe(SearchPage)
    })

    it('should have module route at /module/:moduleId', () => {
      const moduleRoute = router.getRoutes().find(r => r.path === '/module/:moduleId')
      expect(moduleRoute).toBeDefined()
      expect(moduleRoute.name).toBe('module')
      expect(moduleRoute.components.default).toBe(ModulePage)
    })

    it('should have admin route at /admin', () => {
      const adminRoute = router.getRoutes().find(r => r.path === '/admin')
      expect(adminRoute).toBeDefined()
      expect(adminRoute.name).toBe('admin')
      expect(adminRoute.components.default).toBe(AdminPage)
    })

    it('should have exactly 3 routes', () => {
      expect(router.getRoutes()).toHaveLength(3)
    })
  })

  describe('Route Props', () => {
    it('should pass props to module route', () => {
      const moduleRoute = router.getRoutes().find(r => r.path === '/module/:moduleId')
      expect(moduleRoute.props.default).toBe(true)
    })
  })

  describe('Navigation', () => {
    it('should navigate to search page', async () => {
      await router.push('/')
      await router.isReady()

      expect(router.currentRoute.value.name).toBe('search')
      expect(router.currentRoute.value.path).toBe('/')
    })

    it('should navigate to module page with parameter', async () => {
      await router.push('/module/123')
      await router.isReady()

      expect(router.currentRoute.value.name).toBe('module')
      expect(router.currentRoute.value.path).toBe('/module/123')
      expect(router.currentRoute.value.params.moduleId).toBe('123')
    })

    it('should navigate to admin page', async () => {
      await router.push('/admin')
      await router.isReady()

      expect(router.currentRoute.value.name).toBe('admin')
      expect(router.currentRoute.value.path).toBe('/admin')
    })

    it('should navigate between routes', async () => {
      await router.push('/')
      expect(router.currentRoute.value.name).toBe('search')

      await router.push('/module/456')
      expect(router.currentRoute.value.name).toBe('module')
      expect(router.currentRoute.value.params.moduleId).toBe('456')

      await router.push('/admin')
      expect(router.currentRoute.value.name).toBe('admin')

      await router.push('/')
      expect(router.currentRoute.value.name).toBe('search')
    })
  })

  describe('Route Parameters', () => {
    it('should handle numeric module IDs', async () => {
      await router.push('/module/123')
      await router.isReady()

      expect(router.currentRoute.value.params.moduleId).toBe('123')
    })

    it('should handle different module IDs', async () => {
      await router.push('/module/1')
      expect(router.currentRoute.value.params.moduleId).toBe('1')

      await router.push('/module/999')
      expect(router.currentRoute.value.params.moduleId).toBe('999')
    })
  })

  describe('Query Parameters', () => {
    it('should handle query parameters on search route', async () => {
      await router.push({ path: '/', query: { q: 'programming' } })
      await router.isReady()

      expect(router.currentRoute.value.query.q).toBe('programming')
    })

    it('should handle multiple query parameters', async () => {
      await router.push({ path: '/', query: { q: 'COMP', course: 'Computer Science' } })
      await router.isReady()

      expect(router.currentRoute.value.query.q).toBe('COMP')
      expect(router.currentRoute.value.query.course).toBe('Computer Science')
    })

    it('should preserve query parameters during navigation', async () => {
      await router.push({ path: '/', query: { q: 'test' } })
      expect(router.currentRoute.value.query.q).toBe('test')

      // Navigate away
      await router.push('/admin')
      expect(router.currentRoute.value.query.q).toBeUndefined()

      // Navigate back without query
      await router.push('/')
      expect(router.currentRoute.value.query.q).toBeUndefined()
    })
  })

  describe('Named Routes', () => {
    it('should navigate using route names', async () => {
      await router.push({ name: 'search' })
      expect(router.currentRoute.value.name).toBe('search')

      await router.push({ name: 'module', params: { moduleId: '789' } })
      expect(router.currentRoute.value.name).toBe('module')
      expect(router.currentRoute.value.params.moduleId).toBe('789')

      await router.push({ name: 'admin' })
      expect(router.currentRoute.value.name).toBe('admin')
    })
  })

  describe('History Mode', () => {
    it('should use memory history for testing', () => {
      expect(router.options.history).toBeDefined()
    })

    it('should support back navigation', async () => {
      const testRouter = createTestRouter()
      
      await testRouter.push('/')
      await testRouter.push('/module/123')
      await testRouter.push('/admin')

      expect(testRouter.currentRoute.value.path).toBe('/admin')

      // Use back() method
      testRouter.back()
      // Wait a bit for the navigation to complete
      await new Promise(resolve => setTimeout(resolve, 10))
      expect(testRouter.currentRoute.value.path).toBe('/module/123')

      testRouter.back()
      await new Promise(resolve => setTimeout(resolve, 10))
      expect(testRouter.currentRoute.value.path).toBe('/')
    })

    it('should support forward navigation', async () => {
      const testRouter = createTestRouter()
      
      await testRouter.push('/')
      await testRouter.push('/module/123')

      testRouter.back()
      await new Promise(resolve => setTimeout(resolve, 10))
      expect(testRouter.currentRoute.value.path).toBe('/')

      testRouter.forward()
      await new Promise(resolve => setTimeout(resolve, 10))
      expect(testRouter.currentRoute.value.path).toBe('/module/123')
    })
  })
})
