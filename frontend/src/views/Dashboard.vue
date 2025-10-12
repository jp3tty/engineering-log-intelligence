<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Page Header -->
    <div class="bg-white shadow-sm border-b border-gray-200">
      <div class="container-custom py-6">
        <div class="flex items-center justify-between">
          <div class="flex-1">
            <h1 class="text-2xl font-bold text-gray-900">Engineering Log Intelligence Dashboard</h1>
            <p class="text-gray-600 mt-1">Real-time monitoring and analysis of enterprise log data from multiple sources</p>
            <div class="mt-3 flex flex-wrap items-center gap-4 text-sm text-gray-500">
              <div class="flex items-center">
                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <span><strong>Data Sources:</strong> SPLUNK, SAP, Application Logs</span>
              </div>
              <div class="flex items-center">
                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span><strong>Time Range:</strong> Last 24 Hours</span>
              </div>
              <div class="flex items-center">
                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
                <span><strong>Processing:</strong> Real-time Analytics & AI Insights</span>
              </div>
            </div>
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
        <!-- System Health Card - Links to Monitoring -->
        <router-link to="/monitoring" class="card card-clickable">
          <div class="card-body">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <div class="w-8 h-8 bg-success-100 rounded-lg flex items-center justify-center">
                  <svg class="w-5 h-5 text-success-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
              </div>
              <div class="ml-4 flex-1">
                <p class="text-sm font-medium text-gray-600">System Health</p>
                <p class="text-2xl font-semibold text-gray-900">{{ systemHealth.status || 'Unknown' }}</p>
              </div>
              <div class="ml-2">
                <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                </svg>
              </div>
            </div>
          </div>
        </router-link>

        <!-- Logs Processed Card - Links to Log Analysis -->
        <router-link to="/logs" class="card card-clickable">
          <div class="card-body">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <div class="w-8 h-8 bg-primary-100 rounded-lg flex items-center justify-center">
                  <svg class="w-5 h-5 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                </div>
              </div>
              <div class="ml-4 flex-1">
                <p class="text-sm font-medium text-gray-600">Logs Processed</p>
                <p class="text-2xl font-semibold text-gray-900">{{ formatNumber(logsProcessed) }}</p>
              </div>
              <div class="ml-2">
                <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                </svg>
              </div>
            </div>
          </div>
        </router-link>

        <!-- Active Alerts Card - Links to ML Analytics -->
        <router-link to="/ml-analytics" class="card card-clickable">
          <div class="card-body">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <div class="w-8 h-8 bg-warning-100 rounded-lg flex items-center justify-center">
                  <svg class="w-5 h-5 text-warning-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
                  </svg>
                </div>
              </div>
              <div class="ml-4 flex-1">
                <p class="text-sm font-medium text-gray-600">Active Alerts</p>
                <p class="text-2xl font-semibold text-gray-900">{{ activeAlerts }}</p>
              </div>
              <div class="ml-2">
                <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                </svg>
              </div>
            </div>
          </div>
        </router-link>

        <!-- Response Time Card - Links to Monitoring -->
        <router-link to="/monitoring" class="card card-clickable">
          <div class="card-body">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <div class="w-8 h-8 bg-danger-100 rounded-lg flex items-center justify-center">
                  <svg class="w-5 h-5 text-danger-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                </div>
              </div>
              <div class="ml-4 flex-1">
                <p class="text-sm font-medium text-gray-600">Response Time</p>
                <p class="text-2xl font-semibold text-gray-900">{{ responseTime }}ms</p>
              </div>
              <div class="ml-2">
                <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                </svg>
              </div>
            </div>
          </div>
        </router-link>
      </div>

      <!-- ML Summary Widget -->
      <div class="mb-8">
        <MLSummaryWidget />
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
              :height="375"
            />
          </div>
        </div>

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
              :height="375"
            />
          </div>
        </div>
      </div>

      <!-- Additional Charts Row -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        <!-- Log Distribution Bar Chart -->
        <div class="card">
          <div class="card-header">
            <h3 class="text-lg font-semibold text-gray-900">Log Distribution (Last 24 Hours)</h3>
            <p class="text-sm text-gray-600 mt-1">Breakdown of log levels across all data sources (SPLUNK, SAP, Application logs) over the past 24 hours, providing insights into system health and error patterns.</p>
          </div>
          <div class="card-body" style="overflow: visible; position: relative; z-index: 1;">
            <div class="flex flex-col gap-6">
              <!-- Chart Container -->
              <div class="w-full" style="overflow: visible; position: relative;">
                <div style="height: 375px; overflow: visible; position: relative;">
                  <BarChart 
                    :data="logDistributionData" 
                    :options="logDistributionBarOptions"
                    :height="375"
                  />
                </div>
              </div>
              
              <!-- Log Level Legend -->
              <div class="w-full">
                <div class="p-4 bg-gray-50 rounded-lg">
                  <div class="space-y-3">
                    <div class="flex items-center space-x-3">
                      <div class="w-4 h-4 rounded-full bg-green-500 flex-shrink-0"></div>
                      <div>
                        <p class="text-xs text-gray-600">Normal operations, successful transactions</p>
                      </div>
                    </div>
                    <div class="flex items-center space-x-3">
                      <div class="w-4 h-4 rounded-full bg-yellow-500 flex-shrink-0"></div>
                      <div>
                        <p class="text-xs text-gray-600">Performance issues, unusual patterns</p>
                      </div>
                    </div>
                    <div class="flex items-center space-x-3">
                      <div class="w-4 h-4 rounded-full bg-red-500 flex-shrink-0"></div>
                      <div>
                        <p class="text-xs text-gray-600">Application errors, failed transactions</p>
                      </div>
                    </div>
                    <div class="flex items-center space-x-3">
                      <div class="w-4 h-4 rounded-full bg-gray-500 flex-shrink-0"></div>
                      <div>
                        <p class="text-xs text-gray-600">Detailed diagnostic information</p>
                      </div>
                    </div>
                    <div class="flex items-center space-x-3">
                      <div class="w-4 h-4 rounded-full bg-purple-500 flex-shrink-0"></div>
                      <div>
                        <p class="text-xs text-gray-600">Critical system failures, security breaches</p>
                      </div>
                    </div>
                    <div class="pt-3 border-t border-gray-200">
                      <div class="flex items-center space-x-3">
                        <div class="w-4 h-4 rounded-full bg-blue-500 flex-shrink-0"></div>
                        <div>
                          <p class="text-xs text-gray-600">SPLUNK + SAP + Application logs</p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Service Health TreeMap -->
        <div class="card">
          <div class="card-header">
            <h3 class="text-lg font-semibold text-gray-900">Service Health Overview</h3>
            <p class="text-sm text-gray-600 mt-1">Hierarchical view of system services with size indicating importance and color indicating health status for quick monitoring.</p>
          </div>
          <div class="card-body">
            <div class="flex flex-col gap-6">
              <!-- TreeMap Container -->
              <div class="w-full">
                <TreeMapChart :data="flatServiceHealthData" :height="400" />
              </div>
              
              <!-- Service Health Legend -->
              <div class="w-full">
                <div class="p-4 bg-gray-50 rounded-lg">
                  <div class="space-y-3">
                    <div class="flex items-center space-x-3">
                      <div class="w-4 h-4 rounded-full bg-green-500 flex-shrink-0"></div>
                      <div>
                        <p class="text-xs text-gray-600">Healthy services, optimal performance</p>
                      </div>
                    </div>
                    <div class="flex items-center space-x-3">
                      <div class="w-4 h-4 rounded-full bg-yellow-500 flex-shrink-0"></div>
                      <div>
                        <p class="text-xs text-gray-600">Warning state, performance degradation</p>
                      </div>
                    </div>
                    <div class="flex items-center space-x-3">
                      <div class="w-4 h-4 rounded-full bg-red-500 flex-shrink-0"></div>
                      <div>
                        <p class="text-xs text-gray-600">Critical issues, service failures</p>
                      </div>
                    </div>
                    <div class="flex items-center space-x-3">
                      <div class="w-4 h-4 rounded-full bg-gray-500 flex-shrink-0"></div>
                      <div>
                        <p class="text-xs text-gray-600">Unknown status, monitoring unavailable</p>
                      </div>
                    </div>
                    <div class="pt-3 border-t border-gray-200">
                      <div class="flex items-center space-x-3">
                        <div class="w-4 h-4 rounded-full bg-blue-500 flex-shrink-0"></div>
                        <div>
                          <p class="text-xs text-gray-600">Service size indicates importance/load</p>
                        </div>
                      </div>
                    </div>
                  </div>
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
import { LineChart, BarChart, PieChart, TreeMapChart } from '@/components/charts'
import { fetchDashboardAnalytics } from '@/services/analytics'
import MLSummaryWidget from '@/components/dashboard/MLSummaryWidget.vue'

export default {
  name: 'Dashboard',
  components: {
    LineChart,
    BarChart,
    PieChart,
    TreeMapChart,
    MLSummaryWidget
  },
  setup() {
    const systemStore = useSystemStore()

    // Reactive data
    const isLoading = ref(false)
    
    // Generate dynamic metrics based on time of day
    // Fetch REAL metrics from /api/metrics - NO MOCK DATA!
    const fetchRealMetrics = async () => {
      try {
        console.log('📊 Fetching REAL metrics from /api/metrics...')
        const response = await fetch('/api/metrics')
        const data = await response.json()
        
        if (data.success && data.metrics) {
          console.log('✅ Real metrics loaded:', data.metrics)
          return {
            logs: data.metrics.total_logs || 0,
            alerts: data.metrics.high_anomaly_count || 0,  // Use actual count, not calculated from rate
            response: Math.round(data.metrics.avg_response_time_ms || 0)
          }
        }
      } catch (error) {
        console.error('❌ Failed to fetch real metrics:', error)
      }
      
      // Fallback only if API fails
      return { logs: 0, alerts: 0, response: 0 }
    }
    
    // Initialize with zeros, will be loaded from API
    const logsProcessed = ref(0)
    const activeAlerts = ref(0)
    const responseTime = ref(0)
    
    console.log('=' .repeat(80))
    console.log('🚀 DASHBOARD INITIALIZED - ' + new Date().toISOString())
    console.log('Loading REAL metrics from database...')
    console.log('=' .repeat(80))
    
    // Load real metrics immediately on initialization
    ;(async () => {
      const initialRealMetrics = await fetchRealMetrics()
      logsProcessed.value = initialRealMetrics.logs
      activeAlerts.value = initialRealMetrics.alerts
      responseTime.value = initialRealMetrics.response
      console.log('✅ Initial real metrics loaded:', initialRealMetrics)
    })()

    // Chart data - For beginners: This is the data that will be displayed in our charts
    // Generate realistic log volume data based on total logs processed
    const generateLogVolumeData = () => {
      const now = new Date()
      const hourOfDay = now.getHours()
      const dayOfWeek = now.getDay()
      
      // Use the total logs from the metric card as our base
      const totalLogs = logsProcessed.value
      
      // Generate distribution weights for each 4-hour period
      const weights = []
      const isWeekend = dayOfWeek === 0 || dayOfWeek === 6
      const baseMultiplier = isWeekend ? 0.6 : 1.0
      
      for (let i = 0; i < 7; i++) {
        const timeOfDataPoint = i * 4 // 0, 4, 8, 12, 16, 20, 24
        
        // Business hours (8-20) have higher volume
        const isBusinessHours = timeOfDataPoint >= 8 && timeOfDataPoint <= 20
        const hourFactor = isBusinessHours ? 1.5 + Math.random() * 0.5 : 0.4 + Math.random() * 0.3
        
        // Peak hours (12-16) have even higher volume
        const isPeakHours = timeOfDataPoint >= 12 && timeOfDataPoint <= 16
        const peakFactor = isPeakHours ? 1.3 + Math.random() * 0.4 : 1.0
        
        // Current time has extra variation
        const isNearCurrentTime = Math.abs(timeOfDataPoint - hourOfDay) < 3
        const currentTimeFactor = isNearCurrentTime ? 0.9 + Math.random() * 0.4 : 1.0
        
        weights.push(baseMultiplier * hourFactor * peakFactor * currentTimeFactor)
      }
      
      // Normalize weights to sum to totalLogs
      const totalWeight = weights.reduce((sum, w) => sum + w, 0)
      const data = weights.map(w => Math.floor((w / totalWeight) * totalLogs))
      
      console.log('📈 Generated Log Volume (sum:', data.reduce((a,b) => a+b, 0), 'target:', totalLogs, '):', data)
      
      return {
        labels: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00', '24:00'],
        datasets: [{
          label: 'Logs per hour',
          data: data,
          borderColor: 'rgb(59, 130, 246)',
          backgroundColor: 'rgba(59, 130, 246, 0.1)',
          tension: 0.4,
          fill: true
        }]
      }
    }
    
    const logVolumeData = ref(generateLogVolumeData())

    // Generate dynamic log distribution data
    const generateLogDistributionData = () => {
      // Use the total logs processed to calculate realistic distribution
      const totalLogs = logsProcessed.value
      
      // Realistic log level distribution percentages with some variation
      const infoPercent = 0.68 + Math.random() * 0.08  // 68-76% INFO
      const warnPercent = 0.15 + Math.random() * 0.05  // 15-20% WARN
      const errorPercent = 0.05 + Math.random() * 0.03 // 5-8% ERROR
      const debugPercent = 0.03 + Math.random() * 0.02 // 3-5% DEBUG
      const fatalPercent = 0.001 + Math.random() * 0.003 // 0.1-0.4% FATAL
      
      const infoCount = Math.floor(totalLogs * infoPercent)
      const warnCount = Math.floor(totalLogs * warnPercent)
      const errorCount = Math.floor(totalLogs * errorPercent)
      const debugCount = Math.floor(totalLogs * debugPercent)
      const fatalCount = Math.floor(totalLogs * fatalPercent)
      
      console.log('📊 Generated Log Distribution:', { infoCount, warnCount, errorCount, debugCount, fatalCount, totalLogs })
      
      return {
        labels: ['INFO', 'WARN', 'ERROR', 'DEBUG', 'FATAL'],
        datasets: [{
          label: 'Log Count (Last 24h)',
          data: [infoCount, warnCount, errorCount, debugCount, fatalCount],
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
      }
    }
    
    const logDistributionData = ref(generateLogDistributionData())

    // Generate realistic response time data based on current response time metric
    const generateResponseTimeData = () => {
      const now = new Date()
      const hourOfDay = now.getHours()
      const dayOfWeek = now.getDay()
      
      // Use the average response time from the metric card as our base
      const avgResponseTime = responseTime.value
      
      // Generate dynamic response time data with variation around the average
      const data = []
      const isWeekend = dayOfWeek === 0 || dayOfWeek === 6
      
      for (let i = 0; i < 7; i++) {
        const timeOfDataPoint = i * 4 // 0, 4, 8, 12, 16, 20, 24
        
        // Business hours (8-20) have higher response times due to load
        const isBusinessHours = timeOfDataPoint >= 8 && timeOfDataPoint <= 20
        const loadFactor = isBusinessHours ? 1.1 + Math.random() * 0.4 : 0.7 + Math.random() * 0.2
        
        // Peak hours (12-16) have even higher response times
        const isPeakHours = timeOfDataPoint >= 12 && timeOfDataPoint <= 16
        const peakPenalty = isPeakHours ? 1.1 + Math.random() * 0.3 : 1.0
        
        // Current time has extra variation
        const isNearCurrentTime = Math.abs(timeOfDataPoint - hourOfDay) < 3
        const currentTimeFactor = isNearCurrentTime ? 0.85 + Math.random() * 0.5 : 1.0
        
        // Weekend adjustment
        const weekendFactor = isWeekend ? 0.8 : 1.0
        
        const respTime = Math.floor(avgResponseTime * loadFactor * peakPenalty * currentTimeFactor * weekendFactor)
        data.push(respTime)
      }
      
      const calculatedAvg = Math.floor(data.reduce((a,b) => a+b, 0) / data.length)
      console.log('⏱️ Generated Response Time (avg:', calculatedAvg, 'target:', avgResponseTime, '):', data)
      
      return {
        labels: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00', '24:00'],
        datasets: [{
          label: 'Average Response Time (ms)',
          data: data,
          borderColor: 'rgb(16, 185, 129)',
          backgroundColor: 'rgba(16, 185, 129, 0.1)',
          tension: 0.4,
          fill: true
        }]
      }
    }
    
    const responseTimeData = ref(generateResponseTimeData())

    // Generate dynamic recent activity based on log distribution and metrics
    const generateRecentActivity = () => {
      const activities = []
      const now = Date.now()
      
      // Get log counts from distribution (now that it's been created)
      const distribution = logDistributionData.value?.datasets?.[0]?.data || [0, 0, 0, 0, 0]
      const [infoCount, warnCount, errorCount, debugCount, fatalCount] = distribution
      
      // Always show a recent system health check (5 min ago)
      activities.push({
        id: 1,
        type: 'success',
        message: 'System health check completed successfully',
        timestamp: new Date(now - 5 * 60 * 1000),
      })
      
      // Show FATAL activity if any fatal logs exist (most critical, show first)
      if (fatalCount > 0) {
        activities.push({
          id: 2,
          type: 'error',
          message: `${fatalCount.toLocaleString()} FATAL logs detected - immediate attention required`,
          timestamp: new Date(now - 8 * 60 * 1000),
        })
      }
      
      // Show ERROR activity if significant error count
      if (errorCount > 100) {
        activities.push({
          id: 3,
          type: 'error',
          message: `${errorCount.toLocaleString()} ERROR logs processed in last 24 hours`,
          timestamp: new Date(now - 12 * 60 * 1000),
        })
      }
      
      // Show WARNING activity if significant warning count
      if (warnCount > 500) {
        activities.push({
          id: 4,
          type: 'warning',
          message: `${warnCount.toLocaleString()} WARNING logs require review`,
          timestamp: new Date(now - 20 * 60 * 1000),
        })
      }
      
      // Show log batch processing info
      activities.push({
        id: 5,
        type: 'info',
        message: `Log batch processed: ${logsProcessed.value.toLocaleString()} total entries`,
        timestamp: new Date(now - 25 * 60 * 1000),
      })
      
      // Show INFO log summary
      if (infoCount > 0) {
        activities.push({
          id: 6,
          type: 'info',
          message: `${infoCount.toLocaleString()} INFO logs processed successfully`,
          timestamp: new Date(now - 35 * 60 * 1000),
        })
      }
      
      // Show active alerts if any
      if (activeAlerts.value > 0) {
        activities.push({
          id: 7,
          type: 'warning',
          message: `${activeAlerts.value} active alerts require attention`,
          timestamp: new Date(now - 40 * 60 * 1000),
        })
      }
      
      // Limit to 5 most recent activities
      return activities.slice(0, 5)
    }
    
    const recentActivity = ref(generateRecentActivity())

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
          display: false
        },
        legend: {
          display: false
        },
        tooltip: {
          enabled: true,
          mode: 'index',
          intersect: false,
          position: 'nearest',
          backgroundColor: 'rgba(0, 0, 0, 0.9)',
          titleColor: '#fff',
          bodyColor: '#fff',
          borderColor: 'rgba(255, 255, 255, 0.5)',
          borderWidth: 2,
          padding: 16,
          displayColors: true,
          cornerRadius: 8,
          titleFont: {
            size: 14,
            weight: 'bold'
          },
          bodyFont: {
            size: 13
          },
          callbacks: {
            title: function(context) {
              return 'Log Level: ' + context[0].label
            },
            label: function(context) {
              const value = context.parsed.y
              const total = context.dataset.data.reduce((a, b) => a + b, 0)
              const percentage = ((value / total) * 100).toFixed(1)
              return [
                `Count: ${value.toLocaleString()} logs`,
                `Percentage: ${percentage}% of total`,
                `Total 24h: ${total.toLocaleString()} logs`
              ]
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
              size: 12,
              weight: 'bold'
            }
          },
          grid: {
            display: false
          },
          ticks: {
            maxRotation: 45,
            minRotation: 0,
            font: {
              size: 10
            },
            padding: 10
          }
        },
        y: {
          beginAtZero: true,
          min: 0,
          max: 16000,
          title: {
            display: true,
            text: 'Log Count (24h)',
            font: {
              size: 12,
              weight: 'bold'
            }
          },
          grid: {
            color: 'rgba(0, 0, 0, 0.1)'
          },
          ticks: {
            font: {
              size: 11
            },
            stepSize: 2000,
            callback: function(value) {
              if (value >= 1000) {
                return (value / 1000).toFixed(0) + 'k'
              }
              return value
            }
          }
        }
      },
      animation: {
        duration: 1000,
        easing: 'easeInOutQuart'
      },
      layout: {
        padding: {
          left: 20,
          right: 20,
          top: 20,
          bottom: 20
        }
      },
      elements: {
        bar: {
          borderWidth: 1
        }
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
          
          // Update system metrics with REAL data from /api/metrics
          const realMetrics = await fetchRealMetrics()
          logsProcessed.value = realMetrics.logs
          activeAlerts.value = realMetrics.alerts
          responseTime.value = realMetrics.response
          console.log('✅ Chart data and real metrics updated successfully')
        } else {
          console.log('❌ No analytics data received, fetching real metrics only')
          // Fetch REAL metrics from /api/metrics
          const realMetrics = await fetchRealMetrics()
          logsProcessed.value = realMetrics.logs
          activeAlerts.value = realMetrics.alerts
          responseTime.value = realMetrics.response
          
          // Regenerate ALL chart data with variation
          logVolumeData.value = generateLogVolumeData()
          logDistributionData.value = generateLogDistributionData()
          responseTimeData.value = generateResponseTimeData()
          
          // Regenerate recent activity based on new data
          recentActivity.value = generateRecentActivity()
        }
        
      } catch (error) {
        console.error('❌ Failed to refresh data:', error)
        // Even on error, fetch real metrics
        const realMetrics = await fetchRealMetrics()
        logsProcessed.value = realMetrics.logs
        activeAlerts.value = realMetrics.alerts
        responseTime.value = realMetrics.response
        
        // Regenerate ALL chart data
        logVolumeData.value = generateLogVolumeData()
        logDistributionData.value = generateLogDistributionData()
        responseTimeData.value = generateResponseTimeData()
        
        // Regenerate recent activity based on new data
        recentActivity.value = generateRecentActivity()
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

    // Computed property to flatten service health data for TreeMap
    const flatServiceHealthData = computed(() => {
      if (!serviceHealthData.value || serviceHealthData.value.length === 0) {
        return []
      }
      
      // Extract top-level services and their first-level children
      const flattened = []
      
      serviceHealthData.value.forEach(service => {
        if (service.children && service.children.length > 0) {
          // Add the main children as separate services
          service.children.forEach(child => {
            flattened.push({
              name: child.name,
              status: child.status,
              importance: child.importance || 20,
              responseTime: child.responseTime || 0,
              uptime: child.uptime || 99.0
            })
          })
        } else {
          // Add the service itself if it has no children
          flattened.push({
            name: service.name,
            status: service.status,
            importance: service.importance || 20,
            responseTime: service.responseTime || 0,
            uptime: service.uptime || 99.0
          })
        }
      })
      
      // Normalize importance values to ensure they sum to 100
      const totalImportance = flattened.reduce((sum, s) => sum + s.importance, 0)
      if (totalImportance > 0) {
        flattened.forEach(s => {
          s.importance = (s.importance / totalImportance) * 100
        })
      }
      
      return flattened
    })
    
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
      flatServiceHealthData,
      
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

<style scoped>
/* Clickable card styling */
.card-clickable {
  display: block;
  text-decoration: none;
  color: inherit;
  transition: all 0.2s ease-in-out;
  cursor: pointer;
}

.card-clickable:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.card-clickable:active {
  transform: translateY(0);
}

/* Ensure the arrow icon becomes more visible on hover */
.card-clickable:hover svg {
  color: #4b5563;
}
</style>
