/**
 * Minimal Main.js for Testing
 * ===========================
 * 
 * This is a minimal version of main.js to test if Vue.js
 * is working without the router and complex setup.
 * 
 * Author: Engineering Log Intelligence Team
 * Date: September 22, 2025
 */

import { createApp } from 'vue'
import App from './App.vue'

// Create Vue application
const app = createApp(App)

// Global error handler
app.config.errorHandler = (err, vm, info) => {
  console.error('Vue Error:', err)
  console.error('Component:', vm)
  console.error('Info:', info)
}

// Mount the application
app.mount('#app')

console.log('🚀 Minimal Vue.js app initialized!')
