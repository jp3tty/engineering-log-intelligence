<template>
  <div id="app" class="min-h-screen bg-gray-50">
    <!-- Simple test to see if Vue is working -->
    <div class="p-8">
      <h1 class="text-2xl font-bold text-gray-900 mb-4">
        🎉 Vue.js is working!
      </h1>
      <p class="text-gray-600 mb-4">
        If you can see this, the basic Vue.js setup is working.
      </p>
      
      <!-- Test router -->
      <div class="space-y-4">
        <router-link to="/login" class="btn btn-primary">
          Go to Login
        </router-link>
        <router-link to="/dashboard" class="btn btn-outline">
          Go to Dashboard
        </router-link>
      </div>
      
      <!-- Show current route -->
      <div class="mt-4 p-4 bg-gray-100 rounded">
        <p class="text-sm text-gray-600">
          Current route: {{ $route.path }}
        </p>
      </div>
    </div>
    
    <!-- Router View -->
    <router-view />
  </div>
</template>

<script>
/**
 * Simple App Component for Testing
 * ================================
 * 
 * This is a simplified version of App.vue to test if Vue.js
 * and the router are working properly.
 * 
 * Author: Engineering Log Intelligence Team
 * Date: September 22, 2025
 */

export default {
  name: 'App',
  setup() {
    console.log('✅ Simple App component loaded')
    return {}
  }
}
</script>

<style>
/* Basic styles */
.btn {
  @apply px-4 py-2 rounded font-medium inline-block;
}

.btn-primary {
  @apply bg-blue-600 text-white hover:bg-blue-700;
}

.btn-outline {
  @apply border border-gray-300 text-gray-700 hover:bg-gray-50;
}
</style>
