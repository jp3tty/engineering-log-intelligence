/**
 * Main Vue.js Application Entry Point
 * ==================================
 * 
 * This is the main entry point for our Vue.js frontend application.
 * It sets up the Vue app, routing, state management, and global configurations.
 * 
 * For beginners: This file is like the "main" function in other programming
 * languages - it's where our application starts and gets configured.
 * 
 * Author: Engineering Log Intelligence Team
 * Date: September 22, 2025
 */

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import App from './App.vue'

// Import global styles
import './assets/css/main.css'

// Create Vue application
const app = createApp(App)

// Configure Pinia for state management
const pinia = createPinia()
app.use(pinia)

// Configure Vue Router for navigation
app.use(router)

// Global error handler
app.config.errorHandler = (err, vm, info) => {
  console.error('Vue Error:', err)
  console.error('Component:', vm)
  console.error('Info:', info)
  
  // In production, you might want to send this to an error tracking service
  if (import.meta.env.PROD) {
    // Send to error tracking service (e.g., Sentry)
    console.log('Error would be sent to tracking service in production')
  }
}

// Global properties
app.config.globalProperties.$log = (message, ...args) => {
  if (import.meta.env.DEV) {
    console.log(`[${new Date().toISOString()}] ${message}`, ...args)
  }
}

// Mount the application
app.mount('#app')

// Development helpers
if (import.meta.env.DEV) {
  // Make Vue app available globally for debugging
  window.VueApp = app
  
  // Log successful initialization
  console.log('🚀 Engineering Log Intelligence Frontend initialized successfully!')
  console.log('📊 Available routes:', router.getRoutes().map(route => route.path))
  console.log('🏪 Available stores:', Object.keys(pinia.state.value))
}
