<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Page Header -->
    <div class="bg-white shadow-sm border-b border-gray-200">
      <div class="container-custom py-6">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-2xl font-bold text-gray-900">Dashboard</h1>
            <p class="text-gray-600 mt-1">Overview of system health and log analysis</p>
          </div>
          <div class="flex items-center space-x-4">
            <button
              @click="refreshData"
              :disabled="isLoading"
              class="btn btn-outline"
            >
              <svg class="w-4 h-4 mr-2" :class="{ 'animate-spin': isLoading }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              {{ isLoading ? 'Refreshing...' : 'Refresh' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="container-custom py-8">
      <!-- System Status Cards -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div class="card">
          <div class="card-body">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <div class="w-8 h-8 bg-success-100 rounded-lg flex items-center justify-center">
                  <svg class="w-5 h-5 text-success-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
              </div>
              <div class="ml-4">
                <p class="text-sm font-medium text-gray-600">System Health</p>
                <p class="text-2xl font-semibold text-gray-900">{{ systemHealth.status || 'Unknown' }}</p>
              </div>
            </div>
          </div>
        </div>

        <div class="card">
          <div class="card-body">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <div class="w-8 h-8 bg-primary-100 rounded-lg flex items-center justify-center">
                  <svg class="w-5 h-5 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                </div>
              </div>
              <div class="ml-4">
                <p class="text-sm font-medium text-gray-600">Logs Processed</p>
                <p class="text-2xl font-semibold text-gray-900">{{ formatNumber(logsProcessed) }}</p>
              </div>
            </div>
          </div>
        </div>

        <div class="card">
          <div class="card-body">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <div class="w-8 h-8 bg-warning-100 rounded-lg flex items-center justify-center">
                  <svg class="w-5 h-5 text-warning-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
                  </svg>
                </div>
              </div>
              <div class="ml-4">
                <p class="text-sm font-medium text-gray-600">Active Alerts</p>
                <p class="text-2xl font-semibold text-gray-900">{{ activeAlerts }}</p>
              </div>
            </div>
          </div>
        </div>

        <div class="card">
          <div class="card-body">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <div class="w-8 h-8 bg-danger-100 rounded-lg flex items-center justify-center">
                  <svg class="w-5 h-5 text-danger-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                </div>
              </div>
              <div class="ml-4">
                <p class="text-sm font-medium text-gray-600">Response Time</p>
                <p class="text-2xl font-semibold text-gray-900">{{ responseTime }}ms</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Charts and Analytics -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        <!-- Log Volume Chart -->
        <div class="card">
          <div class="card-header">
            <h3 class="text-lg font-semibold text-gray-900">Log Volume (Last 24 Hours)</h3>
          </div>
          <div class="card-body">
            <div class="h-64 flex items-center justify-center bg-gray-50 rounded-lg">
              <div class="text-center">
                <svg class="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
                <p class="text-gray-500">Chart will be implemented with Chart.js</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Error Distribution -->
        <div class="card">
          <div class="card-header">
            <h3 class="text-lg font-semibold text-gray-900">Error Distribution</h3>
          </div>
          <div class="card-body">
            <div class="space-y-4">
              <div class="flex items-center justify-between">
                <span class="text-sm text-gray-600">ERROR</span>
                <div class="flex items-center space-x-2">
                  <div class="w-32 bg-gray-200 rounded-full h-2">
                    <div class="bg-danger-500 h-2 rounded-full" style="width: 15%"></div>
                  </div>
                  <span class="text-sm font-medium text-gray-900">15%</span>
                </div>
              </div>
              <div class="flex items-center justify-between">
                <span class="text-sm text-gray-600">WARN</span>
                <div class="flex items-center space-x-2">
                  <div class="w-32 bg-gray-200 rounded-full h-2">
                    <div class="bg-warning-500 h-2 rounded-full" style="width: 25%"></div>
                  </div>
                  <span class="text-sm font-medium text-gray-900">25%</span>
                </div>
              </div>
              <div class="flex items-center justify-between">
                <span class="text-sm text-gray-600">INFO</span>
                <div class="flex items-center space-x-2">
                  <div class="w-32 bg-gray-200 rounded-full h-2">
                    <div class="bg-success-500 h-2 rounded-full" style="width: 60%"></div>
                  </div>
                  <span class="text-sm font-medium text-gray-900">60%</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Recent Activity -->
      <div class="card">
        <div class="card-header">
          <h3 class="text-lg font-semibold text-gray-900">Recent Activity</h3>
        </div>
        <div class="card-body">
          <div class="space-y-4">
            <div v-for="activity in recentActivity" :key="activity.id" class="flex items-center space-x-4">
              <div class="flex-shrink-0">
                <div 
                  class="w-2 h-2 rounded-full"
                  :class="getActivityColor(activity.type)"
                ></div>
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-sm text-gray-900">{{ activity.message }}</p>
                <p class="text-xs text-gray-500">{{ formatTime(activity.timestamp) }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
/**
 * Dashboard View Component
 * =======================
 * 
 * This component displays the main dashboard with system overview,
 * metrics, charts, and recent activity.
 * 
 * For beginners: This is the main page users see when they log in.
 * It shows important information about the system at a glance.
 * 
 * Author: Engineering Log Intelligence Team
 * Date: September 22, 2025
 */

import { ref, computed, onMounted } from 'vue'
import { useSystemStore } from '@/stores/system'

export default {
  name: 'Dashboard',
  setup() {
    const systemStore = useSystemStore()

    // Reactive data
    const isLoading = ref(false)
    const logsProcessed = ref(125000)
    const activeAlerts = ref(3)
    const responseTime = ref(89)

    // Sample data for demonstration
    const recentActivity = ref([
      {
        id: 1,
        type: 'success',
        message: 'System health check completed successfully',
        timestamp: new Date(Date.now() - 5 * 60 * 1000),
      },
      {
        id: 2,
        type: 'warning',
        message: 'High CPU usage detected on server-01',
        timestamp: new Date(Date.now() - 15 * 60 * 1000),
      },
      {
        id: 3,
        type: 'info',
        message: 'New log batch processed: 1,250 entries',
        timestamp: new Date(Date.now() - 30 * 60 * 1000),
      },
      {
        id: 4,
        type: 'error',
        message: 'Database connection timeout occurred',
        timestamp: new Date(Date.now() - 45 * 60 * 1000),
      },
    ])

    // Computed properties
    const systemHealth = computed(() => systemStore.systemHealth)

    // Methods
    const refreshData = async () => {
      isLoading.value = true
      try {
        await systemStore.checkSystemHealth()
        // In a real app, you'd fetch other data here
        await new Promise(resolve => setTimeout(resolve, 1000)) // Simulate API call
      } catch (error) {
        console.error('Failed to refresh data:', error)
      } finally {
        isLoading.value = false
      }
    }

    const formatNumber = (num) => {
      return new Intl.NumberFormat().format(num)
    }

    const formatTime = (timestamp) => {
      const now = new Date()
      const diff = now - timestamp
      const minutes = Math.floor(diff / 60000)
      
      if (minutes < 1) return 'Just now'
      if (minutes < 60) return `${minutes}m ago`
      const hours = Math.floor(minutes / 60)
      if (hours < 24) return `${hours}h ago`
      const days = Math.floor(hours / 24)
      return `${days}d ago`
    }

    const getActivityColor = (type) => {
      switch (type) {
        case 'success': return 'bg-success-500'
        case 'warning': return 'bg-warning-500'
        case 'error': return 'bg-danger-500'
        default: return 'bg-gray-500'
      }
    }

    // Lifecycle
    onMounted(() => {
      refreshData()
    })

    return {
      // Data
      isLoading,
      logsProcessed,
      activeAlerts,
      responseTime,
      recentActivity,
      
      // Computed
      systemHealth,
      
      // Methods
      refreshData,
      formatNumber,
      formatTime,
      getActivityColor,
    }
  },
}
</script>
