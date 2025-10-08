<template>
  <div class="log-widget h-full flex flex-col">
    <!-- Widget Header -->
    <div class="flex items-center justify-between p-3 border-b border-gray-100">
      <div class="flex items-center space-x-2">
        <div class="flex items-center space-x-1">
          <span class="text-sm font-medium text-gray-900">{{ logs.length }}</span>
          <span class="text-xs text-gray-500">entries</span>
        </div>
        <div class="flex items-center space-x-1">
          <div v-for="level in levelCounts" :key="level.level" class="flex items-center space-x-1">
            <div :class="['w-2 h-2 rounded-full', getLevelColor(level.level)]"></div>
            <span class="text-xs text-gray-600">{{ level.count }}</span>
          </div>
        </div>
      </div>
      <div class="flex items-center space-x-2">
        <select
          v-model="localLogLevel"
          @change="updateLogLevel"
          class="text-xs border border-gray-300 rounded px-2 py-1 focus:outline-none focus:ring-1 focus:ring-blue-500"
        >
          <option value="all">All</option>
          <option value="error">Error</option>
          <option value="warning">Warning</option>
          <option value="info">Info</option>
          <option value="debug">Debug</option>
        </select>
        <button
          v-if="!previewMode"
          @click="refreshLogs"
          :disabled="loading"
          class="p-1 text-gray-400 hover:text-blue-600 transition-colors disabled:opacity-50"
          title="Refresh Logs"
        >
          <ArrowPathIcon :class="['w-4 h-4', loading ? 'animate-spin' : '']" />
        </button>
      </div>
    </div>

    <!-- Logs List -->
    <div class="flex-1 overflow-y-auto">
      <div v-if="logs.length === 0 && !loading" class="flex items-center justify-center h-full text-gray-500">
        <div class="text-center">
          <DocumentTextIcon class="w-8 h-8 mx-auto mb-2 text-gray-400" />
          <p class="text-sm">No logs available</p>
        </div>
      </div>
      
      <div v-else class="p-3 space-y-1">
        <div
          v-for="log in logs"
          :key="log.id"
          class="log-entry bg-white border border-gray-200 rounded p-2 hover:shadow-sm transition-shadow"
        >
          <div class="flex items-start space-x-3">
            <!-- Log Level Indicator -->
            <div :class="['w-2 h-2 rounded-full mt-2', getLevelColor(log.level)]"></div>
            
            <!-- Log Content -->
            <div class="flex-1 min-w-0">
              <div class="flex items-center justify-between mb-1">
                <div class="flex items-center space-x-2">
                  <span class="text-xs font-medium text-gray-900">{{ log.level.toUpperCase() }}</span>
                  <span class="text-xs text-gray-500">{{ log.source }}</span>
                </div>
                <span class="text-xs text-gray-500">{{ formatTime(log.timestamp) }}</span>
              </div>
              <p class="text-xs text-gray-700 mb-1">{{ log.message }}</p>
              <div v-if="log.details" class="text-xs text-gray-600 bg-gray-50 p-2 rounded">
                {{ log.details }}
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
        <p class="text-xs text-gray-600">Loading logs...</p>
      </div>
    </div>

    <!-- Error State -->
    <div v-if="error" class="absolute inset-0 bg-red-50 flex items-center justify-center">
      <div class="text-center">
        <ExclamationTriangleIcon class="w-6 h-6 text-red-500 mx-auto mb-1" />
        <p class="text-xs text-red-600">{{ error }}</p>
        <button
          @click="refreshLogs"
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
  DocumentTextIcon 
} from '@heroicons/vue/24/outline'

export default {
  name: 'LogWidget',
  components: {
    ArrowPathIcon,
    ExclamationTriangleIcon,
    DocumentTextIcon
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
    const logs = ref([])
    const loading = ref(false)
    const error = ref(null)
    const refreshInterval = ref(null)
    const localLogLevel = ref(props.widget.config.logLevel || 'all')

    // Computed properties
    const levelCounts = computed(() => {
      const counts = {
        error: 0,
        warning: 0,
        info: 0,
        debug: 0
      }
      
      logs.value.forEach(log => {
        if (counts.hasOwnProperty(log.level)) {
          counts[log.level]++
        }
      })
      
      return Object.entries(counts).map(([level, count]) => ({ level, count }))
    })

    // Methods
    const getLevelColor = (level) => {
      const colors = {
        error: 'bg-red-500',
        warning: 'bg-yellow-500',
        info: 'bg-blue-500',
        debug: 'bg-gray-500'
      }
      return colors[level] || 'bg-gray-500'
    }

    const formatTime = (timestamp) => {
      const date = new Date(timestamp)
      return date.toLocaleTimeString()
    }

    const generateMockLogs = () => {
      const levels = ['error', 'warning', 'info', 'debug']
      const sources = ['app', 'db', 'api', 'auth', 'cache', 'queue']
      const messages = [
        'Database connection established',
        'User authentication successful',
        'Cache hit for key: user_profile_123',
        'API request processed in 150ms',
        'Failed to connect to external service',
        'Memory usage at 85%',
        'Queue processing started',
        'SSL handshake completed',
        'File upload completed',
        'Background job finished'
      ]
      
      const mockLogs = []
      const limit = props.widget.config.limit || 50
      const levelFilter = localLogLevel.value
      
      for (let i = 0; i < Math.min(limit, 20); i++) {
        const level = levels[Math.floor(Math.random() * levels.length)]
        
        // Apply level filter
        if (levelFilter !== 'all' && level !== levelFilter) continue
        
        mockLogs.push({
          id: `log-${Date.now()}-${i}`,
          level,
          source: sources[Math.floor(Math.random() * sources.length)],
          message: messages[Math.floor(Math.random() * messages.length)],
          details: level === 'error' ? 'Stack trace and additional error details would appear here.' : null,
          timestamp: new Date(Date.now() - Math.random() * 3600000), // Random time in last hour
          metadata: {
            userId: Math.floor(Math.random() * 1000),
            sessionId: `session-${Math.random().toString(36).substr(2, 9)}`
          }
        })
      }
      
      // Sort by timestamp (newest first)
      return mockLogs.sort((a, b) => b.timestamp - a.timestamp)
    }

    const fetchLogs = async () => {
      if (props.previewMode) return
      
      loading.value = true
      error.value = null
      
      try {
        // Simulate API call with shorter timeout
        await new Promise(resolve => setTimeout(resolve, 300))
        
        // Generate mock logs
        const newLogs = generateMockLogs()
        logs.value = newLogs
        
        // Emit update to parent (with error handling)
        try {
          emit('update-widget', props.widget.id, { 
            data: newLogs,
            lastUpdated: new Date()
          })
        } catch (emitError) {
          console.warn('Failed to emit log update:', emitError)
        }
        
      } catch (err) {
        error.value = 'Failed to fetch logs'
        console.error('Error fetching logs:', err)
        
        // Provide fallback data
        const fallbackLogs = generateMockLogs()
        logs.value = fallbackLogs
      } finally {
        loading.value = false
      }
    }

    const refreshLogs = () => {
      fetchLogs()
    }

    const updateLogLevel = () => {
      props.widget.config.logLevel = localLogLevel.value
      fetchLogs()
    }

    const startAutoRefresh = () => {
      if (props.previewMode) return
      
      const interval = props.widget.config.refreshInterval || 30
      refreshInterval.value = setInterval(fetchLogs, interval * 1000)
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
        fetchLogs()
        startAutoRefresh()
      } else {
        // Show mock data in preview mode
        logs.value = generateMockLogs()
      }
    })

    onUnmounted(() => {
      stopAutoRefresh()
    })

    return {
      logs,
      loading,
      error,
      localLogLevel,
      levelCounts,
      getLevelColor,
      formatTime,
      refreshLogs,
      updateLogLevel
    }
  }
}
</script>

<style scoped>
.log-widget {
  position: relative;
}

.log-entry {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
}
</style>
