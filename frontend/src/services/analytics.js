/**
 * Analytics Service
 * ================
 * 
 * This service handles communication with the analytics API.
 * It fetches data for the dashboard charts and metrics.
 * 
 * For beginners: This is like a helper that knows how to talk to the backend.
 * Instead of writing API calls in every component, we put them here and
 * reuse them throughout the application.
 * 
 * Author: Engineering Log Intelligence Team
 * Date: September 22, 2025
 */

import axios from 'axios'

// For beginners: This creates an axios instance with default settings
// It's like having a pre-configured HTTP client
const analyticsAPI = axios.create({
  baseURL: 'http://localhost:3000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

/**
 * Fetch dashboard analytics data
 * 
 * For beginners: This function calls our backend API to get chart data.
 * It returns a Promise, which is a way to handle asynchronous operations.
 * 
 * @returns {Promise<Object>} Analytics data for charts
 */
export const fetchDashboardAnalytics = async () => {
  try {
    console.log('Fetching dashboard analytics...')
    
    // For beginners: This makes an HTTP GET request to our API
    const response = await analyticsAPI.get('/api/dashboard_analytics')
    
    console.log('Analytics data received:', response.data)
    return response.data
    
  } catch (error) {
    console.log('API not available, using mock analytics data:', error.message)
    
    // For beginners: If the API fails, we return mock data so the app still works
    return getMockAnalyticsData()
  }
}

/**
 * Get mock analytics data for development/fallback
 * 
 * For beginners: This provides fake data when the real API isn't available.
 * It's useful for development and testing.
 */
const getMockAnalyticsData = () => {
  console.log('Using mock analytics data')
  
  return {
    logVolume: {
      labels: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00', '24:00'],
      datasets: [{
        label: 'Logs per hour',
        data: [1200, 1900, 3000, 5000, 4200, 3800, 2100],
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        tension: 0.4,
        fill: true
      }]
    },
    logDistribution: {
      labels: ['INFO', 'WARN', 'ERROR', 'DEBUG', 'FATAL'],
      datasets: [{
        data: [60, 25, 10, 4, 1],
        backgroundColor: [
          'rgb(34, 197, 94)',
          'rgb(245, 158, 11)',
          'rgb(239, 68, 68)',
          'rgb(107, 114, 128)',
          'rgb(147, 51, 234)'
        ],
        borderWidth: 2,
        borderColor: '#ffffff'
      }]
    },
    responseTime: {
      labels: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00', '24:00'],
      datasets: [{
        label: 'Average Response Time (ms)',
        data: [85, 92, 78, 105, 88, 95, 82],
        borderColor: 'rgb(16, 185, 129)',
        backgroundColor: 'rgba(16, 185, 129, 0.1)',
        tension: 0.4,
        fill: true
      }]
    },
    errorTypes: {
      labels: ['Database', 'Network', 'Authentication', 'Validation', 'System'],
      datasets: [{
        label: 'Error Count',
        data: [45, 32, 28, 15, 8],
        backgroundColor: [
          'rgba(239, 68, 68, 0.8)',
          'rgba(245, 158, 11, 0.8)',
          'rgba(147, 51, 234, 0.8)',
          'rgba(59, 130, 246, 0.8)',
          'rgba(16, 185, 129, 0.8)'
        ],
        borderColor: [
          'rgb(239, 68, 68)',
          'rgb(245, 158, 11)',
          'rgb(147, 51, 234)',
          'rgb(59, 130, 246)',
          'rgb(16, 185, 129)'
        ],
        borderWidth: 1
      }]
    },
    systemMetrics: {
      logsProcessed: 125000,
      activeAlerts: 3,
      responseTime: 89,
      systemHealth: 'Healthy',
      uptime: '99.9%',
      cpuUsage: 45,
      memoryUsage: 62,
      diskUsage: 78
    },
    timestamp: new Date().toISOString()
  }
}

/**
 * Fetch real-time metrics
 * 
 * For beginners: This could be used to get live updates of system metrics.
 * In a real application, this might use WebSockets for real-time updates.
 */
export const fetchRealTimeMetrics = async () => {
  try {
    const response = await analyticsAPI.get('/api/real_time_metrics')
    return response.data
  } catch (error) {
    console.error('Failed to fetch real-time metrics:', error)
    return null
  }
}

/**
 * Subscribe to real-time updates (placeholder for WebSocket implementation)
 * 
 * For beginners: This is where you would implement real-time updates
 * using WebSockets or Server-Sent Events.
 */
export const subscribeToRealTimeUpdates = (callback) => {
  // For beginners: This is a placeholder for real-time updates
  // In a real application, you would set up WebSocket connections here
  console.log('Real-time updates not implemented yet')
  
  // For now, we'll simulate updates with a timer
  const interval = setInterval(() => {
    callback(getMockAnalyticsData())
  }, 30000) // Update every 30 seconds
  
  // Return a function to unsubscribe
  return () => {
    clearInterval(interval)
  }
}
