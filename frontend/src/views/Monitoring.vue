<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Page Header -->
    <div class="bg-white shadow-sm border-b border-gray-200">
      <div class="container-custom py-6">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-2xl font-bold text-gray-900">Advanced Monitoring</h1>
            <p class="text-gray-600 mt-1">Detailed system monitoring, alerts, and resource tracking</p>
          </div>
          <button
            @click="refreshData"
            :disabled="loading"
            class="btn btn-outline"
          >
            <svg class="w-4 h-4 mr-2" :class="{ 'animate-spin': loading }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            {{ loading ? 'Refreshing...' : 'Refresh' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="container-custom py-8">
      <!-- Loading State -->
      <div v-if="loading && !monitoringData" class="flex justify-center py-12">
        <div class="spinner w-12 h-12"></div>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="card">
        <div class="card-body">
          <div class="text-center py-8 text-red-600">
            <p>⚠️ {{ error }}</p>
            <button @click="refreshData" class="btn btn-primary mt-4">Retry</button>
          </div>
        </div>
      </div>

      <!-- Monitoring Dashboard -->
      <div v-else-if="monitoringData" class="space-y-8">
        <!-- Resource Usage Metrics -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <!-- Database Resources -->
          <div class="card">
            <div class="card-header">
              <h3 class="text-lg font-semibold text-gray-900">📦 Database Resources</h3>
            </div>
            <div class="card-body space-y-4">
              <div>
                <div class="flex justify-between mb-1">
                  <span class="text-sm font-medium text-gray-600">Database Size</span>
                  <span class="text-sm font-semibold text-gray-900">{{ monitoringData.resources.database.size_formatted }}</span>
                </div>
                <div class="text-xs text-gray-500">
                  {{ monitoringData.resources.database.total_logs.toLocaleString() }} total logs • 
                  Max: {{ monitoringData.resources.database.max_size_formatted }}
                  <span v-if="monitoringData.resources.database.usage_percent" class="ml-1" :class="getUsageColorClass(monitoringData.resources.database.usage_percent)">
                    ({{ monitoringData.resources.database.usage_percent }}% used)
                  </span>
                </div>
              </div>
              
              <div>
                <div class="flex justify-between mb-1">
                  <span class="text-sm font-medium text-gray-600">Growth Rate</span>
                  <span class="text-sm font-semibold text-gray-900">{{ monitoringData.resources.database.growth_rate }}</span>
                </div>
                <div class="text-xs text-gray-500">{{ monitoringData.resources.throughput.logs_per_hour.toLocaleString() }} logs/hour</div>
              </div>
              
              <div>
                <div class="flex justify-between mb-1">
                  <span class="text-sm font-medium text-gray-600">ML Predictions</span>
                  <span class="text-sm font-semibold" :class="monitoringData.resources.ml_predictions.status === 'active' ? 'text-green-600' : 'text-gray-400'">
                    {{ monitoringData.resources.ml_predictions.count_24h.toLocaleString() }} (24h)
                  </span>
                </div>
                <div class="text-xs" :class="monitoringData.resources.ml_predictions.status === 'active' ? 'text-green-600' : 'text-gray-400'">
                  Status: {{ monitoringData.resources.ml_predictions.status }}
                </div>
              </div>
            </div>
          </div>

          <!-- Response Time Percentiles -->
          <div class="card">
            <div class="card-header">
              <h3 class="text-lg font-semibold text-gray-900">⚡ Response Time Distribution</h3>
            </div>
            <div class="card-body space-y-4">
              <div class="grid grid-cols-3 gap-4 mb-4">
                <div class="text-center p-3 bg-blue-50 rounded-lg">
                  <div class="text-2xl font-bold text-blue-600">{{ Math.round(monitoringData.percentiles.p50) }}ms</div>
                  <div class="text-xs text-gray-600">p50 (median)</div>
                </div>
                <div class="text-center p-3 bg-yellow-50 rounded-lg">
                  <div class="text-2xl font-bold text-yellow-600">{{ Math.round(monitoringData.percentiles.p95) }}ms</div>
                  <div class="text-xs text-gray-600">p95</div>
                </div>
                <div class="text-center p-3 bg-red-50 rounded-lg">
                  <div class="text-2xl font-bold text-red-600">{{ Math.round(monitoringData.percentiles.p99) }}ms</div>
                  <div class="text-xs text-gray-600">p99 (slowest)</div>
                </div>
              </div>
              
              <div class="space-y-2 text-sm">
                <div class="flex justify-between">
                  <span class="text-gray-600">Min:</span>
                  <span class="font-semibold">{{ Math.round(monitoringData.percentiles.min) }}ms</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-gray-600">Average:</span>
                  <span class="font-semibold">{{ Math.round(monitoringData.percentiles.avg) }}ms</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-gray-600">Max:</span>
                  <span class="font-semibold">{{ Math.round(monitoringData.percentiles.max) }}ms</span>
                </div>
                <div class="flex justify-between pt-2 border-t">
                  <span class="text-gray-600">Total Requests:</span>
                  <span class="font-semibold">{{ monitoringData.percentiles.total_requests.toLocaleString() }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- ML Anomaly Alerts -->
        <div v-if="monitoringData.ml_alerts && monitoringData.ml_alerts.length > 0" class="card">
          <div class="card-header">
            <h3 class="text-lg font-semibold text-gray-900">🤖 High-Severity ML Anomaly Alerts (Last 24h)</h3>
            <p class="text-sm text-gray-600 mt-1">{{ monitoringData.ml_alerts.length }} anomalies detected by machine learning</p>
          </div>
          <div class="card-body">
            <div class="overflow-x-auto">
              <table class="w-full">
                <thead class="bg-gray-50">
                  <tr>
                    <th class="px-4 py-3 text-left text-xs font-medium text-gray-600 uppercase">Time</th>
                    <th class="px-4 py-3 text-left text-xs font-medium text-gray-600 uppercase">Source</th>
                    <th class="px-4 py-3 text-left text-xs font-medium text-gray-600 uppercase">Message</th>
                    <th class="px-4 py-3 text-left text-xs font-medium text-gray-600 uppercase">Severity</th>
                    <th class="px-4 py-3 text-left text-xs font-medium text-gray-600 uppercase">Confidence</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-gray-200">
                  <tr v-for="alert in monitoringData.ml_alerts.slice(0, 10)" :key="alert.log_id" class="hover:bg-gray-50">
                    <td class="px-4 py-3 text-sm text-gray-900">{{ formatTime(alert.timestamp) }}</td>
                    <td class="px-4 py-3">
                      <div class="text-sm">
                        <div class="font-medium text-gray-900">{{ alert.source_type }}</div>
                        <div class="text-gray-500">{{ alert.host }}</div>
                      </div>
                    </td>
                    <td class="px-4 py-3 text-sm text-gray-900 max-w-md truncate">{{ alert.message }}</td>
                    <td class="px-4 py-3">
                      <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                        {{ alert.severity }}
                      </span>
                    </td>
                    <td class="px-4 py-3 text-sm font-semibold text-gray-900">{{ (alert.anomaly_score * 100).toFixed(0) }}%</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- Recent Incidents Feed -->
        <div class="card">
          <div class="card-header">
            <h3 class="text-lg font-semibold text-gray-900">🚨 Recent Incidents (Last 24h)</h3>
            <p class="text-sm text-gray-600 mt-1">{{ monitoringData.incidents.length }} FATAL & ERROR events</p>
          </div>
          <div class="card-body">
            <div class="space-y-3">
              <div
                v-for="incident in monitoringData.incidents.slice(0, 15)"
                :key="incident.log_id"
                class="border-l-4 pl-4 py-2"
                :class="incident.level === 'FATAL' ? 'border-red-600 bg-red-50' : 'border-orange-500 bg-orange-50'"
              >
                <div class="flex items-start justify-between">
                  <div class="flex-1">
                    <div class="flex items-center gap-2 mb-1">
                      <span
                        class="px-2 py-0.5 rounded text-xs font-semibold"
                        :class="incident.level === 'FATAL' ? 'bg-red-600 text-white' : 'bg-orange-600 text-white'"
                      >
                        {{ incident.level }}
                      </span>
                      <span class="text-sm text-gray-600">{{ formatTime(incident.timestamp) }}</span>
                      <span class="text-sm text-gray-500">• {{ incident.source_type }}</span>
                    </div>
                    <p class="text-sm text-gray-900 font-medium">{{ incident.message }}</p>
                    <div class="mt-1 flex items-center gap-4 text-xs text-gray-600">
                      <span>Host: {{ incident.host }}</span>
                      <span>Service: {{ incident.service }}</span>
                      <span v-if="incident.response_time_ms">Response: {{ incident.response_time_ms }}ms</span>
                      <span v-if="incident.http_status">HTTP: {{ incident.http_status }}</span>
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
</template>

<script>
import { ref, onMounted } from 'vue'

export default {
  name: 'Monitoring',
  setup() {
    const monitoringData = ref(null)
    const loading = ref(false)
    const error = ref(null)

    const fetchMonitoringData = async () => {
      loading.value = true
      error.value = null
      
      try {
        const response = await fetch('/api/monitoring')
        const data = await response.json()
        
        if (data.success) {
          monitoringData.value = data.data
          console.log('✅ Monitoring data loaded:', data.data)
        } else {
          throw new Error(data.error || 'Failed to fetch monitoring data')
        }
      } catch (err) {
        console.error('❌ Error fetching monitoring data:', err)
        error.value = err.message || 'Failed to load monitoring data'
      } finally {
        loading.value = false
      }
    }

    const refreshData = () => {
      fetchMonitoringData()
    }

    const formatTime = (timestamp) => {
      const date = new Date(timestamp)
      const now = new Date()
      const diffMs = now - date
      const diffMins = Math.floor(diffMs / 60000)
      
      if (diffMins < 1) return 'Just now'
      if (diffMins < 60) return `${diffMins}m ago`
      const diffHours = Math.floor(diffMins / 60)
      if (diffHours < 24) return `${diffHours}h ago`
      return date.toLocaleString()
    }

    const getUsageColorClass = (percent) => {
      if (percent >= 90) return 'text-red-600 font-semibold'
      if (percent >= 75) return 'text-orange-600'
      if (percent >= 50) return 'text-yellow-600'
      return 'text-green-600'
    }

    onMounted(() => {
      fetchMonitoringData()
      
      // Auto-refresh every 30 seconds
      setInterval(fetchMonitoringData, 30000)
    })

    return {
      monitoringData,
      loading,
      error,
      refreshData,
      formatTime,
      getUsageColorClass
    }
  }
}
</script>
