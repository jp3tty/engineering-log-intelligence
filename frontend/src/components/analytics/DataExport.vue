<template>
  <div class="data-export">
    <!-- Header -->
    <div class="section-header">
      <h2 class="section-title">
        <ArrowDownTrayIcon class="w-6 h-6 text-green-500" />
        Data Export
      </h2>
      <button
        @click="showExportModal = true"
        :disabled="loading"
        class="btn-primary"
      >
        <ArrowDownTrayIcon class="w-4 h-4" />
        Export Data
      </button>
    </div>

    <!-- Export Formats -->
    <div class="formats-section">
      <h3 class="subsection-title">Available Formats</h3>
      <div class="formats-grid">
        <div
          v-for="format in formats"
          :key="format.id"
          class="format-card"
          @click="selectFormat(format.id)"
          :class="{ 'format-selected': selectedFormat === format.id }"
        >
          <div class="format-icon">
            <span class="format-emoji">{{ format.icon }}</span>
          </div>
          <h4 class="format-name">{{ format.name }}</h4>
          <p class="format-description">{{ format.description }}</p>
        </div>
      </div>
    </div>

    <!-- Export Filters -->
    <div class="filters-section">
      <h3 class="subsection-title">Export Filters</h3>
      <div class="filters-grid">
        <div class="filter-group">
          <label class="filter-label">Date Range</label>
          <select v-model="exportConfig.dateRange" class="filter-select">
            <option value="1h">Last Hour</option>
            <option value="24h">Last 24 Hours</option>
            <option value="7d">Last 7 Days</option>
            <option value="30d">Last 30 Days</option>
            <option value="90d">Last 90 Days</option>
            <option value="custom">Custom Range</option>
          </select>
        </div>
        
        <div class="filter-group">
          <label class="filter-label">Log Types</label>
          <select v-model="exportConfig.logTypes" class="filter-select" multiple>
            <option value="all">All Types</option>
            <option value="splunk">SPLUNK</option>
            <option value="sap">SAP</option>
            <option value="application">Application</option>
          </select>
        </div>
        
        <div class="filter-group">
          <label class="filter-label">Severity Levels</label>
          <select v-model="exportConfig.severity" class="filter-select" multiple>
            <option value="all">All Levels</option>
            <option value="critical">Critical</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
        </div>
        
        <div class="filter-group">
          <label class="filter-label">Systems</label>
          <select v-model="exportConfig.systems" class="filter-select" multiple>
            <option value="all">All Systems</option>
            <option value="web">Web Server</option>
            <option value="database">Database</option>
            <option value="api">API Gateway</option>
            <option value="auth">Authentication</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Export History -->
    <div v-if="exports && exports.length > 0" class="history-section">
      <h3 class="subsection-title">Export History</h3>
      <div class="exports-list">
        <div
          v-for="exportItem in exports"
          :key="exportItem.id"
          class="export-item"
        >
          <div class="export-header">
            <div class="export-icon">
              <component :is="getFormatIcon(exportItem.format)" class="w-5 h-5" />
            </div>
            <div class="export-info">
              <h4 class="export-title">{{ exportItem.filename }}</h4>
              <p class="export-meta">
                Exported {{ formatTime(exportItem.created_at) }} • 
                {{ exportItem.format.toUpperCase() }} • 
                {{ formatFileSize(exportItem.size) }}
              </p>
            </div>
            <div class="export-status">
              <span :class="getStatusClass(exportItem.status)">
                {{ exportItem.status }}
              </span>
            </div>
          </div>
          <div class="export-actions">
            <button
              v-if="exportItem.status === 'completed'"
              @click="downloadExport(exportItem)"
              class="btn-small btn-primary"
            >
              <ArrowDownTrayIcon class="w-4 h-4" />
              Download
            </button>
            <button
              @click="deleteExport(exportItem)"
              class="btn-small btn-danger"
            >
              <TrashIcon class="w-4 h-4" />
              Delete
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="(!exports || exports.length === 0)" class="empty-state">
      <ArrowDownTrayIcon class="w-12 h-12 text-gray-400 mx-auto mb-4" />
      <h3 class="empty-title">No Exports Yet</h3>
      <p class="empty-description">
        Export your data to get started with external analysis.
      </p>
      <button @click="showExportModal = true" class="btn-primary mt-4">
        Export Data
      </button>
    </div>

    <!-- Export Modal -->
    <div v-if="showExportModal" class="modal-overlay" @click="showExportModal = false">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3 class="modal-title">Export Data</h3>
          <button @click="showExportModal = false" class="modal-close">
            <XMarkIcon class="w-5 h-5" />
          </button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="handleExport">
            <div class="form-group">
              <label class="form-label">Export Format</label>
              <select v-model="exportConfig.format" class="form-select" required>
                <option value="">Select format...</option>
                <option
                  v-for="format in formats"
                  :key="format.id"
                  :value="format.id"
                >
                  {{ format.name }}
                </option>
              </select>
            </div>
            
            <div class="form-group">
              <label class="form-label">Filename</label>
              <input
                v-model="exportConfig.filename"
                type="text"
                class="form-input"
                placeholder="Enter filename..."
                required
              />
            </div>
            
            <div class="form-group">
              <label class="form-label">Date Range</label>
              <select v-model="exportConfig.dateRange" class="form-select">
                <option value="1h">Last Hour</option>
                <option value="24h">Last 24 Hours</option>
                <option value="7d">Last 7 Days</option>
                <option value="30d">Last 30 Days</option>
                <option value="90d">Last 90 Days</option>
              </select>
            </div>
            
            <div class="form-group">
              <label class="form-label">Include Metadata</label>
              <div class="checkbox-group">
                <label class="checkbox-item">
                  <input
                    v-model="exportConfig.include_metadata"
                    type="checkbox"
                    class="form-checkbox"
                  />
                  <span>Include system metadata</span>
                </label>
                <label class="checkbox-item">
                  <input
                    v-model="exportConfig.include_timestamps"
                    type="checkbox"
                    class="form-checkbox"
                  />
                  <span>Include timestamps</span>
                </label>
              </div>
            </div>
          </form>
        </div>
        <div class="modal-footer">
          <button @click="showExportModal = false" class="btn-secondary">
            Cancel
          </button>
          <button @click="handleExport" class="btn-primary" :disabled="exporting">
            <ArrowPathIcon v-if="exporting" class="w-4 h-4 animate-spin" />
            <span v-else>Export Data</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive } from 'vue'
import {
  ArrowDownTrayIcon,
  TrashIcon,
  XMarkIcon,
  ArrowPathIcon,
  DocumentTextIcon
} from '@heroicons/vue/24/outline'

export default {
  name: 'DataExport',
  props: {
    formats: {
      type: Array,
      default: () => [
        { id: 'json', name: 'JSON', icon: '📄', description: 'Structured data format' },
        { id: 'csv', name: 'CSV', icon: '📊', description: 'Comma-separated values' },
        { id: 'excel', name: 'Excel', icon: '📈', description: 'Microsoft Excel format' },
        { id: 'pdf', name: 'PDF', icon: '📋', description: 'Portable document format' }
      ]
    },
    filters: {
      type: Object,
      default: () => ({
        dateRange: '7d',
        logTypes: ['all'],
        severity: ['all'],
        systems: ['all']
      })
    },
    exports: {
      type: Array,
      default: () => []
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  emits: ['export', 'download', 'delete'],
  setup(props, { emit }) {
    const showExportModal = ref(false)
    const selectedFormat = ref('')
    const exporting = ref(false)
    
    const exportConfig = reactive({
      format: '',
      filename: '',
      dateRange: '7d',
      include_metadata: true,
      include_timestamps: true
    })

    const selectFormat = (formatId) => {
      selectedFormat.value = formatId
      exportConfig.format = formatId
    }

    const handleExport = async () => {
      if (!exportConfig.format || !exportConfig.filename) return
      
      try {
        exporting.value = true
        await emit('export', exportConfig)
        showExportModal.value = false
        resetConfig()
      } catch (error) {
        console.error('Failed to export data:', error)
      } finally {
        exporting.value = false
      }
    }

    const downloadExport = async (exportItem) => {
      await emit('download', exportItem)
    }

    const deleteExport = async (exportItem) => {
      if (confirm('Are you sure you want to delete this export?')) {
        await emit('delete', exportItem)
      }
    }

    const resetConfig = () => {
      Object.assign(exportConfig, {
        format: '',
        filename: '',
        dateRange: '7d',
        include_metadata: true,
        include_timestamps: true
      })
      selectedFormat.value = ''
    }

    const getFormatIcon = (format) => {
      return DocumentTextIcon
    }

    const getStatusClass = (status) => {
      const classMap = {
        'completed': 'text-green-600 bg-green-100',
        'exporting': 'text-yellow-600 bg-yellow-100',
        'failed': 'text-red-600 bg-red-100',
        'pending': 'text-blue-600 bg-blue-100'
      }
      return classMap[status] || 'text-gray-600 bg-gray-100'
    }

    const formatTime = (timestamp) => {
      if (!timestamp) return 'Unknown'
      
      const date = new Date(timestamp)
      const now = new Date()
      const diffMs = now - date
      const diffMins = Math.floor(diffMs / 60000)
      const diffHours = Math.floor(diffMs / 3600000)
      const diffDays = Math.floor(diffMs / 86400000)

      if (diffMins < 60) return `${diffMins}m ago`
      if (diffHours < 24) return `${diffHours}h ago`
      return `${diffDays}d ago`
    }

    const formatFileSize = (bytes) => {
      if (!bytes) return '0 B'
      
      const k = 1024
      const sizes = ['B', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      
      return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`
    }

    return {
      showExportModal,
      selectedFormat,
      exporting,
      exportConfig,
      selectFormat,
      handleExport,
      downloadExport,
      deleteExport,
      getFormatIcon,
      getStatusClass,
      formatTime,
      formatFileSize
    }
  }
}
</script>

<style scoped>
.data-export {
  @apply space-y-6;
}

.section-header {
  @apply flex items-center justify-between;
}

.section-title {
  @apply text-xl font-semibold text-gray-900 flex items-center gap-2;
}

.formats-section {
  @apply space-y-4;
}

.subsection-title {
  @apply text-lg font-medium text-gray-900;
}

.formats-grid {
  @apply grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4;
}

.format-card {
  @apply bg-white border border-gray-200 rounded-lg p-4 cursor-pointer hover:shadow-md transition-shadow;
}

.format-card.format-selected {
  @apply border-blue-500 bg-blue-50;
}

.format-icon {
  @apply text-2xl mb-3;
}

.format-name {
  @apply font-medium text-gray-900 mb-2;
}

.format-description {
  @apply text-sm text-gray-600;
}

.filters-section {
  @apply space-y-4;
}

.filters-grid {
  @apply grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4;
}

.filter-group {
  @apply space-y-2;
}

.filter-label {
  @apply block text-sm font-medium text-gray-700;
}

.filter-select {
  @apply w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500;
}

.history-section {
  @apply space-y-4;
}

.exports-list {
  @apply space-y-4;
}

.export-item {
  @apply bg-white border border-gray-200 rounded-lg p-4;
}

.export-header {
  @apply flex items-center justify-between mb-3;
}

.export-icon {
  @apply p-2 bg-gray-100 text-gray-600 rounded-lg;
}

.export-info {
  @apply flex-1 ml-3;
}

.export-title {
  @apply font-medium text-gray-900;
}

.export-meta {
  @apply text-sm text-gray-500 mt-1;
}

.export-status {
  @apply flex-shrink-0;
}

.export-status span {
  @apply px-2 py-1 rounded-full text-xs font-medium;
}

.export-actions {
  @apply flex gap-2;
}

.btn-small {
  @apply px-3 py-1 text-xs font-medium rounded-md transition-colors;
}

.btn-primary {
  @apply bg-blue-600 text-white hover:bg-blue-700;
}

.btn-secondary {
  @apply bg-white text-gray-700 border border-gray-300 hover:bg-gray-50;
}

.btn-danger {
  @apply bg-red-600 text-white hover:bg-red-700;
}

.empty-state {
  @apply text-center py-12;
}

.empty-title {
  @apply text-lg font-medium text-gray-900 mb-2;
}

.empty-description {
  @apply text-gray-600;
}

.modal-overlay {
  @apply fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50;
}

.modal-content {
  @apply bg-white rounded-lg shadow-xl max-w-md w-full mx-4;
}

.modal-header {
  @apply flex items-center justify-between p-6 border-b border-gray-200;
}

.modal-title {
  @apply text-lg font-semibold text-gray-900;
}

.modal-close {
  @apply text-gray-400 hover:text-gray-600;
}

.modal-body {
  @apply p-6;
}

.modal-footer {
  @apply flex items-center justify-end gap-3 p-6 border-t border-gray-200;
}

.form-group {
  @apply mb-4;
}

.form-label {
  @apply block text-sm font-medium text-gray-700 mb-2;
}

.form-input {
  @apply w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500;
}

.form-select {
  @apply w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500;
}

.checkbox-group {
  @apply space-y-2;
}

.checkbox-item {
  @apply flex items-center;
}

.form-checkbox {
  @apply mr-2;
}
</style>
