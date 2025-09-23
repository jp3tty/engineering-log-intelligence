/**
 * Vue Router Configuration
 * =======================
 * 
 * This file configures the routing for our Vue.js application.
 * It defines all the different pages and how users navigate between them.
 * 
 * For beginners: Routing is like having different pages in a website.
 * When a user clicks a link or types a URL, the router decides which
 * page/component to show.
 * 
 * Author: Engineering Log Intelligence Team
 * Date: September 22, 2025
 */

import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// Import page components
import Dashboard from '@/views/Dashboard.vue'
import LogAnalysis from '@/views/LogAnalysis.vue'
import ABTesting from '@/views/ABTesting.vue'
import Monitoring from '@/views/Monitoring.vue'
import Settings from '@/views/Settings.vue'
import Login from '@/views/Login.vue'
import NotFound from '@/views/NotFound.vue'

// Define routes
const routes = [
  {
    path: '/',
    name: 'Home',
    redirect: '/dashboard',
    meta: {
      title: 'Home',
      requiresAuth: true,
    },
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: Dashboard,
    meta: {
      title: 'Dashboard',
      description: 'Overview of system health and log analysis',
      requiresAuth: true,
      icon: 'chart-bar',
    },
  },
  {
    path: '/logs',
    name: 'LogAnalysis',
    component: LogAnalysis,
    meta: {
      title: 'Log Analysis',
      description: 'Analyze and search through log entries',
      requiresAuth: true,
      icon: 'document-text',
    },
  },
  {
    path: '/ab-testing',
    name: 'ABTesting',
    component: ABTesting,
    meta: {
      title: 'A/B Testing',
      description: 'Manage and monitor A/B tests for ML models',
      requiresAuth: true,
      icon: 'beaker',
      roles: ['analyst', 'admin'],
    },
  },
  {
    path: '/monitoring',
    name: 'Monitoring',
    component: Monitoring,
    meta: {
      title: 'Monitoring',
      description: 'System monitoring and alerting',
      requiresAuth: true,
      icon: 'chart-pie',
    },
  },
  {
    path: '/settings',
    name: 'Settings',
    component: Settings,
    meta: {
      title: 'Settings',
      description: 'Application settings and configuration',
      requiresAuth: true,
      icon: 'cog',
    },
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: {
      title: 'Login',
      description: 'Sign in to your account',
      requiresAuth: false,
      hideForAuth: true, // Hide this route if user is already authenticated
    },
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: NotFound,
    meta: {
      title: 'Page Not Found',
      requiresAuth: false,
    },
  },
]

// Create router instance
const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    // Scroll to top when navigating to a new page
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  },
})

// Navigation guards
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  
  // Check if route requires authentication
  if (to.meta.requiresAuth) {
    // Check if user is authenticated
    if (!authStore.isAuthenticated) {
      // Redirect to login page
      next({
        name: 'Login',
        query: { redirect: to.fullPath },
      })
      return
    }
    
    // Check role-based access
    if (to.meta.roles && to.meta.roles.length > 0) {
      const userRole = authStore.user?.role
      if (!userRole || !to.meta.roles.includes(userRole)) {
        // User doesn't have required role
        next({
          name: 'Dashboard',
          query: { error: 'insufficient_permissions' },
        })
        return
      }
    }
  }
  
  // Check if route should be hidden for authenticated users
  if (to.meta.hideForAuth && authStore.isAuthenticated) {
    // Redirect authenticated users away from login page
    next({ name: 'Dashboard' })
    return
  }
  
  // Update page title
  if (to.meta.title) {
    document.title = `${to.meta.title} - Engineering Log Intelligence`
  }
  
  // Update meta description
  if (to.meta.description) {
    const metaDescription = document.querySelector('meta[name="description"]')
    if (metaDescription) {
      metaDescription.setAttribute('content', to.meta.description)
    }
  }
  
  next()
})

// After navigation
router.afterEach((to, from) => {
  // Track page views (in production, you might send this to analytics)
  if (import.meta.env.DEV) {
    console.log(`📄 Navigated to: ${to.name} (${to.path})`)
  }
  
  // Clear any previous error messages
  const errorParam = to.query.error
  if (errorParam) {
    // Handle specific error cases
    switch (errorParam) {
      case 'insufficient_permissions':
        console.warn('⚠️ Insufficient permissions for this page')
        break
      case 'session_expired':
        console.warn('⚠️ Session expired, please log in again')
        break
      default:
        console.warn(`⚠️ Unknown error: ${errorParam}`)
    }
  }
})

// Error handling
router.onError((error) => {
  console.error('🚨 Router error:', error)
  
  // In production, you might want to send this to an error tracking service
  if (import.meta.env.PROD) {
    // Send to error tracking service (e.g., Sentry)
    console.log('Router error would be sent to tracking service in production')
  }
})

export default router
