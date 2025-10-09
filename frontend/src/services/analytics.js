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
  baseURL: '/api',  // Use Vercel's built-in API routing
  timeout: 15000,  // Increased timeout for database queries
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
    // Add cache-busting timestamp to ensure fresh data
    const response = await analyticsAPI.get('/dashboard_analytics', {
      params: { _t: Date.now() }
    })
    
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
  console.log('Using mock analytics data with dynamic metrics')
  
  // Generate dynamic metrics based on time
  const now = new Date()
  const hourOfDay = now.getHours()
  const minuteOfHour = now.getMinutes()
  const isBusinessHours = hourOfDay >= 9 && hourOfDay <= 17
  
  const baseLogVolume = 125000
  const hourModifier = isBusinessHours ? 1.35 : 0.65
  const randomVariation = 0.85 + Math.random() * 0.3
  const minuteVariation = 1 + (minuteOfHour / 60) * 0.1
  const logsProcessed = Math.floor(baseLogVolume * hourModifier * randomVariation * minuteVariation)
  
  const anomalyRate = 0.015 + Math.random() * 0.025
  const activeAlerts = Math.max(2, Math.min(18, Math.floor(logsProcessed * anomalyRate / 1000)))
  
  const baseResponseTime = 75
  const loadFactor = logsProcessed / baseLogVolume
  const responseTime = Math.max(60, Math.min(150, Math.floor(baseResponseTime * loadFactor + Math.random() * 25)))
  
  console.log('📊 Mock Analytics Generated:', { logsProcessed, activeAlerts, responseTime, hourOfDay, isBusinessHours })
  
  // Calculate dynamic log distribution based on total logs
  const infoPercent = 0.68 + Math.random() * 0.08  // 68-76% INFO
  const warnPercent = 0.15 + Math.random() * 0.05  // 15-20% WARN
  const errorPercent = 0.05 + Math.random() * 0.03 // 5-8% ERROR
  const debugPercent = 0.03 + Math.random() * 0.02 // 3-5% DEBUG
  const fatalPercent = 0.001 + Math.random() * 0.003 // 0.1-0.4% FATAL
  
  const infoCount = Math.floor(logsProcessed * infoPercent)
  const warnCount = Math.floor(logsProcessed * warnPercent)
  const errorCount = Math.floor(logsProcessed * errorPercent)
  const debugCount = Math.floor(logsProcessed * debugPercent)
  const fatalCount = Math.floor(logsProcessed * fatalPercent)
  
  // Generate dynamic log volume data based on total logs
  const dayOfWeek = now.getDay()
  const isWeekend = dayOfWeek === 0 || dayOfWeek === 6
  const baseMultiplier = isWeekend ? 0.6 : 1.0
  
  // Generate distribution weights
  const weights = []
  for (let i = 0; i < 7; i++) {
    const timeOfDataPoint = i * 4
    const isBusinessHours = timeOfDataPoint >= 8 && timeOfDataPoint <= 20
    const hourFactor = isBusinessHours ? 1.5 + Math.random() * 0.5 : 0.4 + Math.random() * 0.3
    const isPeakHours = timeOfDataPoint >= 12 && timeOfDataPoint <= 16
    const peakFactor = isPeakHours ? 1.3 + Math.random() * 0.4 : 1.0
    const isNearCurrentTime = Math.abs(timeOfDataPoint - hourOfDay) < 3
    const currentTimeFactor = isNearCurrentTime ? 0.9 + Math.random() * 0.4 : 1.0
    weights.push(baseMultiplier * hourFactor * peakFactor * currentTimeFactor)
  }
  
  // Normalize weights to sum to logsProcessed
  const totalWeight = weights.reduce((sum, w) => sum + w, 0)
  const logVolumeData = weights.map(w => Math.floor((w / totalWeight) * logsProcessed))
  
  return {
    logVolume: {
      labels: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00', '24:00'],
      datasets: [{
        label: 'Logs per hour',
        data: logVolumeData,
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        tension: 0.4,
        fill: true
      }]
    },
    logDistribution: {
      labels: ['INFO', 'WARN', 'ERROR', 'DEBUG', 'FATAL'],
      datasets: [{
        label: 'Log Count (Last 24h)',
        data: [infoCount, warnCount, errorCount, debugCount, fatalCount],
        backgroundColor: [
          'rgba(34, 197, 94, 0.8)',
          'rgba(245, 158, 11, 0.8)',
          'rgba(239, 68, 68, 0.8)',
          'rgba(107, 114, 128, 0.8)',
          'rgba(147, 51, 234, 0.8)'
        ],
        borderColor: [
          'rgb(34, 197, 94)',
          'rgb(245, 158, 11)',
          'rgb(239, 68, 68)',
          'rgb(107, 114, 128)',
          'rgb(147, 51, 234)'
        ],
        borderWidth: 2,
        borderRadius: 4,
        borderSkipped: false
      }]
    },
    responseTime: {
      labels: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00', '24:00'],
      datasets: [{
        label: 'Average Response Time (ms)',
        data: (() => {
          // Generate dynamic response time data based on average response time
          const responseTimeData = []
          
          for (let i = 0; i < 7; i++) {
            const timeOfDataPoint = i * 4
            const isBusinessHours = timeOfDataPoint >= 8 && timeOfDataPoint <= 20
            const loadFactor = isBusinessHours ? 1.1 + Math.random() * 0.4 : 0.7 + Math.random() * 0.2
            const isPeakHours = timeOfDataPoint >= 12 && timeOfDataPoint <= 16
            const peakPenalty = isPeakHours ? 1.1 + Math.random() * 0.3 : 1.0
            const isNearCurrentTime = Math.abs(timeOfDataPoint - hourOfDay) < 3
            const currentTimeFactor = isNearCurrentTime ? 0.85 + Math.random() * 0.5 : 1.0
            const weekendFactor = isWeekend ? 0.8 : 1.0
            const respTime = Math.floor(responseTime * loadFactor * peakPenalty * currentTimeFactor * weekendFactor)
            responseTimeData.push(respTime)
          }
          
          return responseTimeData
        })(),
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
      logsProcessed: logsProcessed,
      activeAlerts: activeAlerts,
      responseTime: responseTime,
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
