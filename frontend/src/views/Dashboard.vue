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
            <p class="text-sm text-gray-600 mt-1">Real-time log processing trends showing system activity and data ingestion patterns over the past 24 hours.</p>
          </div>
          <div class="card-body">
            <LineChart 
              :data="logVolumeData" 
              :options="logVolumeOptions"
              :height="300"
            />
          </div>
        </div>

        <!-- Log Distribution Bar Chart -->
        <div class="card">
          <div class="card-header">
            <h3 class="text-lg font-semibold text-gray-900">Log Distribution</h3>
            <p class="text-sm text-gray-600 mt-1">Breakdown of log levels (INFO, WARN, ERROR, DEBUG, FATAL) providing insights into system health and error patterns.</p>
          </div>
          <div class="card-body">
            <BarChart 
              :data="logDistributionData" 
              :options="logDistributionBarOptions"
              :height="300"
            />
          </div>
        </div>
      </div>

      <!-- Additional Charts Row -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        <!-- Response Time Chart -->
        <div class="card">
          <div class="card-header">
            <h3 class="text-lg font-semibold text-gray-900">Response Time Trends</h3>
            <p class="text-sm text-gray-600 mt-1">Performance metrics tracking API response times throughout the day to identify bottlenecks and optimization opportunities.</p>
          </div>
          <div class="card-body">
            <LineChart 
              :data="responseTimeData" 
              :options="responseTimeOptions"
              :height="300"
            />
          </div>
        </div>

        <!-- Service Health TreeMap -->
        <div class="card">
          <div class="card-header">
            <h3 class="text-lg font-semibold text-gray-900">Service Health Overview</h3>
            <p class="text-sm text-gray-600 mt-1">Hierarchical view of system services with size indicating importance and color indicating health status for quick monitoring.</p>
          </div>
          <div class="card-body">
            <TreeMapChart 
              :data="serviceHealthData" 
              :height="300"
            />
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
import { LineChart, BarChart, PieChart, TreeMapChart } from '@/components/charts'
import { fetchDashboardAnalytics } from '@/services/analytics'

export default {
  name: 'Dashboard',
  components: {
    LineChart,
    BarChart,
    PieChart,
    TreeMapChart
  },
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

    // Chart data - For beginners: This is the data that will be displayed in our charts
    const logVolumeData = ref({
      labels: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00', '24:00'],
      datasets: [{
        label: 'Logs per hour',
        data: [1200, 1900, 3000, 5000, 4200, 3800, 2100],
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        tension: 0.4,
        fill: true
      }]
    })

    const logDistributionData = ref({
      labels: ['INFO', 'WARN', 'ERROR', 'DEBUG', 'FATAL'],
      datasets: [{
        label: 'Log Count',
        data: [60, 25, 10, 4, 1],
        backgroundColor: [
          'rgba(34, 197, 94, 0.8)',   // Green for INFO
          'rgba(245, 158, 11, 0.8)',  // Yellow for WARN
          'rgba(239, 68, 68, 0.8)',   // Red for ERROR
          'rgba(107, 114, 128, 0.8)', // Gray for DEBUG
          'rgba(147, 51, 234, 0.8)'   // Purple for FATAL
        ],
        borderColor: [
          'rgb(34, 197, 94)',   // Green for INFO
          'rgb(245, 158, 11)',  // Yellow for WARN
          'rgb(239, 68, 68)',   // Red for ERROR
          'rgb(107, 114, 128)', // Gray for DEBUG
          'rgb(147, 51, 234)'   // Purple for FATAL
        ],
        borderWidth: 2,
        borderRadius: 4,
        borderSkipped: false
      }]
    })

    const responseTimeData = ref({
      labels: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00', '24:00'],
      datasets: [{
        label: 'Average Response Time (ms)',
        data: [85, 92, 78, 105, 88, 95, 82],
        borderColor: 'rgb(16, 185, 129)',
        backgroundColor: 'rgba(16, 185, 129, 0.1)',
        tension: 0.4,
        fill: true
      }]
    })

    // Service health data for TreeMap with drill-down capability
    const serviceHealthData = ref([
      {
        name: 'Database Services',
        status: 'healthy',
        importance: 100,
        responseTime: 15,
        uptime: 99.9,
        description: 'Core database infrastructure and data storage systems',
        children: [
          {
            name: 'PostgreSQL Primary',
            status: 'healthy',
            importance: 90,
            responseTime: 12,
            uptime: 99.9,
            description: 'Primary database for structured data storage',
            children: [
              {
                name: 'Connection Pool',
                status: 'healthy',
                importance: 85,
                responseTime: 5,
                uptime: 99.8,
                description: 'Database connection management'
              },
              {
                name: 'Query Processor',
                status: 'warning',
                importance: 80,
                responseTime: 25,
                uptime: 98.5,
                description: 'SQL query execution engine'
              },
              {
                name: 'Storage Engine',
                status: 'healthy',
                importance: 75,
                responseTime: 8,
                uptime: 99.9,
                description: 'Data persistence layer'
              }
            ]
          },
          {
            name: 'PostgreSQL Replica',
            status: 'healthy',
            importance: 70,
            responseTime: 18,
            uptime: 99.7,
            description: 'Read-only replica for load balancing',
            children: [
              {
                name: 'Replication Process',
                status: 'healthy',
                importance: 65,
                responseTime: 10,
                uptime: 99.5,
                description: 'Data synchronization from primary'
              }
            ]
          },
          {
            name: 'Redis Cache',
            status: 'healthy',
            importance: 60,
            responseTime: 2,
            uptime: 99.8,
            description: 'In-memory caching layer'
          }
        ]
      },
      {
        name: 'API Services',
        status: 'healthy',
        importance: 95,
        responseTime: 45,
        uptime: 99.8,
        description: 'RESTful API endpoints and microservices',
        children: [
          {
            name: 'Authentication API',
            status: 'healthy',
            importance: 90,
            responseTime: 25,
            uptime: 99.8,
            description: 'JWT authentication and authorization',
            children: [
              {
                name: 'Token Validator',
                status: 'healthy',
                importance: 85,
                responseTime: 5,
                uptime: 99.9,
                description: 'JWT token validation service'
              },
              {
                name: 'User Manager',
                status: 'healthy',
                importance: 80,
                responseTime: 15,
                uptime: 99.7,
                description: 'User account management'
              }
            ]
          },
          {
            name: 'Analytics API',
            status: 'healthy',
            importance: 85,
            responseTime: 120,
            uptime: 99.5,
            description: 'Data analytics and reporting endpoints',
            children: [
              {
                name: 'Query Engine',
                status: 'healthy',
                importance: 80,
                responseTime: 100,
                uptime: 99.4,
                description: 'Analytics query processing'
              },
              {
                name: 'Report Generator',
                status: 'warning',
                importance: 75,
                responseTime: 200,
                uptime: 98.8,
                description: 'Automated report generation'
              }
            ]
          },
          {
            name: 'Log Processing API',
            status: 'degraded',
            importance: 80,
            responseTime: 150,
            uptime: 98.5,
            description: 'Log ingestion and processing endpoints'
          }
        ]
      },
      {
        name: 'Frontend Services',
        status: 'healthy',
        importance: 75,
        responseTime: 65,
        uptime: 99.7,
        description: 'User interface and client-side applications',
        children: [
          {
            name: 'Web Application',
            status: 'healthy',
            importance: 70,
            responseTime: 50,
            uptime: 99.6,
            description: 'Main Vue.js dashboard application'
          },
          {
            name: 'Admin Dashboard',
            status: 'healthy',
            importance: 60,
            responseTime: 45,
            uptime: 99.5,
            description: 'Administrative interface'
          }
        ]
      },
      {
        name: 'Infrastructure Services',
        status: 'warning',
        importance: 70,
        responseTime: 200,
        uptime: 97.2,
        description: 'Core infrastructure and monitoring systems',
        children: [
          {
            name: 'Elasticsearch Cluster',
            status: 'healthy',
            importance: 85,
            responseTime: 45,
            uptime: 99.8,
            description: 'Search engine for log analysis and queries'
          },
          {
            name: 'Kafka Streaming',
            status: 'degraded',
            importance: 80,
            responseTime: 120,
            uptime: 98.5,
            description: 'Real-time message streaming platform'
          },
          {
            name: 'Monitoring System',
            status: 'warning',
            importance: 75,
            responseTime: 200,
            uptime: 97.2,
            description: 'System health monitoring and alerting'
          }
        ]
      }
    ])

    // Chart options - For beginners: These control how the charts look and behave
    const logVolumeOptions = ref({
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        title: {
          display: true,
          text: 'Log Volume Over Time',
          font: {
            size: 16,
            weight: 'bold'
          }
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          title: {
            display: true,
            text: 'Number of Logs',
            font: {
              size: 14,
              weight: 'bold'
            },
            color: '#374151'
          },
          grid: {
            color: 'rgba(0, 0, 0, 0.1)'
          }
        },
        x: {
          title: {
            display: true,
            text: 'Time (24h)',
            font: {
              size: 14,
              weight: 'bold'
            },
            color: '#374151'
          },
          grid: {
            display: false
          }
        }
      }
    })

    const pieChartOptions = ref({
      plugins: {
        title: {
          display: true,
          text: 'Log Level Distribution'
        }
      }
    })

    const logDistributionBarOptions = ref({
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        title: {
          display: true,
          text: 'Log Level Distribution (Last 24 Hours)',
          font: {
            size: 16,
            weight: 'bold'
          }
        },
        legend: {
          display: true,
          position: 'top'
        },
        tooltip: {
          callbacks: {
            label: function(context) {
              const label = context.dataset.label || ''
              const value = context.parsed.y
              const total = context.dataset.data.reduce((a, b) => a + b, 0)
              const percentage = ((value / total) * 100).toFixed(1)
              return `${label}: ${value} (${percentage}%)`
            }
          }
        }
      },
      scales: {
        x: {
          title: {
            display: true,
            text: 'Log Level',
            font: {
              size: 14,
              weight: 'bold'
            }
          },
          grid: {
            display: false
          }
        },
        y: {
          beginAtZero: true,
          title: {
            display: true,
            text: 'Number of Logs',
            font: {
              size: 14,
              weight: 'bold'
            }
          },
          grid: {
            color: 'rgba(0, 0, 0, 0.1)'
          }
        }
      },
      animation: {
        duration: 1000,
        easing: 'easeInOutQuart'
      }
    })

    const responseTimeOptions = ref({
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        title: {
          display: true,
          text: 'Response Time Trends',
          font: {
            size: 16,
            weight: 'bold'
          }
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          title: {
            display: true,
            text: 'Response Time (ms)',
            font: {
              size: 14,
              weight: 'bold'
            },
            color: '#374151'
          },
          grid: {
            color: 'rgba(0, 0, 0, 0.1)'
          }
        },
        x: {
          title: {
            display: true,
            text: 'Time (24h)',
            font: {
              size: 14,
              weight: 'bold'
            },
            color: '#374151'
          },
          grid: {
            display: false
          }
        }
      }
    })


    // Computed properties
    const systemHealth = computed(() => systemStore.systemHealth)

    // Methods
    const refreshData = async () => {
      isLoading.value = true
      try {
        console.log('🔄 Refreshing dashboard data...')
        
        // Fetch system health
        await systemStore.checkSystemHealth()
        
        // Fetch analytics data
        const analyticsData = await fetchDashboardAnalytics()
        console.log('📊 Analytics data received:', analyticsData)
        
        // Update chart data with real data
        if (analyticsData) {
          console.log('📈 Updating chart data...')
          logVolumeData.value = analyticsData.logVolume
          logDistributionData.value = analyticsData.logDistribution
          responseTimeData.value = analyticsData.responseTime
          
          // Update service health data if available
          if (analyticsData.serviceHealth) {
            serviceHealthData.value = analyticsData.serviceHealth
          }
          
          // Update system metrics
          if (analyticsData.systemMetrics) {
            logsProcessed.value = analyticsData.systemMetrics.logsProcessed
            activeAlerts.value = analyticsData.systemMetrics.activeAlerts
            responseTime.value = analyticsData.systemMetrics.responseTime
          }
          console.log('✅ Chart data updated successfully')
        } else {
          console.log('❌ No analytics data received')
        }
        
      } catch (error) {
        console.error('❌ Failed to refresh data:', error)
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
      console.log('🎯 Dashboard mounted, refreshing data...')
      refreshData()
    })

    return {
      // Data
      isLoading,
      logsProcessed,
      activeAlerts,
      responseTime,
      recentActivity,
      
      // Chart data
      logVolumeData,
      logDistributionData,
      responseTimeData,
      serviceHealthData,
      
      // Chart options
      logVolumeOptions,
      pieChartOptions,
      logDistributionBarOptions,
      responseTimeOptions,
      
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
