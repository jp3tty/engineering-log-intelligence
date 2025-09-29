<template>
  <div class="report-generation">
    <!-- Header -->
    <div class="section-header">
      <h2 class="section-title">
        <DocumentTextIcon class="w-6 h-6 text-blue-500" />
        Report Generation
      </h2>
      <button
        @click="showGenerateModal = true"
        :disabled="loading"
        class="btn-primary"
      >
        <PlusIcon class="w-4 h-4" />
        Generate New Report
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner">
        <div class="spinner"></div>
        <p>Generating report...</p>
      </div>
    </div>

    <!-- Report Templates -->
    <div v-if="templates && templates.length > 0" class="templates-section">
      <h3 class="subsection-title">Available Templates</h3>
      <div class="templates-grid">
        <div
          v-for="template in templates"
          :key="template.id"
          class="template-card"
          @click="generateReport(template.id)"
        >
          <div class="template-header">
            <div class="template-icon">
              <DocumentTextIcon class="w-6 h-6" />
            </div>
            <div class="template-meta">
              <span class="template-duration">{{ template.duration }}</span>
              <span class="template-type">{{ template.type || 'Standard' }}</span>
            </div>
          </div>
          <h4 class="template-title">{{ template.name }}</h4>
          <p class="template-description">{{ template.description }}</p>
          <div class="template-actions">
            <button class="btn-small btn-primary">
              Generate Now
            </button>
            <button class="btn-small btn-secondary" @click.stop="scheduleReport(template)">
              Schedule
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Generated Reports -->
    <div v-if="reports && reports.length > 0" class="reports-section">
      <h3 class="subsection-title">Recent Reports</h3>
      <div class="reports-list">
        <div
          v-for="report in reports"
          :key="report.id"
          class="report-item"
        >
          <div class="report-header">
            <div class="report-icon">
              <component :is="getReportIcon(report.format)" class="w-5 h-5" />
            </div>
            <div class="report-info">
              <h4 class="report-title">{{ report.title }}</h4>
              <p class="report-meta">
                Generated {{ formatTime(report.created_at) }} • 
                {{ report.format.toUpperCase() }} • 
                {{ formatFileSize(report.size) }}
              </p>
            </div>
            <div class="report-status">
              <span :class="getStatusClass(report.status)">
                {{ report.status }}
              </span>
            </div>
          </div>
          <div class="report-description">
            <p>{{ report.description }}</p>
          </div>
          <div class="report-actions">
            <button
              v-if="report.status === 'completed'"
              @click="downloadReport(report)"
              class="btn-small btn-primary"
            >
              <ArrowDownTrayIcon class="w-4 h-4" />
              Download
            </button>
            <button
              v-if="report.status === 'completed'"
              @click="shareReport(report)"
              class="btn-small btn-secondary"
            >
              <ShareIcon class="w-4 h-4" />
              Share
            </button>
            <button
              @click="deleteReport(report)"
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
    <div v-if="(!templates || templates.length === 0) && (!reports || reports.length === 0)" class="empty-state">
      <DocumentTextIcon class="w-12 h-12 text-gray-400 mx-auto mb-4" />
      <h3 class="empty-title">No Reports Available</h3>
      <p class="empty-description">
        Generate your first report to get started with analytics insights.
      </p>
      <button @click="showGenerateModal = true" class="btn-primary mt-4">
        Generate Report
      </button>
    </div>

    <!-- Generate Report Modal -->
    <div v-if="showGenerateModal" class="modal-overlay" @click="showGenerateModal = false">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3 class="modal-title">Generate New Report</h3>
          <button @click="showGenerateModal = false" class="modal-close">
            <XMarkIcon class="w-5 h-5" />
          </button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="handleGenerateReport">
            <div class="form-group">
              <label class="form-label">Report Template</label>
              <select v-model="newReport.template_id" class="form-select" required>
                <option value="">Select a template...</option>
                <option
                  v-for="template in templates"
                  :key="template.id"
                  :value="template.id"
                >
                  {{ template.name }}
                </option>
              </select>
            </div>
            
            <div class="form-group">
              <label class="form-label">Report Title</label>
              <input
                v-model="newReport.title"
                type="text"
                class="form-input"
                placeholder="Enter report title..."
                required
              />
            </div>
            
            <div class="form-group">
              <label class="form-label">Time Range</label>
              <select v-model="newReport.time_range" class="form-select">
                <option value="1d">Last 24 hours</option>
                <option value="7d">Last 7 days</option>
                <option value="30d">Last 30 days</option>
                <option value="90d">Last 90 days</option>
              </select>
            </div>
            
            <div class="form-group">
              <label class="form-label">Output Format</label>
              <select v-model="newReport.format" class="form-select">
                <option value="pdf">PDF</option>
                <option value="excel">Excel</option>
                <option value="csv">CSV</option>
                <option value="json">JSON</option>
              </select>
            </div>
            
            <div class="form-group">
              <label class="form-label">Include Charts</label>
              <div class="checkbox-group">
                <label class="checkbox-item">
                  <input
                    v-model="newReport.include_charts"
                    type="checkbox"
                    class="form-checkbox"
                  />
                  <span>Include visualizations</span>
                </label>
              </div>
            </div>
            
            <div class="form-group">
              <label class="form-label">Email Recipients (optional)</label>
              <input
                v-model="newReport.email_recipients"
                type="text"
                class="form-input"
                placeholder="email1@example.com, email2@example.com"
              />
            </div>
          </form>
        </div>
        <div class="modal-footer">
          <button @click="showGenerateModal = false" class="btn-secondary">
            Cancel
          </button>
          <button @click="handleGenerateReport" class="btn-primary" :disabled="generating">
            <ArrowPathIcon v-if="generating" class="w-4 h-4 animate-spin" />
            <span v-else>Generate Report</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive } from 'vue'
import {
  DocumentTextIcon,
  PlusIcon,
  ArrowDownTrayIcon,
  ShareIcon,
  TrashIcon,
  XMarkIcon,
  ArrowPathIcon
} from '@heroicons/vue/24/outline'

export default {
  name: 'ReportGeneration',
  props: {
    templates: {
      type: Array,
      default: () => []
    },
    reports: {
      type: Array,
      default: () => []
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  emits: ['generate', 'schedule', 'download', 'share', 'delete'],
  setup(props, { emit }) {
    const showGenerateModal = ref(false)
    const generating = ref(false)
    
    const newReport = reactive({
      template_id: '',
      title: '',
      time_range: '7d',
      format: 'pdf',
      include_charts: true,
      email_recipients: ''
    })

    const generateReport = async (templateId) => {
      try {
        generating.value = true
        await emit('generate', templateId)
        showGenerateModal.value = false
        resetForm()
      } catch (error) {
        console.error('Failed to generate report:', error)
      } finally {
        generating.value = false
      }
    }

    const scheduleReport = async (template) => {
      await emit('schedule', {
        template_id: template.id,
        title: template.name,
        schedule: 'daily',
        time_range: '7d',
        format: 'pdf'
      })
    }

    const handleGenerateReport = async () => {
      if (!newReport.template_id) return
      
      await generateReport(newReport.template_id)
    }

    const downloadReport = async (report) => {
      await emit('download', report)
    }

    const shareReport = async (report) => {
      await emit('share', report)
    }

    const deleteReport = async (report) => {
      if (confirm('Are you sure you want to delete this report?')) {
        await emit('delete', report)
      }
    }

    const resetForm = () => {
      Object.assign(newReport, {
        template_id: '',
        title: '',
        time_range: '7d',
        format: 'pdf',
        include_charts: true,
        email_recipients: ''
      })
    }

    const getReportIcon = (format) => {
      const iconMap = {
        'pdf': DocumentTextIcon,
        'excel': DocumentTextIcon,
        'csv': DocumentTextIcon,
        'json': DocumentTextIcon
      }
      return iconMap[format] || DocumentTextIcon
    }

    const getStatusClass = (status) => {
      const classMap = {
        'completed': 'text-green-600 bg-green-100',
        'generating': 'text-yellow-600 bg-yellow-100',
        'failed': 'text-red-600 bg-red-100',
        'scheduled': 'text-blue-600 bg-blue-100'
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
      showGenerateModal,
      generating,
      newReport,
      generateReport,
      scheduleReport,
      handleGenerateReport,
      downloadReport,
      shareReport,
      deleteReport,
      getReportIcon,
      getStatusClass,
      formatTime,
      formatFileSize
    }
  }
}
</script>

<style scoped>
.report-generation {
  @apply space-y-6;
}

.section-header {
  @apply flex items-center justify-between;
}

.section-title {
  @apply text-xl font-semibold text-gray-900 flex items-center gap-2;
}

.loading-container {
  @apply flex items-center justify-center py-12;
}

.loading-spinner {
  @apply text-center;
}

.spinner {
  @apply w-8 h-8 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin mx-auto mb-4;
}

.templates-section {
  @apply space-y-4;
}

.subsection-title {
  @apply text-lg font-medium text-gray-900;
}

.templates-grid {
  @apply grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4;
}

.template-card {
  @apply bg-white border border-gray-200 rounded-lg p-4 cursor-pointer hover:shadow-md transition-shadow;
}

.template-header {
  @apply flex items-center justify-between mb-3;
}

.template-icon {
  @apply p-2 bg-blue-100 text-blue-600 rounded-lg;
}

.template-meta {
  @apply flex flex-col items-end text-xs text-gray-500;
}

.template-duration {
  @apply font-medium;
}

.template-title {
  @apply font-medium text-gray-900 mb-2;
}

.template-description {
  @apply text-sm text-gray-600 mb-4;
}

.template-actions {
  @apply flex gap-2;
}

.reports-section {
  @apply space-y-4;
}

.reports-list {
  @apply space-y-4;
}

.report-item {
  @apply bg-white border border-gray-200 rounded-lg p-4;
}

.report-header {
  @apply flex items-center justify-between mb-3;
}

.report-icon {
  @apply p-2 bg-gray-100 text-gray-600 rounded-lg;
}

.report-info {
  @apply flex-1 ml-3;
}

.report-title {
  @apply font-medium text-gray-900;
}

.report-meta {
  @apply text-sm text-gray-500 mt-1;
}

.report-status {
  @apply flex-shrink-0;
}

.report-status span {
  @apply px-2 py-1 rounded-full text-xs font-medium;
}

.report-description {
  @apply mb-4;
}

.report-description p {
  @apply text-sm text-gray-600;
}

.report-actions {
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
