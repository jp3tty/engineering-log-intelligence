<template>
  <footer class="bg-white border-t border-gray-200 mt-auto">
    <div class="container-custom py-8">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-8">
        <!-- Brand Section -->
        <div class="col-span-1 md:col-span-2">
          <div class="flex items-center space-x-2 mb-4">
            <div class="w-8 h-8 bg-gradient-to-r from-primary-500 to-primary-700 rounded-lg flex items-center justify-center">
              <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <span class="text-xl font-bold text-gray-900">Log Intelligence</span>
          </div>
          <p class="text-gray-600 text-sm max-w-md">
            AI-powered log analysis platform that processes engineering logs from multiple sources, 
            identifies patterns, and provides actionable insights for system optimization.
          </p>
        </div>

        <!-- Quick Links -->
        <div>
          <h3 class="text-sm font-semibold text-gray-900 uppercase tracking-wider mb-4">Quick Links</h3>
          <ul class="space-y-2">
            <li>
              <router-link to="/dashboard" class="text-sm text-gray-600 hover:text-primary-600 transition-colors">
                Dashboard
              </router-link>
            </li>
            <li>
              <router-link to="/logs" class="text-sm text-gray-600 hover:text-primary-600 transition-colors">
                Log Analysis
              </router-link>
            </li>
            <li>
              <router-link to="/monitoring" class="text-sm text-gray-600 hover:text-primary-600 transition-colors">
                Monitoring
              </router-link>
            </li>
            <li>
              <router-link to="/settings" class="text-sm text-gray-600 hover:text-primary-600 transition-colors">
                Settings
              </router-link>
            </li>
          </ul>
        </div>

        <!-- System Status -->
        <div>
          <h3 class="text-sm font-semibold text-gray-900 uppercase tracking-wider mb-4">System Status</h3>
          <div class="space-y-2">
            <div class="flex items-center space-x-2">
              <div 
                class="status-indicator"
                :class="statusClass"
              ></div>
              <span class="text-sm text-gray-600">{{ systemStatus }}</span>
            </div>
            <p class="text-xs text-gray-500">
              Last updated: {{ lastUpdate }}
            </p>
          </div>
        </div>
      </div>

      <!-- Bottom Section -->
      <div class="mt-8 pt-8 border-t border-gray-200">
        <div class="flex flex-col md:flex-row justify-between items-center">
          <div class="text-sm text-gray-500">
            © {{ currentYear }} Engineering Log Intelligence. All rights reserved.
          </div>
          <div class="flex items-center space-x-6 mt-4 md:mt-0">
            <span class="text-sm text-gray-500">
              Version {{ appVersion }}
            </span>
            <span class="text-sm text-gray-500">
              Built with Vue.js & Vercel
            </span>
          </div>
        </div>
      </div>
    </div>
  </footer>
</template>

<script>
/**
 * App Footer Component
 * ===================
 * 
 * This component provides the footer for the application.
 * It includes brand information, quick links, and system status.
 * 
 * For beginners: This is the bottom section of our application
 * that appears on every page. It contains links and information.
 * 
 * Author: Engineering Log Intelligence Team
 * Date: September 22, 2025
 */

import { computed } from 'vue'
import { useSystemStore } from '@/stores/system'

export default {
  name: 'AppFooter',
  setup() {
    const systemStore = useSystemStore()

    // Computed properties
    const currentYear = computed(() => new Date().getFullYear())
    const appVersion = computed(() => '1.0.0')

    const systemStatus = computed(() => {
      if (systemStore.isHealthy) return 'All Systems Operational'
      if (systemStore.isDegraded) return 'Some Issues Detected'
      if (systemStore.isUnhealthy) return 'System Issues'
      return 'Status Unknown'
    })

    const statusClass = computed(() => {
      if (systemStore.isHealthy) return 'status-online'
      if (systemStore.isDegraded) return 'status-warning'
      if (systemStore.isUnhealthy) return 'status-error'
      return 'status-offline'
    })

    const lastUpdate = computed(() => {
      if (systemStore.lastUpdate) {
        return new Date(systemStore.lastUpdate).toLocaleTimeString()
      }
      return 'Never'
    })

    return {
      currentYear,
      appVersion,
      systemStatus,
      statusClass,
      lastUpdate,
    }
  },
}
</script>
