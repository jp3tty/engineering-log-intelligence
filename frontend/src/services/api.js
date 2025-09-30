/**
 * Mock API Service
 * ===============
 * 
 * This is a mock API service that simulates API calls
 * when the real backend is not available.
 */

// Mock API object that simulates axios
const mockApi = {
  async get(url, config = {}) {
    console.log(`Mock GET ${url}`, config)
    
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 500))
    
    // Return mock data based on the endpoint
    if (url.includes('/api/analytics/insights')) {
      return {
        data: {
          insights: [
            {
              id: 1,
              title: 'High Error Rate Detected',
              description: 'Error rate increased by 15% in the last hour',
              severity: 'high',
              timestamp: new Date().toISOString()
            }
          ]
        }
      }
    }
    
    if (url.includes('/api/analytics/performance')) {
      return {
        data: {
          metrics: {
            responseTime: 145,
            throughput: 1250,
            errorRate: 2.3,
            uptime: 99.9
          }
        }
      }
    }
    
    if (url.includes('/api/analytics/reports')) {
      return {
        data: {
          reports: [
            {
              id: 1,
              name: 'Daily Performance Report',
              status: 'completed',
              createdAt: new Date().toISOString()
            }
          ]
        }
      }
    }
    
    if (url.includes('/api/analytics/export')) {
      return {
        data: {
          exports: [
            {
              id: 1,
              name: 'Log Analysis Export',
              status: 'completed',
              downloadUrl: '/downloads/export-1.csv'
            }
          ]
        }
      }
    }
    
    // Default response
    return {
      data: {
        message: 'Mock API response',
        url: url
      }
    }
  },
  
  async post(url, data = {}, config = {}) {
    console.log(`Mock POST ${url}`, data, config)
    
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 500))
    
    // Return mock success response
    return {
      data: {
        success: true,
        message: 'Mock API response',
        url: url,
        data: data
      }
    }
  }
}

export default mockApi
