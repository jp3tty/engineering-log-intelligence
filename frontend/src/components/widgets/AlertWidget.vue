<template>
  <div class="alert-widget h-full flex flex-col">
    <!-- Widget Header -->
    <div class="flex items-center justify-between p-3 border-b border-gray-100">
      <div class="flex items-center space-x-2">
        <div class="flex items-center space-x-1">
          <span class="text-sm font-medium text-gray-900">{{ alerts.length }}</span>
          <span class="text-xs text-gray-500">alerts</span>
        </div>
        <div class="flex items-center space-x-1">
          <div v-for="severity in severityCounts" :key="severity.level" class="flex items-center space-x-1">
            <div :class="['w-2 h-2 rounded-full', getSeverityColor(severity.level)]"></div>
            <span class="text-xs text-gray-600">{{ severity.count }}</span>
          </div>
        </div>
      </div>
      <button
        v-if="!previewMode"
        @click="refreshAlerts"
        :disabled="loading"
        class="p-1 text-gray-400 hover:text-blue-600 transition-colors disabled:opacity-50"
        title="Refresh Alerts"
      >
        <ArrowPathIcon :class="['w-4 h-4', loading ? 'animate-spin' : '']" />
      </button>
    </div>

    <!-- Alerts List -->
    <div class="flex-1 overflow-y-auto">
      <div v-if="alerts.length === 0 && !loading" class="flex items-center justify-center h-full text-gray-500">
        <div class="text-center">
          <CheckCircleIcon class="w-8 h-8 mx-auto mb-2 text-green-500" />
          <p class="text-sm">No alerts</p>
        </div>
      </div>
      
      <div v-else class="p-3 space-y-2">
        <div
          v-for="alert in alerts"
          :key="alert.id"
          class="alert-item bg-white border border-gray-200 rounded-lg p-3 hover:shadow-sm transition-shadow"
        >
          <div class="flex items-start space-x-3">
            <!-- Severity Indicator -->
            <div :class="['w-3 h-3 rounded-full mt-1', getSeverityColor(alert.severity)]"></div>
            
            <!-- Alert Content -->
            <div class="flex-1 min-w-0">
              <div class="flex items-center justify-between mb-1">
                <h4 class="text-sm font-medium text-gray-900 truncate">{{ alert.title }}</h4>
                <span class="text-xs text-gray-500">{{ formatTime(alert.timestamp) }}</span>
              </div>
              <p class="text-xs text-gray-600 mb-2 line-clamp-2">{{ alert.description }}</p>
              <div class="flex items-center justify-between">
                <span class="text-xs text-gray-500">{{ alert.source }}</span>
                <div class="flex items-center space-x-2">
                  <button
                    v-if="!previewMode"
                    @click="acknowledgeAlert(alert.id)"
                    class="text-xs px-2 py-1 bg-blue-100 text-blue-700 rounded hover:bg-blue-200 transition-colors"
                  >
                    Acknowledge
                  </button>
                  <button
                    v-if="!previewMode"
                    @click="resolveAlert(alert.id)"
                    class="text-xs px-2 py-1 bg-green-100 text-green-700 rounded hover:bg-green-200 transition-colors"
                  >
                    Resolve
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="absolute inset-0 bg-white bg-opacity-75 flex items-center justify-center">
      <div class="text-center">
        <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600 mx-auto mb-2"></div>
        <p class="text-xs text-gray-600">Loading alerts...</p>
      </div>
    </div>

    <!-- Error State -->
    <div v-if="error" class="absolute inset-0 bg-red-50 flex items-center justify-center">
      <div class="text-center">
        <ExclamationTriangleIcon class="w-6 h-6 text-red-500 mx-auto mb-1" />
        <p class="text-xs text-red-600">{{ error }}</p>
        <button
          @click="refreshAlerts"
          class="mt-2 px-2 py-1 bg-red-100 text-red-700 rounded text-xs hover:bg-red-200 transition-colors"
        >
          Retry
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { 
  ArrowPathIcon, 
  ExclamationTriangleIcon, 
  CheckCircleIcon 
} from '@heroicons/vue/24/outline'

export default {
  name: 'AlertWidget',
  components: {
    ArrowPathIcon,
    ExclamationTriangleIcon,
    CheckCircleIcon
  },
  props: {
    widget: {
      type: Object,
      required: true
    },
    previewMode: {
      type: Boolean,
      default: false
    }
  },
  emits: ['update-widget'],
  setup(props, { emit }) {
    const alerts = ref([])
    const loading = ref(false)
    const error = ref(null)
    const refreshInterval = ref(null)

    // Computed properties
    const severityCounts = computed(() => {
      const counts = {
        critical: 0,
        high: 0,
        medium: 0,
        low: 0
      }
      
      alerts.value.forEach(alert => {
        if (counts.hasOwnProperty(alert.severity)) {
          counts[alert.severity]++
        }
      })
      
      return Object.entries(counts).map(([level, count]) => ({ level, count }))
    })

    // Methods
    const getSeverityColor = (severity) => {
      const colors = {
        critical: 'bg-red-500',
        high: 'bg-orange-500',
        medium: 'bg-yellow-500',
        low: 'bg-blue-500'
      }
      return colors[severity] || 'bg-gray-500'
    }

    const formatTime = (timestamp) => {
      const date = new Date(timestamp)
      const now = new Date()
      const diff = now - date
      
      if (diff < 60000) { // Less than 1 minute
        return 'Just now'
      } else if (diff < 3600000) { // Less than 1 hour
        return `${Math.floor(diff / 60000)}m ago`
      } else if (diff < 86400000) { // Less than 1 day
        return `${Math.floor(diff / 3600000)}h ago`
      } else {
        return date.toLocaleDateString()
      }
    }

    const generateMockAlerts = () => {
      const severities = ['critical', 'high', 'medium', 'low']
      const sources = ['System', 'Application', 'Database', 'Network', 'Security']
      const titles = [
        'High CPU usage detected',
        'Database connection timeout',
        'Memory usage exceeded threshold',
        'Network latency spike',
        'Failed authentication attempt',
        'Disk space running low',
        'Service unavailable',
        'SSL certificate expired'
      ]
      
      const mockAlerts = []
      const limit = props.widget.config.limit || 10
      const severityFilter = props.widget.config.severity || 'all'
      
      for (let i = 0; i < Math.min(limit, 8); i++) {
        const severity = severities[Math.floor(Math.random() * severities.length)]
        
        // Apply severity filter
        if (severityFilter !== 'all') {
          if (severityFilter === 'critical' && severity !== 'critical') continue
          if (severityFilter === 'high' && !['critical', 'high'].includes(severity)) continue
          if (severityFilter === 'medium' && !['critical', 'high', 'medium'].includes(severity)) continue
        }
        
        mockAlerts.push({
          id: `alert-${Date.now()}-${i}`,
          title: titles[Math.floor(Math.random() * titles.length)],
          description: `This is a sample alert description for ${severity} severity level. It provides additional context about the issue.`,
          severity,
          source: sources[Math.floor(Math.random() * sources.length)],
          timestamp: new Date(Date.now() - Math.random() * 86400000), // Random time in last 24 hours
          status: 'open'
        })
      }
      
      return mockAlerts
    }

    const fetchAlerts = async () => {
      if (props.previewMode) return
      
      loading.value = true
      error.value = null
      
      try {
        // Simulate API call with shorter timeout
        await new Promise(resolve => setTimeout(resolve, 300))
        
        // Generate mock alerts
        const newAlerts = generateMockAlerts()
        alerts.value = newAlerts
        
        // Emit update to parent (with error handling)
        try {
          emit('update-widget', props.widget.id, { 
            data: newAlerts,
            lastUpdated: new Date()
          })
        } catch (emitError) {
          console.warn('Failed to emit alert update:', emitError)
        }
        
      } catch (err) {
        error.value = 'Failed to fetch alerts'
        console.error('Error fetching alerts:', err)
        
        // Provide fallback data
        const fallbackAlerts = generateMockAlerts()
        alerts.value = fallbackAlerts
      } finally {
        loading.value = false
      }
    }

    const refreshAlerts = () => {
      fetchAlerts()
    }

    const acknowledgeAlert = (alertId) => {
      const alert = alerts.value.find(a => a.id === alertId)
      if (alert) {
        alert.status = 'acknowledged'
        // Here you would make an API call to acknowledge the alert
        console.log('Acknowledging alert:', alertId)
      }
    }

    const resolveAlert = (alertId) => {
      const alert = alerts.value.find(a => a.id === alertId)
      if (alert) {
        alert.status = 'resolved'
        // Here you would make an API call to resolve the alert
        console.log('Resolving alert:', alertId)
      }
    }

    const startAutoRefresh = () => {
      if (props.previewMode) return
      
      const interval = props.widget.config.refreshInterval || 30
      refreshInterval.value = setInterval(fetchAlerts, interval * 1000)
    }

    const stopAutoRefresh = () => {
      if (refreshInterval.value) {
        clearInterval(refreshInterval.value)
        refreshInterval.value = null
      }
    }

    // Lifecycle
    onMounted(() => {
      if (!props.previewMode) {
        fetchAlerts()
        startAutoRefresh()
      } else {
        // Show mock data in preview mode
        alerts.value = generateMockAlerts()
      }
    })

    onUnmounted(() => {
      stopAutoRefresh()
    })

    return {
      alerts,
      loading,
      error,
      severityCounts,
      getSeverityColor,
      formatTime,
      refreshAlerts,
      acknowledgeAlert,
      resolveAlert
    }
  }
}
</script>

<style scoped>
.alert-widget {
  position: relative;
}

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
