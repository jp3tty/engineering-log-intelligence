/**
 * API Service
 * ==========
 * 
 * This service handles API calls for the application.
 * It uses mock data when the real backend is not available.
 */

// Mock API object that simulates axios
const api = {
  async get(url, config = {}) {
    console.log(`API GET ${url}`, config)
    
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 100))
    
    // Handle analytics insights endpoint
    if (url.includes('/api/analytics_insights')) {
      const action = config.params?.action
      
      if (action === 'overview') {
        // Generate dynamic overview data
        const now = new Date()
        const hourOfDay = now.getHours()
        const minuteOfHour = now.getMinutes()
        const isBusinessHours = hourOfDay >= 9 && hourOfDay <= 17
        
        const baseLogVolume = 125000
        const hourModifier = isBusinessHours ? 1.35 : 0.65
        const randomVariation = 0.85 + Math.random() * 0.3
        const minuteVariation = 1 + (minuteOfHour / 60) * 0.1
        const total_logs = Math.floor(baseLogVolume * hourModifier * randomVariation * minuteVariation)
        
        const anomalyRate = 0.015 + Math.random() * 0.025
        const anomalies_detected = Math.floor(total_logs * anomalyRate)
        
        const baseResponseTime = 75
        const loadFactor = total_logs / baseLogVolume
        const avg_response_time = Math.max(60, Math.min(150, Math.floor(baseResponseTime * loadFactor + Math.random() * 25)))
        
        const healthBase = 98 - (anomalies_detected / total_logs) * 100
        const system_health = Math.max(85, Math.min(99, healthBase))
        
        console.log('📊 Mock API Generated Overview:', { total_logs, anomalies_detected, avg_response_time, system_health, hourOfDay, isBusinessHours })
        
        return {
          data: {
            total_logs: total_logs,
            anomalies_detected: anomalies_detected,
            avg_response_time: avg_response_time,
            system_health: parseFloat(system_health.toFixed(1)),
            logs_trend: -2 + Math.random() * 20,
            anomalies_trend: -15 + Math.random() * 20,
            response_trend: -10 + Math.random() * 15,
            health_trend: -5 + Math.random() * 8
          }
        }
      }
      
      if (action === 'insights') {
        return {
          data: {
            trend_analysis: [
              {
                id: 1,
                title: 'Response Time Improvement Trend',
                description: 'Average response times have decreased by 15% over the last week, indicating successful optimization efforts.',
                type: 'decreasing',
                confidence: 0.89,
                impact: 'high'
              },
              {
                id: 2,
                title: 'Log Volume Growth Pattern',
                description: 'Log volume is showing a consistent 12% week-over-week increase, suggesting system growth.',
                type: 'increasing',
                confidence: 0.92,
                impact: 'medium'
              },
              {
                id: 3,
                title: 'Error Rate Stability',
                description: 'Error rates have remained stable at 0.3% for the past month, indicating good system health.',
                type: 'stable',
                confidence: 0.95,
                impact: 'low'
              }
            ],
            anomalies: [
              {
                id: 1,
                title: 'Unusual CPU Spike Detected',
                description: 'CPU usage spiked to 95% for 15 minutes at 2:30 AM, which is unusual for this time period.',
                severity: 'high',
                confidence: 0.87,
                detected_at: new Date(Date.now() - 3600000).toISOString(),
                affected_systems: ['web-server-01', 'web-server-02']
              },
              {
                id: 2,
                title: 'Memory Leak Pattern Identified',
                description: 'Gradual memory increase detected in application containers over the last 24 hours.',
                severity: 'medium',
                confidence: 0.78,
                detected_at: new Date(Date.now() - 86400000).toISOString(),
                affected_systems: ['app-container-03', 'app-container-07']
              },
              {
                id: 3,
                title: 'Network Latency Anomaly',
                description: 'Network latency increased by 40% for 5 minutes during peak traffic hours.',
                severity: 'low',
                confidence: 0.82,
                detected_at: new Date(Date.now() - 1800000).toISOString(),
                affected_systems: ['load-balancer-01']
              }
            ],
            patterns: [
              {
                id: 1,
                title: 'Peak Traffic Pattern',
                description: 'Consistent traffic spikes detected every weekday between 9-10 AM and 5-6 PM, indicating business hours usage patterns.',
                type: 'temporal',
                frequency: 127,
                tags: ['traffic', 'business-hours', 'predictable'],
                confidence: 0.94
              },
              {
                id: 2,
                title: 'Error Correlation Pattern',
                description: 'Database timeout errors consistently precede application crashes by 2-3 minutes, suggesting a cascading failure pattern.',
                type: 'causal',
                frequency: 23,
                tags: ['database', 'timeout', 'cascading-failure'],
                confidence: 0.89
              },
              {
                id: 3,
                title: 'Resource Usage Pattern',
                description: 'Memory usage follows a predictable weekly cycle with cleanup occurring every Sunday at 2 AM.',
                type: 'cyclical',
                frequency: 52,
                tags: ['memory', 'cleanup', 'weekly-cycle'],
                confidence: 0.96
              },
              {
                id: 4,
                title: 'API Response Time Pattern',
                description: 'API response times increase by 15-20% during the first 30 minutes after deployments, indicating warm-up behavior.',
                type: 'behavioral',
                frequency: 18,
                tags: ['api', 'deployment', 'warm-up'],
                confidence: 0.87
              }
            ],
            recommendations: [
              {
                id: 1,
                title: 'Implement Database Query Optimization',
                description: 'Based on performance analysis, optimizing the top 10 slowest queries could improve response times by up to 25%.',
                priority: 'high',
                expected_impact: '25% faster response times',
                category: 'performance',
                effort: 'medium'
              },
              {
                id: 2,
                title: 'Set Up Automated Scaling',
                description: 'Implement auto-scaling based on CPU and memory thresholds to handle traffic spikes automatically.',
                priority: 'medium',
                expected_impact: 'Reduce manual intervention by 80%',
                category: 'infrastructure',
                effort: 'high'
              },
              {
                id: 3,
                title: 'Enhance Log Retention Strategy',
                description: 'Current log retention is consuming 40% of storage. Implement tiered retention to optimize costs.',
                priority: 'low',
                expected_impact: 'Reduce storage costs by 30%',
                category: 'cost-optimization',
                effort: 'low'
              }
            ],
            generated_at: new Date().toISOString()
          }
        }
      }
    }
    
    // Handle analytics performance endpoint
    if (url.includes('/api/analytics_performance')) {
      const action = config.params?.action
      const timeRange = config.params?.time_range || '7d'
      
      if (action === 'metrics') {
        return {
          data: {
            time_range: timeRange,
            cpu_usage: {
              avg: 65.2,
              max: 89.1,
              min: 23.4,
              trend: 2.3
            },
            memory_usage: {
              avg: 72.8,
              max: 91.5,
              min: 45.2,
              trend: -1.2
            },
            response_times: {
              avg: 125.6,
              max: 298.3,
              min: 67.1,
              trend: -5.4
            },
            throughput: {
              avg: 750,
              max: 1200,
              min: 300,
              trend: 8.7
            },
            generated_at: new Date().toISOString()
          }
        }
      }
      
      if (action === 'forecast') {
        return {
          data: {
            time_range: timeRange,
            forecast_period: '30d',
            cpu_forecast: [70.1, 72.3, 75.8, 78.2, 81.5, 83.7, 86.2],
            memory_forecast: [85.2, 87.1, 89.5, 91.8, 94.2, 96.7, 98.9],
            response_time_forecast: [145.2, 158.7, 172.3, 185.9, 198.4, 212.1, 225.8],
            generated_at: new Date().toISOString()
          }
        }
      }
    }
    
    // Handle analytics reports endpoint
    if (url.includes('/api/analytics_reports')) {
      const action = config.params?.action
      
      if (action === 'list_templates') {
        return {
          data: [
            { id: 'daily_summary', name: 'Daily Summary Report', description: 'Overview of daily system activity' },
            { id: 'weekly_performance', name: 'Weekly Performance Report', description: 'Detailed weekly performance metrics' },
            { id: 'anomaly_overview', name: 'Anomaly Overview Report', description: 'Summary of detected anomalies' }
          ]
        }
      }
      
      if (action === 'list_reports') {
        return {
          data: [
            { id: 'rep_001', name: 'Daily Summary 2025-10-01', status: 'completed', generated_at: new Date(Date.now() - 86400000).toISOString(), url: '/reports/daily_summary_2025-10-01.pdf' },
            { id: 'rep_002', name: 'Weekly Performance 2025-W39', status: 'pending', generated_at: new Date(Date.now() - 259200000).toISOString(), url: null }
          ]
        }
      }
    }
    
    // Handle dashboard analytics endpoint
    if (url.includes('/api/dashboard_analytics')) {
      return {
        data: {
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
          }
        }
      }
    }
    
    // Default response for unknown endpoints
    console.warn(`Unknown API endpoint: ${url}`)
    return {
      data: {
        message: 'Mock API response',
        url: url,
        timestamp: new Date().toISOString()
      }
    }
  },
  
  async post(url, data = {}, config = {}) {
    console.log(`API POST ${url}`, data, config)
    
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 100))
    
    // Handle analytics reports POST
    if (url.includes('/api/analytics_reports')) {
      const action = data.action
      
      if (action === 'generate') {
        return {
          data: {
            id: `rep_${Math.floor(Math.random() * 900) + 100}`,
            name: `${data.template_id.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())} ${new Date().toLocaleDateString()}`,
            status: 'completed',
            generated_at: new Date().toISOString(),
            url: `/reports/${data.template_id}_${Date.now()}.pdf`,
            template_id: data.template_id,
            options: data.options
          }
        }
      }
      
      if (action === 'schedule') {
        return {
          data: {
            id: `sch_${Math.floor(Math.random() * 900) + 100}`,
            message: 'Report scheduled successfully',
            schedule_data: data.schedule_data,
            scheduled_at: new Date().toISOString()
          }
        }
      }
    }
    
    // Default POST response
    return {
      data: {
        success: true,
        message: 'Mock API response',
        url: url,
        data: data,
        timestamp: new Date().toISOString()
      }
    }
  }
}

export default api
