import { createRouter, createWebHistory } from 'vue-router'
import ModulePage from '../pages/module/ModulePage.vue'
import SearchPage from '../pages/search/SearchPage.vue'
import AdminPage from '../pages/admin/AdminPage.vue'

const routes = [
  {
    path: '/',
    name: 'search',
    component: SearchPage
  },
  {
    path: '/module/:moduleId',
    name: 'module',
    component: ModulePage,
    props: true
  },
  {
    path: '/admin',
    name: 'admin',
    component: AdminPage
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
