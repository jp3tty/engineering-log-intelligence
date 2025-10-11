<template>
  <div class="analytics-insights">
    <!-- Header -->
    <div class="insights-header">
      <h2 class="section-title">
        <LightBulbIcon class="w-6 h-6 text-yellow-500" />
        AI-Powered Insights
      </h2>
      <button
        @click="$emit('refresh')"
        :disabled="loading"
        class="btn-secondary"
      >
        <ArrowPathIcon class="w-4 h-4" :class="{ 'animate-spin': loading }" />
        Refresh Insights
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner">
        <div class="spinner"></div>
        <p>Analyzing data with AI...</p>
      </div>
    </div>

    <!-- Insights Content -->
    <div v-else-if="insights" class="insights-content">
      <!-- Trend Analysis -->
      <div class="insight-section">
        <h3 class="subsection-title">Trend Analysis</h3>
        <div class="trend-cards">
          <div
            v-for="trend in insights.trend_analysis"
            :key="trend.id"
            class="trend-card"
          >
            <div class="trend-header">
              <div class="trend-icon" :class="getTrendIconClass(trend.type)">
                <component :is="getTrendIcon(trend.type)" class="w-5 h-5" />
              </div>
              <span class="trend-confidence">
                {{ Math.round(trend.confidence * 100) }}% confidence
              </span>
            </div>
            <h4 class="trend-title">{{ trend.title }}</h4>
            <p class="trend-description">{{ trend.description }}</p>
            <div class="trend-impact">
              <span class="impact-label">Impact:</span>
              <span :class="getImpactClass(trend.impact)">{{ trend.impact }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Anomaly Detection -->
      <div class="insight-section">
        <div class="subsection-header">
          <h3 class="subsection-title">Anomaly Detection (ML-Powered)</h3>
          <span v-if="mlAnomalies.length > 0" class="ml-badge">
            🤖 Live ML Data
          </span>
        </div>
        
        <!-- ML Loading State -->
        <div v-if="mlLoading" class="ml-loading">
          <div class="spinner-small"></div>
          <span>Loading ML anomalies...</span>
        </div>
        
        <!-- ML Anomalies -->
        <div v-else-if="mlAnomalies.length > 0" class="anomaly-grid">
          <div
            v-for="anomaly in mlAnomalies.slice(0, 6)"
            :key="anomaly.id"
            class="anomaly-card"
            :class="getAnomalySeverityClass(anomaly.severity)"
          >
            <div class="anomaly-header">
              <div class="anomaly-severity">
                <component :is="getSeverityIcon(anomaly.severity)" class="w-5 h-5" />
                <span class="severity-text">{{ anomaly.severity }}</span>
              </div>
              <span class="anomaly-time">{{ formatTime(anomaly.detected_at) }}</span>
            </div>
            <h4 class="anomaly-title">{{ anomaly.title }}</h4>
            <p class="anomaly-description">{{ truncateText(anomaly.description, 100) }}</p>
            <div class="anomaly-metrics">
              <div class="metric">
                <span class="metric-label">ML Confidence:</span>
                <span class="metric-value">{{ Math.round(anomaly.confidence * 100) }}%</span>
              </div>
              <div class="metric">
                <span class="metric-label">Log ID:</span>
                <span class="metric-value mono">{{ anomaly.log_id }}</span>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Fallback to mock data -->
        <div v-else-if="insights?.anomalies && insights.anomalies.length > 0" class="anomaly-grid">
          <div
            v-for="anomaly in insights.anomalies"
            :key="anomaly.id"
            class="anomaly-card"
            :class="getAnomalySeverityClass(anomaly.severity)"
          >
            <div class="anomaly-header">
              <div class="anomaly-severity">
                <component :is="getSeverityIcon(anomaly.severity)" class="w-5 h-5" />
                <span class="severity-text">{{ anomaly.severity }}</span>
              </div>
              <span class="anomaly-time">{{ formatTime(anomaly.detected_at) }}</span>
            </div>
            <h4 class="anomaly-title">{{ anomaly.title }}</h4>
            <p class="anomaly-description">{{ anomaly.description }}</p>
            <div class="anomaly-metrics">
              <div class="metric">
                <span class="metric-label">Confidence:</span>
                <span class="metric-value">{{ Math.round(anomaly.confidence * 100) }}%</span>
              </div>
              <div class="metric">
                <span class="metric-label">Affected Systems:</span>
                <span class="metric-value">{{ anomaly.affected_systems?.length || 0 }}</span>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Empty State -->
        <div v-else class="empty-anomalies">
          <p>✅ No anomalies detected in the last 24 hours</p>
        </div>
        
        <!-- View All Link -->
        <div v-if="mlAnomalies.length > 6" class="view-all-link">
          <router-link to="/ml-analytics" class="link-primary">
            View all {{ mlAnomalies.length }} anomalies →
          </router-link>
        </div>
      </div>

      <!-- Pattern Recognition -->
      <div class="insight-section">
        <h3 class="subsection-title">Pattern Recognition</h3>
        <div class="pattern-list">
          <div
            v-for="pattern in insights.patterns"
            :key="pattern.id"
            class="pattern-item"
          >
            <div class="pattern-header">
              <div class="pattern-type">
                <component :is="getPatternIcon(pattern.type)" class="w-5 h-5" />
                <span class="pattern-type-text">{{ pattern.type }}</span>
              </div>
              <span class="pattern-frequency">{{ pattern.frequency }} occurrences</span>
            </div>
            <div class="pattern-content">
              <h4 class="pattern-title">{{ pattern.title }}</h4>
              <p class="pattern-description">{{ pattern.description }}</p>
              <div class="pattern-tags">
                <span
                  v-for="tag in pattern.tags"
                  :key="tag"
                  class="pattern-tag"
                >
                  {{ tag }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Recommendations -->
      <div class="insight-section">
        <h3 class="subsection-title">AI Recommendations</h3>
        <div class="recommendations-list">
          <div
            v-for="recommendation in insights.recommendations"
            :key="recommendation.id"
            class="recommendation-item"
            :class="getPriorityClass(recommendation.priority)"
          >
            <div class="recommendation-header">
              <div class="recommendation-priority">
                <component :is="getPriorityIcon(recommendation.priority)" class="w-5 h-5" />
                <span class="priority-text">{{ recommendation.priority }}</span>
              </div>
              <span class="recommendation-impact">
                Expected Impact: {{ recommendation.expected_impact }}
              </span>
            </div>
            <h4 class="recommendation-title">{{ recommendation.title }}</h4>
            <p class="recommendation-description">{{ recommendation.description }}</p>
            <div class="recommendation-actions">
              <button class="btn-small btn-primary">
                Implement
              </button>
              <button class="btn-small btn-secondary">
                Learn More
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="empty-state">
      <LightBulbIcon class="w-12 h-12 text-gray-400 mx-auto mb-4" />
      <h3 class="empty-title">No Insights Available</h3>
      <p class="empty-description">
        AI insights will appear here once sufficient data is available for analysis.
      </p>
      <button @click="$emit('refresh')" class="btn-primary mt-4">
        Generate Insights
      </button>
    </div>
  </div>
</template>

<script>
import { computed, onMounted } from 'vue'
import { useMLData } from '@/composables/useMLData'
import {
  LightBulbIcon,
  ArrowPathIcon,
  ChartBarIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
  ExclamationTriangleIcon,
  ExclamationCircleIcon,
  InformationCircleIcon,
  CheckCircleIcon,
  ClockIcon,
  BoltIcon,
  StarIcon,
  ArrowUpIcon,
  ArrowDownIcon,
  MinusIcon
} from '@heroicons/vue/24/outline'

export default {
  name: 'AnalyticsInsights',
  props: {
    insights: {
      type: Object,
      default: null
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  emits: ['refresh'],
  setup(props) {
    // Use ML Data composable
    const {
      formattedAnomalies,
      loading: mlLoading,
      fetchAllMLData
    } = useMLData()

    // Fetch ML data on mount
    onMounted(() => {
      fetchAllMLData()
    })

    // Alias for template
    const mlAnomalies = formattedAnomalies

    // Helper function
    const truncateText = (text, length) => {
      if (!text) return ''
      return text.length > length ? text.substring(0, length) + '...' : text
    }

    // Trend icon mapping
    const getTrendIcon = (type) => {
      const iconMap = {
        'increasing': ArrowTrendingUpIcon,
        'decreasing': ArrowTrendingDownIcon,
        'stable': MinusIcon,
        'volatile': BoltIcon,
        'seasonal': ClockIcon,
        'anomalous': ExclamationTriangleIcon
      }
      return iconMap[type] || ChartBarIcon
    }

    const getTrendIconClass = (type) => {
      const classMap = {
        'increasing': 'bg-green-100 text-green-600',
        'decreasing': 'bg-red-100 text-red-600',
        'stable': 'bg-gray-100 text-gray-600',
        'volatile': 'bg-yellow-100 text-yellow-600',
        'seasonal': 'bg-blue-100 text-blue-600',
        'anomalous': 'bg-orange-100 text-orange-600'
      }
      return classMap[type] || 'bg-gray-100 text-gray-600'
    }

    // Impact class mapping
    const getImpactClass = (impact) => {
      const classMap = {
        'high': 'text-red-600 font-semibold',
        'medium': 'text-yellow-600 font-semibold',
        'low': 'text-green-600 font-semibold'
      }
      return classMap[impact] || 'text-gray-600'
    }

    // Anomaly severity mapping
    const getSeverityIcon = (severity) => {
      const iconMap = {
        'critical': ExclamationCircleIcon,
        'high': ExclamationTriangleIcon,
        'medium': InformationCircleIcon,
        'low': CheckCircleIcon
      }
      return iconMap[severity] || InformationCircleIcon
    }

    const getAnomalySeverityClass = (severity) => {
      const classMap = {
        'critical': 'border-red-200 bg-red-50',
        'high': 'border-orange-200 bg-orange-50',
        'medium': 'border-yellow-200 bg-yellow-50',
        'low': 'border-green-200 bg-green-50'
      }
      return classMap[severity] || 'border-gray-200 bg-gray-50'
    }

    // Pattern icon mapping
    const getPatternIcon = (type) => {
      const iconMap = {
        'error': ExclamationTriangleIcon,
        'performance': ChartBarIcon,
        'security': StarIcon,
        'usage': ArrowTrendingUpIcon,
        'seasonal': ClockIcon,
        'correlation': BoltIcon
      }
      return iconMap[type] || ChartBarIcon
    }

    // Priority mapping
    const getPriorityIcon = (priority) => {
      const iconMap = {
        'critical': ExclamationCircleIcon,
        'high': ArrowUpIcon,
        'medium': MinusIcon,
        'low': ArrowDownIcon
      }
      return iconMap[priority] || MinusIcon
    }

    const getPriorityClass = (priority) => {
      const classMap = {
        'critical': 'border-red-200 bg-red-50',
        'high': 'border-orange-200 bg-orange-50',
        'medium': 'border-yellow-200 bg-yellow-50',
        'low': 'border-green-200 bg-green-50'
      }
      return classMap[priority] || 'border-gray-200 bg-gray-50'
    }

    // Helper function to format time
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

    return {
      // ML Data
      mlAnomalies,
      mlLoading,
      truncateText,
      // Icon/Class mappings
      getTrendIcon,
      getTrendIconClass,
      getImpactClass,
      getSeverityIcon,
      getAnomalySeverityClass,
      getPatternIcon,
      getPriorityIcon,
      getPriorityClass,
      formatTime
    }
  }
}
</script>

<style scoped>
.analytics-insights {
  @apply space-y-6;
}

.insights-header {
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

.insights-content {
  @apply space-y-8;
}

.insight-section {
  @apply space-y-4;
}

.subsection-title {
  @apply text-lg font-medium text-gray-900;
}

.trend-cards {
  @apply grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4;
}

.trend-card {
  @apply bg-white border border-gray-200 rounded-lg p-4;
}

.trend-header {
  @apply flex items-center justify-between mb-3;
}

.trend-icon {
  @apply p-2 rounded-lg;
}

.trend-confidence {
  @apply text-xs text-gray-500;
}

.trend-title {
  @apply font-medium text-gray-900 mb-2;
}

.trend-description {
  @apply text-sm text-gray-600 mb-3;
}

.trend-impact {
  @apply flex items-center gap-2;
}

.impact-label {
  @apply text-xs text-gray-500;
}

.anomaly-grid {
  @apply grid grid-cols-1 md:grid-cols-2 gap-4;
}

.anomaly-card {
  @apply border rounded-lg p-4;
}

.anomaly-header {
  @apply flex items-center justify-between mb-3;
}

.anomaly-severity {
  @apply flex items-center gap-2;
}

.severity-text {
  @apply text-sm font-medium capitalize;
}

.anomaly-time {
  @apply text-xs text-gray-500;
}

.anomaly-title {
  @apply font-medium text-gray-900 mb-2;
}

.anomaly-description {
  @apply text-sm text-gray-600 mb-3;
}

.anomaly-metrics {
  @apply flex gap-4;
}

.metric {
  @apply flex flex-col;
}

.metric-label {
  @apply text-xs text-gray-500;
}

.metric-value {
  @apply text-sm font-medium text-gray-900;
}

.pattern-list {
  @apply space-y-4;
}

.pattern-item {
  @apply bg-white border border-gray-200 rounded-lg p-4;
}

.pattern-header {
  @apply flex items-center justify-between mb-3;
}

.pattern-type {
  @apply flex items-center gap-2;
}

.pattern-type-text {
  @apply text-sm font-medium capitalize;
}

.pattern-frequency {
  @apply text-xs text-gray-500;
}

.pattern-title {
  @apply font-medium text-gray-900 mb-2;
}

.pattern-description {
  @apply text-sm text-gray-600 mb-3;
}

.pattern-tags {
  @apply flex flex-wrap gap-2;
}

.pattern-tag {
  @apply px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full;
}

.recommendations-list {
  @apply space-y-4;
}

.recommendation-item {
  @apply border rounded-lg p-4;
}

.recommendation-header {
  @apply flex items-center justify-between mb-3;
}

.recommendation-priority {
  @apply flex items-center gap-2;
}

.priority-text {
  @apply text-sm font-medium capitalize;
}

.recommendation-impact {
  @apply text-xs text-gray-500;
}

.recommendation-title {
  @apply font-medium text-gray-900 mb-2;
}

.recommendation-description {
  @apply text-sm text-gray-600 mb-3;
}

.recommendation-actions {
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

.empty-state {
  @apply text-center py-12;
}

.empty-title {
  @apply text-lg font-medium text-gray-900 mb-2;
}

.empty-description {
  @apply text-gray-600;
}

/* ML Integration Styles */
.subsection-header {
  @apply flex items-center justify-between mb-4;
}

.ml-badge {
  @apply px-3 py-1 bg-gradient-to-r from-blue-500 to-purple-500 text-white text-xs font-semibold rounded-full;
}

.ml-loading {
  @apply flex items-center justify-center gap-2 py-8 text-gray-500;
}

.spinner-small {
  @apply w-5 h-5 border-2 border-gray-300 border-t-blue-600 rounded-full animate-spin;
}

.empty-anomalies {
  @apply text-center py-8 text-gray-500 bg-green-50 rounded-lg border border-green-200;
}

.view-all-link {
  @apply mt-4 text-center;
}

.link-primary {
  @apply text-blue-600 hover:text-blue-700 font-semibold transition-colors;
}

.mono {
  @apply font-mono text-xs;
}
</style>
