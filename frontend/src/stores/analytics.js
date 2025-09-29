import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api'

export const useAnalyticsStore = defineStore('analytics', () => {
  // State
  const overview = ref(null)
  const insights = ref(null)
  const reports = ref([])
  const performance = ref(null)
  const exports = ref([])
  const loading = ref(false)
  const error = ref(null)

  // Computed
  const hasData = computed(() => {
    return overview.value || insights.value || performance.value
  })

  const keyMetrics = computed(() => {
    if (!overview.value) return []
    
    return [
      {
        id: 'total_logs',
        title: 'Total Logs Processed',
        value: overview.value.total_logs || 0,
        format: 'number',
        trend: overview.value.logs_trend || 0,
        color: 'blue'
      },
      {
        id: 'anomalies_detected',
        title: 'Anomalies Detected',
        value: overview.value.anomalies_detected || 0,
        format: 'number',
        trend: overview.value.anomalies_trend || 0,
        color: 'red'
      },
      {
        id: 'avg_response_time',
        title: 'Avg Response Time',
        value: overview.value.avg_response_time || 0,
        format: 'duration',
        trend: overview.value.response_trend || 0,
        color: 'green'
      },
      {
        id: 'system_health',
        title: 'System Health',
        value: overview.value.system_health || 0,
        format: 'percentage',
        trend: overview.value.health_trend || 0,
        color: 'emerald'
      }
    ]
  })

  const recentReports = computed(() => {
    return reports.value.slice(0, 5)
  })

  const activeExports = computed(() => {
    return exports.value.filter(exp => exp.status === 'in_progress')
  })

  // Actions
  const fetchOverview = async () => {
    try {
      loading.value = true
      error.value = null
      
      const response = await api.get('/api/analytics/insights', {
        params: { action: 'overview' }
      })
      
      overview.value = response.data
      return response.data
    } catch (err) {
      error.value = err.message || 'Failed to fetch overview'
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchInsights = async (filters = {}) => {
    try {
      loading.value = true
      error.value = null
      
      const response = await api.get('/api/analytics/insights', {
        params: { action: 'insights', ...filters }
      })
      
      insights.value = response.data
      return response.data
    } catch (err) {
      error.value = err.message || 'Failed to fetch insights'
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchPerformance = async (timeRange = '7d') => {
    try {
      loading.value = true
      error.value = null
      
      const response = await api.get('/api/analytics/performance', {
        params: { action: 'metrics', time_range: timeRange }
      })
      
      performance.value = response.data
      return response.data
    } catch (err) {
      error.value = err.message || 'Failed to fetch performance data'
      throw err
    } finally {
      loading.value = false
    }
  }

  const generateReport = async (templateId, options = {}) => {
    try {
      loading.value = true
      error.value = null
      
      const response = await api.post('/api/analytics/reports', {
        action: 'generate',
        template_id: templateId,
        options: options
      })
      
      const report = response.data
      reports.value.unshift(report)
      
      return report
    } catch (err) {
      error.value = err.message || 'Failed to generate report'
      throw err
    } finally {
      loading.value = false
    }
  }

  const scheduleReport = async (scheduleData) => {
    try {
      loading.value = true
      error.value = null
      
      const response = await api.post('/api/analytics/reports', {
        action: 'schedule',
        ...scheduleData
      })
      
      return response.data
    } catch (err) {
      error.value = err.message || 'Failed to schedule report'
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchReports = async () => {
    try {
      loading.value = true
      error.value = null
      
      const response = await api.get('/api/analytics/reports', {
        params: { action: 'list' }
      })
      
      reports.value = response.data.reports || []
      return response.data
    } catch (err) {
      error.value = err.message || 'Failed to fetch reports'
      throw err
    } finally {
      loading.value = false
    }
  }

  const exportData = async (exportConfig) => {
    try {
      loading.value = true
      error.value = null
      
      const response = await api.post('/api/analytics/export', {
        action: 'export',
        ...exportConfig
      }, {
        responseType: 'blob'
      })
      
      // Create export record
      const exportRecord = {
        id: Date.now(),
        filename: exportConfig.filename || `export_${Date.now()}.${exportConfig.format}`,
        format: exportConfig.format,
        status: 'completed',
        created_at: new Date().toISOString(),
        size: response.data.size || 0
      }
      
      exports.value.unshift(exportRecord)
      
      return {
        data: response.data,
        mimeType: getMimeType(exportConfig.format),
        filename: exportRecord.filename
      }
    } catch (err) {
      error.value = err.message || 'Failed to export data'
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchExports = async () => {
    try {
      loading.value = true
      error.value = null
      
      const response = await api.get('/api/analytics/export', {
        params: { action: 'list' }
      })
      
      exports.value = response.data.exports || []
      return response.data
    } catch (err) {
      error.value = err.message || 'Failed to fetch exports'
      throw err
    } finally {
      loading.value = false
    }
  }

  const getReportTemplates = async () => {
    try {
      const response = await api.get('/api/analytics/reports', {
        params: { action: 'templates' }
      })
      
      return response.data.templates || []
    } catch (err) {
      error.value = err.message || 'Failed to fetch report templates'
      throw err
    }
  }

  const getExportFormats = async () => {
    try {
      const response = await api.get('/api/analytics/export', {
        params: { action: 'formats' }
      })
      
      return response.data.formats || []
    } catch (err) {
      error.value = err.message || 'Failed to fetch export formats'
      throw err
    }
  }

  const refreshAll = async () => {
    try {
      loading.value = true
      error.value = null
      
      await Promise.all([
        fetchOverview(),
        fetchInsights(),
        fetchPerformance(),
        fetchReports(),
        fetchExports()
      ])
    } catch (err) {
      error.value = err.message || 'Failed to refresh analytics data'
      throw err
    } finally {
      loading.value = false
    }
  }

  const clearError = () => {
    error.value = null
  }

  const reset = () => {
    overview.value = null
    insights.value = null
    reports.value = []
    performance.value = null
    exports.value = []
    loading.value = false
    error.value = null
  }

  // Helper functions
  const getMimeType = (format) => {
    const mimeTypes = {
      'json': 'application/json',
      'csv': 'text/csv',
      'excel': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      'pdf': 'application/pdf'
    }
    return mimeTypes[format] || 'application/octet-stream'
  }

  return {
    // State
    overview,
    insights,
    reports,
    performance,
    exports,
    loading,
    error,
    
    // Computed
    hasData,
    keyMetrics,
    recentReports,
    activeExports,
    
    // Actions
    fetchOverview,
    fetchInsights,
    fetchPerformance,
    generateReport,
    scheduleReport,
    fetchReports,
    exportData,
    fetchExports,
    getReportTemplates,
    getExportFormats,
    refreshAll,
    clearError,
    reset
  }
})
