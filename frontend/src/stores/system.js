/**
 * System Store
 * ============
 * 
 * This store manages system-wide state like health status,
 * notifications, and global settings.
 * 
 * For beginners: This store handles things that affect the
 * entire application, like system health and notifications.
 * 
 * Author: Engineering Log Intelligence Team
 * Date: September 22, 2025
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'

export const useSystemStore = defineStore('system', () => {
  // State
  const systemHealth = ref({
    status: 'unknown',
    services: {},
    lastChecked: null,
  })
  const isLoading = ref(false)
  const error = ref(null)
  const lastUpdate = ref(null)

  // Getters
  const isHealthy = computed(() => systemHealth.value.status === 'healthy')
  const isDegraded = computed(() => systemHealth.value.status === 'degraded')
  const isUnhealthy = computed(() => systemHealth.value.status === 'unhealthy')
  const hasError = computed(() => !!error.value)

  // Actions
  const checkSystemHealth = async () => {
    try {
      isLoading.value = true
      error.value = null

      const response = await axios.get('/api/health/check')
      
      if (response.data) {
        systemHealth.value = {
          status: response.data.status || 'unknown',
          services: response.data.services || {},
          lastChecked: new Date().toISOString(),
        }
        lastUpdate.value = new Date()
        return { success: true, data: response.data }
      } else {
        throw new Error('Invalid health check response')
      }
    } catch (err) {
      const errorMessage = err.response?.data?.error || err.message || 'Health check failed'
      error.value = errorMessage
      systemHealth.value.status = 'unhealthy'
      return { success: false, error: errorMessage }
    } finally {
      isLoading.value = false
    }
  }

  const initializeSystem = async () => {
    try {
      // Check system health
      await checkSystemHealth()
      
      // Set up periodic health checks
      setInterval(checkSystemHealth, 30000) // Check every 30 seconds
      
      return true
    } catch (err) {
      console.error('System initialization failed:', err.message)
      return false
    }
  }

  const getServiceStatus = (serviceName) => {
    return systemHealth.value.services[serviceName] || { status: 'unknown' }
  }

  const getOverallStatus = () => {
    return {
      status: systemHealth.value.status,
      lastChecked: systemHealth.value.lastChecked,
      services: Object.keys(systemHealth.value.services).length,
    }
  }

  return {
    // State
    systemHealth,
    isLoading,
    error,
    lastUpdate,
    
    // Getters
    isHealthy,
    isDegraded,
    isUnhealthy,
    hasError,
    
    // Actions
    checkSystemHealth,
    initializeSystem,
    getServiceStatus,
    getOverallStatus,
  }
})
