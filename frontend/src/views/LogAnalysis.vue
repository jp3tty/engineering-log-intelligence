<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Page Header -->
    <div class="bg-white shadow-sm border-b border-gray-200">
      <div class="container-custom py-6">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-2xl font-bold text-gray-900">Log Analysis</h1>
            <p class="text-gray-600 mt-1">AI-powered log search and analysis</p>
          </div>
          <div class="flex items-center space-x-3">
            <button
              @click="refreshLogs"
              :disabled="isLoading"
              class="btn btn-secondary flex items-center space-x-2"
            >
              <ArrowPathIcon :class="['w-4 h-4', { 'animate-spin': isLoading }]" />
              <span>Refresh</span>
            </button>
            <button
              @click="exportResults"
              :disabled="!searchResults.length"
              class="btn btn-primary flex items-center space-x-2"
            >
              <ArrowDownTrayIcon class="w-4 h-4" />
              <span>Export</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="container-custom py-8">
      <!-- Search and Filters -->
      <div class="grid grid-cols-1 lg:grid-cols-4 gap-6 mb-8">
        <!-- Search Panel -->
        <div class="lg:col-span-3">
          <div class="card">
            <div class="card-header">
              <h3 class="text-lg font-semibold text-gray-900">Search & Analysis</h3>
            </div>
            <div class="card-body space-y-4">
              <!-- Search Input -->
              <div class="relative">
                <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <MagnifyingGlassIcon class="h-5 w-5 text-gray-400" />
                </div>
                <input
                  v-model="searchQuery"
                  @input="debouncedSearch"
                  type="text"
                  placeholder="Search logs... (supports regex and filters)"
                  class="input pl-10"
                />
              </div>

              <!-- Filters Row -->
              <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Time Range</label>
                  <select v-model="timeRange" class="select">
                    <option value="1h">Last Hour</option>
                    <option value="6h">Last 6 Hours</option>
                    <option value="24h">Last 24 Hours</option>
                    <option value="7d">Last 7 Days</option>
                    <option value="30d">Last 30 Days</option>
                    <option value="custom">Custom Range</option>
                  </select>
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Log Level</label>
                  <select v-model="logLevel" class="select">
                    <option value="">All Levels</option>
                    <option value="DEBUG">DEBUG</option>
                    <option value="INFO">INFO</option>
                    <option value="WARN">WARN</option>
                    <option value="ERROR">ERROR</option>
                    <option value="FATAL">FATAL</option>
                  </select>
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Source System</label>
                  <select v-model="sourceSystem" class="select">
                    <option value="">All Systems</option>
                    <option value="SPLUNK">SPLUNK</option>
                    <option value="SAP">SAP</option>
                    <option value="APPLICATION">Application</option>
                    <option value="SYSTEM">System</option>
                  </select>
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">AI Analysis</label>
                  <select v-model="aiAnalysisType" class="select">
                    <option value="">No AI Analysis</option>
                    <option value="anomaly">Anomaly Detection</option>
                    <option value="classification">Log Classification</option>
                    <option value="sentiment">Sentiment Analysis</option>
                    <option value="correlation">Pattern Correlation</option>
                  </select>
                </div>
              </div>

              <!-- Search Actions -->
              <div class="flex items-center justify-between">
                <div class="flex items-center space-x-4">
                  <button
                    @click="performSearch"
                    :disabled="isLoading"
                    class="btn btn-primary flex items-center space-x-2"
                  >
                    <MagnifyingGlassIcon class="w-4 h-4" />
                    <span>{{ isLoading ? 'Analyzing...' : 'Search & Analyze' }}</span>
                  </button>
                  <button
                    @click="clearFilters"
                    class="btn btn-secondary"
                  >
                    Clear Filters
                  </button>
                </div>
                <div class="text-sm text-gray-500">
                  {{ searchResults.length }} results found
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- AI Insights Panel -->
        <div class="lg:col-span-1">
          <div class="card">
            <div class="card-header">
              <h3 class="text-lg font-semibold text-gray-900">AI Insights</h3>
            </div>
            <div class="card-body">
              <div v-if="aiInsights.length === 0" class="text-center py-4">
                <LightBulbIcon class="w-8 h-8 text-gray-400 mx-auto mb-2" />
                <p class="text-sm text-gray-500">Run analysis to see AI insights</p>
              </div>
              <div v-else class="space-y-3">
                <div
                  v-for="insight in aiInsights"
                  :key="insight.id"
                  class="p-3 bg-blue-50 border border-blue-200 rounded-lg"
                >
                  <div class="flex items-start space-x-2">
                    <ExclamationTriangleIcon class="w-4 h-4 text-blue-600 mt-0.5 flex-shrink-0" />
                    <div>
                      <p class="text-sm font-medium text-blue-900">{{ insight.title }}</p>
                      <p class="text-xs text-blue-700 mt-1">{{ insight.description }}</p>
                      <span class="inline-block mt-2 text-xs px-2 py-1 bg-blue-100 text-blue-800 rounded">
                        {{ insight.severity }}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Search Results -->
      <div v-if="searchResults.length > 0" class="card">
        <div class="card-header">
          <div class="flex items-center justify-between">
            <h3 class="text-lg font-semibold text-gray-900">Search Results</h3>
            <div class="flex items-center space-x-2">
              <span class="text-sm text-gray-500">{{ searchResults.length }} logs</span>
              <select v-model="sortBy" class="select text-sm">
                <option value="timestamp">Sort by Time</option>
                <option value="level">Sort by Level</option>
                <option value="source">Sort by Source</option>
                <option value="relevance">Sort by Relevance</option>
              </select>
            </div>
          </div>
        </div>
        <div class="card-body p-0">
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Timestamp
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Level
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Source
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Message
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    AI Analysis
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr
                  v-for="log in paginatedResults"
                  :key="log.id"
                  class="hover:bg-gray-50 cursor-pointer"
                  @click="selectLog(log)"
                >
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {{ formatTimestamp(log.timestamp) }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap">
                    <span :class="getLevelBadgeClass(log.level)" class="inline-flex px-2 py-1 text-xs font-semibold rounded-full">
                      {{ log.level }}
                    </span>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {{ log.source }}
                  </td>
                  <td class="px-6 py-4 text-sm text-gray-900 max-w-xs truncate">
                    {{ log.message }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap">
                    <div v-if="log.aiAnalysis" class="flex items-center space-x-2">
                      <span v-if="log.aiAnalysis.anomaly" class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
                        <ExclamationTriangleIcon class="w-3 h-3 mr-1" />
                        Anomaly
                      </span>
                      <span v-if="log.aiAnalysis.category" class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                        {{ log.aiAnalysis.category }}
                      </span>
                    </div>
                    <span v-else class="text-gray-400 text-xs">No analysis</span>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <button
                      @click.stop="analyzeLog(log)"
                      class="text-blue-600 hover:text-blue-900 mr-3"
                    >
                      Analyze
                    </button>
                    <button
                      @click.stop="viewLogDetails(log)"
                      class="text-gray-600 hover:text-gray-900"
                    >
                      View
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Pagination -->
          <div class="bg-white px-4 py-3 border-t border-gray-200 sm:px-6">
            <div class="flex items-center justify-between">
              <div class="flex items-center">
                <span class="text-sm text-gray-700">
                  Showing {{ (currentPage - 1) * pageSize + 1 }} to {{ Math.min(currentPage * pageSize, searchResults.length) }} of {{ searchResults.length }} results
                </span>
              </div>
              <div class="flex items-center space-x-2">
                <button
                  @click="currentPage = Math.max(1, currentPage - 1)"
                  :disabled="currentPage === 1"
                  class="btn btn-secondary btn-sm"
                >
                  Previous
                </button>
                <span class="text-sm text-gray-700">
                  Page {{ currentPage }} of {{ totalPages }}
                </span>
                <button
                  @click="currentPage = Math.min(totalPages, currentPage + 1)"
                  :disabled="currentPage === totalPages"
                  class="btn btn-secondary btn-sm"
                >
                  Next
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else-if="!isLoading" class="card">
        <div class="card-body">
          <div class="text-center py-12">
            <DocumentTextIcon class="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 class="text-lg font-medium text-gray-900 mb-2">No logs found</h3>
            <p class="text-gray-500">Try adjusting your search criteria or filters</p>
          </div>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="isLoading" class="card">
        <div class="card-body">
          <div class="text-center py-12">
            <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p class="text-gray-500">Analyzing logs with AI...</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Log Details Modal -->
    <div v-if="selectedLog" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div class="relative top-20 mx-auto p-5 border w-11/12 md:w-3/4 lg:w-1/2 shadow-lg rounded-md bg-white">
        <div class="mt-3">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-medium text-gray-900">Log Details</h3>
            <button @click="selectedLog = null" class="text-gray-400 hover:text-gray-600">
              <XMarkIcon class="w-6 h-6" />
            </button>
          </div>
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700">Timestamp</label>
              <p class="mt-1 text-sm text-gray-900">{{ formatTimestamp(selectedLog.timestamp) }}</p>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700">Level</label>
              <span :class="getLevelBadgeClass(selectedLog.level)" class="inline-flex px-2 py-1 text-xs font-semibold rounded-full">
                {{ selectedLog.level }}
              </span>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700">Source</label>
              <p class="mt-1 text-sm text-gray-900">{{ selectedLog.source }}</p>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700">Message</label>
              <p class="mt-1 text-sm text-gray-900 bg-gray-50 p-3 rounded border font-mono">{{ selectedLog.message }}</p>
            </div>
            <div v-if="selectedLog.aiAnalysis">
              <label class="block text-sm font-medium text-gray-700">AI Analysis</label>
              <div class="mt-1 p-3 bg-blue-50 rounded border">
                <pre class="text-sm text-gray-900">{{ JSON.stringify(selectedLog.aiAnalysis, null, 2) }}</pre>
              </div>
            </div>
          </div>
          <div class="mt-6 flex justify-end space-x-3">
            <button @click="analyzeLog(selectedLog)" class="btn btn-primary">
              Run AI Analysis
            </button>
            <button @click="selectedLog = null" class="btn btn-secondary">
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useNotificationStore } from '@/stores/notifications'
import {
  MagnifyingGlassIcon,
  ArrowPathIcon,
  ArrowDownTrayIcon,
  LightBulbIcon,
  ExclamationTriangleIcon,
  DocumentTextIcon,
  XMarkIcon
} from '@heroicons/vue/24/outline'

export default {
  name: 'LogAnalysis',
  components: {
    MagnifyingGlassIcon,
    ArrowPathIcon,
    ArrowDownTrayIcon,
    LightBulbIcon,
    ExclamationTriangleIcon,
    DocumentTextIcon,
    XMarkIcon
  },
  setup() {
    const notificationStore = useNotificationStore()

    // Reactive state
    const isLoading = ref(false)
    const searchQuery = ref('')
    const timeRange = ref('24h')
    const logLevel = ref('')
    const sourceSystem = ref('')
    const aiAnalysisType = ref('')
    const sortBy = ref('timestamp')
    const currentPage = ref(1)
    const pageSize = ref(20)
    const selectedLog = ref(null)

    // Search results and AI insights
    const searchResults = ref([])
    const aiInsights = ref([])

    // Sample log data (in real app, this would come from API)
    const sampleLogs = ref([
      {
        id: 1,
        timestamp: new Date(Date.now() - 1000 * 60 * 5).toISOString(),
        level: 'ERROR',
        source: 'APPLICATION',
        message: 'Database connection failed: Connection timeout after 30 seconds',
        aiAnalysis: null
      },
      {
        id: 2,
        timestamp: new Date(Date.now() - 1000 * 60 * 15).toISOString(),
        level: 'WARN',
        source: 'SPLUNK',
        message: 'High CPU usage detected on server-01: 95% utilization',
        aiAnalysis: { category: 'Performance', anomaly: true }
      },
      {
        id: 3,
        timestamp: new Date(Date.now() - 1000 * 60 * 30).toISOString(),
        level: 'INFO',
        source: 'SAP',
        message: 'User authentication successful for user: admin@company.com',
        aiAnalysis: null
      },
      {
        id: 4,
        timestamp: new Date(Date.now() - 1000 * 60 * 45).toISOString(),
        level: 'DEBUG',
        source: 'APPLICATION',
        message: 'Processing batch job: 1,250 records processed successfully',
        aiAnalysis: null
      },
      {
        id: 5,
        timestamp: new Date(Date.now() - 1000 * 60 * 60).toISOString(),
        level: 'FATAL',
        source: 'SYSTEM',
        message: 'Out of memory error: Unable to allocate 512MB for process',
        aiAnalysis: { category: 'Critical Error', anomaly: true, severity: 'high' }
      }
    ])

    // Computed properties
    const totalPages = computed(() => Math.ceil(searchResults.value.length / pageSize.value))
    
    const paginatedResults = computed(() => {
      const start = (currentPage.value - 1) * pageSize.value
      const end = start + pageSize.value
      return searchResults.value.slice(start, end)
    })

    // Methods
    const debouncedSearch = debounce(() => {
      performSearch()
    }, 500)

    const performSearch = async () => {
      isLoading.value = true
      try {
        // Simulate API call delay
        await new Promise(resolve => setTimeout(resolve, 1500))
        
        // Filter sample logs based on search criteria
        let filteredLogs = sampleLogs.value.filter(log => {
          // Text search
          if (searchQuery.value && !log.message.toLowerCase().includes(searchQuery.value.toLowerCase())) {
            return false
          }
          
          // Level filter
          if (logLevel.value && log.level !== logLevel.value) {
            return false
          }
          
          // Source filter
          if (sourceSystem.value && log.source !== sourceSystem.value) {
            return false
          }
          
          return true
        })

        // Sort results
        filteredLogs.sort((a, b) => {
          switch (sortBy.value) {
            case 'timestamp':
              return new Date(b.timestamp) - new Date(a.timestamp)
            case 'level':
              const levelOrder = { 'FATAL': 0, 'ERROR': 1, 'WARN': 2, 'INFO': 3, 'DEBUG': 4 }
              return levelOrder[a.level] - levelOrder[b.level]
            case 'source':
              return a.source.localeCompare(b.source)
            default:
              return 0
          }
        })

        searchResults.value = filteredLogs
        
        // Generate AI insights if analysis type is selected
        if (aiAnalysisType.value) {
          generateAIInsights(filteredLogs)
        }
        
        notificationStore.addNotification({
          type: 'success',
          title: 'Search Complete',
          message: `Found ${filteredLogs.length} logs matching your criteria`
        })
        
      } catch (error) {
        console.error('Search error:', error)
        notificationStore.addNotification({
          type: 'error',
          title: 'Search Failed',
          message: 'Unable to search logs. Please try again.'
        })
      } finally {
        isLoading.value = false
      }
    }

    const generateAIInsights = (logs) => {
      const insights = []
      
      // Count anomalies
      const anomalies = logs.filter(log => log.aiAnalysis?.anomaly)
      if (anomalies.length > 0) {
        insights.push({
          id: 1,
          title: 'Anomaly Detection',
          description: `Found ${anomalies.length} anomalous log entries that require attention`,
          severity: anomalies.length > 3 ? 'High' : 'Medium'
        })
      }
      
      // Error pattern analysis
      const errors = logs.filter(log => log.level === 'ERROR' || log.level === 'FATAL')
      if (errors.length > 5) {
        insights.push({
          id: 2,
          title: 'Error Spike Detected',
          description: `High number of errors (${errors.length}) detected in the selected time range`,
          severity: 'High'
        })
      }
      
      // Performance issues
      const performanceLogs = logs.filter(log => 
        log.message.toLowerCase().includes('cpu') || 
        log.message.toLowerCase().includes('memory') ||
        log.message.toLowerCase().includes('timeout')
      )
      if (performanceLogs.length > 0) {
        insights.push({
          id: 3,
          title: 'Performance Issues',
          description: `Detected ${performanceLogs.length} performance-related log entries`,
          severity: 'Medium'
        })
      }
      
      aiInsights.value = insights
    }

    const analyzeLog = async (log) => {
      try {
        // Call ML analysis API
        const response = await fetch('/api/ml/analyze', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            operation: 'analyze',
            log_entry: log.message
          })
        })
        
        const result = await response.json()
        
        if (result.analysis) {
          log.aiAnalysis = result.analysis
          notificationStore.addNotification({
            type: 'success',
            title: 'Analysis Complete',
            message: 'AI analysis completed for this log entry'
          })
        }
      } catch (error) {
        console.error('Analysis error:', error)
        // Fallback to mock analysis
        log.aiAnalysis = {
          category: 'System Error',
          confidence: 0.85,
          anomaly: log.level === 'ERROR' || log.level === 'FATAL',
          sentiment: 'negative',
          keywords: ['error', 'failed', 'timeout']
        }
        notificationStore.addNotification({
          type: 'info',
          title: 'Analysis Complete',
          message: 'Mock AI analysis applied (API unavailable)'
        })
      }
    }

    const refreshLogs = () => {
      performSearch()
    }

    const clearFilters = () => {
      searchQuery.value = ''
      timeRange.value = '24h'
      logLevel.value = ''
      sourceSystem.value = ''
      aiAnalysisType.value = ''
      searchResults.value = []
      aiInsights.value = []
      currentPage.value = 1
    }

    const exportResults = () => {
      const data = searchResults.value.map(log => ({
        timestamp: log.timestamp,
        level: log.level,
        source: log.source,
        message: log.message,
        aiAnalysis: log.aiAnalysis
      }))
      
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `log-analysis-${new Date().toISOString().split('T')[0]}.json`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
      
      notificationStore.addNotification({
        type: 'success',
        title: 'Export Complete',
        message: 'Log analysis results exported successfully'
      })
    }

    const selectLog = (log) => {
      selectedLog.value = log
    }

    const viewLogDetails = (log) => {
      selectedLog.value = log
    }

    const formatTimestamp = (timestamp) => {
      return new Date(timestamp).toLocaleString()
    }

    const getLevelBadgeClass = (level) => {
      const classes = {
        'DEBUG': 'bg-gray-100 text-gray-800',
        'INFO': 'bg-blue-100 text-blue-800',
        'WARN': 'bg-yellow-100 text-yellow-800',
        'ERROR': 'bg-red-100 text-red-800',
        'FATAL': 'bg-red-200 text-red-900'
      }
      return classes[level] || 'bg-gray-100 text-gray-800'
    }

    // Watch for sort changes
    watch(sortBy, () => {
      if (searchResults.value.length > 0) {
        performSearch()
      }
    })

    // Initialize with sample data
    onMounted(() => {
      searchResults.value = sampleLogs.value
    })

    return {
      // State
      isLoading,
      searchQuery,
      timeRange,
      logLevel,
      sourceSystem,
      aiAnalysisType,
      sortBy,
      currentPage,
      pageSize,
      selectedLog,
      searchResults,
      aiInsights,
      
      // Computed
      totalPages,
      paginatedResults,
      
      // Methods
      performSearch,
      analyzeLog,
      refreshLogs,
      clearFilters,
      exportResults,
      selectLog,
      viewLogDetails,
      formatTimestamp,
      getLevelBadgeClass
    }
  }
}

// Utility function
function debounce(func, wait) {
  let timeout
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout)
      func(...args)
    }
    clearTimeout(timeout)
    timeout = setTimeout(later, wait)
  }
}
</script>

<style scoped>
.container-custom {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 1rem;
}

.card {
  @apply bg-white rounded-lg shadow-sm border border-gray-200;
}

.card-header {
  @apply px-6 py-4 border-b border-gray-200;
}

.card-body {
  @apply px-6 py-4;
}

.btn {
  @apply inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-offset-2 transition-colors duration-200;
}

.btn-primary {
  @apply text-white bg-blue-600 hover:bg-blue-700 focus:ring-blue-500;
}

.btn-secondary {
  @apply text-gray-700 bg-white border-gray-300 hover:bg-gray-50 focus:ring-blue-500;
}

.btn-sm {
  @apply px-3 py-1.5 text-xs;
}

.btn:disabled {
  @apply opacity-50 cursor-not-allowed;
}

.input {
  @apply block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500;
}

.select {
  @apply block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500;
}
</style>
