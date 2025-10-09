<template>
  <div class="performance-analytics">
    <!-- Header -->
    <div class="section-header">
      <h2 class="section-title">
        <ChartBarIcon class="w-6 h-6 text-purple-500" />
        Performance Analytics
      </h2>
      <button
        @click="$emit('refresh')"
        :disabled="loading"
        class="btn-secondary"
      >
        <ArrowPathIcon class="w-4 h-4" :class="{ 'animate-spin': loading }" />
        Refresh Metrics
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner">
        <div class="spinner"></div>
        <p>Loading performance data...</p>
      </div>
    </div>

    <!-- Performance Overview -->
    <div v-if="metrics" class="metrics-overview">
      <h3 class="subsection-title">Performance Overview</h3>
      <div class="metrics-grid">
        <div class="metric-card">
          <div class="metric-icon bg-green-100 text-green-600">
            <ClockIcon class="w-6 h-6" />
          </div>
          <div class="metric-content">
            <h4 class="metric-title">Response Time</h4>
            <div class="metric-value text-green-600">
              {{ formatDuration(metrics.avg_response_time) }}
            </div>
            <div class="metric-trend" :class="getTrendClass(metrics.response_trend)">
              <component :is="getTrendIcon(metrics.response_trend)" class="w-4 h-4" />
              <span>{{ formatTrend(metrics.response_trend) }}</span>
            </div>
          </div>
        </div>

        <div class="metric-card">
          <div class="metric-icon bg-blue-100 text-blue-600">
            <ChartBarIcon class="w-6 h-6" />
          </div>
          <div class="metric-content">
            <h4 class="metric-title">Throughput</h4>
            <div class="metric-value text-blue-600">
              {{ formatNumber(metrics.throughput) }} req/s
            </div>
            <div class="metric-trend" :class="getTrendClass(metrics.throughput_trend)">
              <component :is="getTrendIcon(metrics.throughput_trend)" class="w-4 h-4" />
              <span>{{ formatTrend(metrics.throughput_trend) }}</span>
            </div>
          </div>
        </div>

        <div class="metric-card">
          <div class="metric-icon bg-red-100 text-red-600">
            <ExclamationTriangleIcon class="w-6 h-6" />
          </div>
          <div class="metric-content">
            <h4 class="metric-title">Error Rate</h4>
            <div class="metric-value text-red-600">
              {{ metrics.error_rate }}%
            </div>
            <div class="metric-trend" :class="getTrendClass(metrics.error_trend)">
              <component :is="getTrendIcon(metrics.error_trend)" class="w-4 h-4" />
              <span>{{ formatTrend(metrics.error_trend) }}</span>
            </div>
          </div>
        </div>

        <div class="metric-card">
          <div class="metric-icon bg-emerald-100 text-emerald-600">
            <CheckCircleIcon class="w-6 h-6" />
          </div>
          <div class="metric-content">
            <h4 class="metric-title">Availability</h4>
            <div class="metric-value text-emerald-600">
              {{ metrics.availability }}%
            </div>
            <div class="metric-trend" :class="getTrendClass(metrics.availability_trend)">
              <component :is="getTrendIcon(metrics.availability_trend)" class="w-4 h-4" />
              <span>{{ formatTrend(metrics.availability_trend) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Performance Charts -->
    <div v-if="metrics" class="charts-section">
      <h3 class="subsection-title">Performance Trends</h3>
      <div class="charts-grid">
        <div class="chart-card">
          <h4 class="chart-title">Response Time Over Time</h4>
          <div class="chart-container">
            <canvas ref="responseTimeChart" width="400" height="200"></canvas>
          </div>
        </div>
        
        <div class="chart-card">
          <h4 class="chart-title">Throughput Over Time</h4>
          <div class="chart-container">
            <canvas ref="throughputChart" width="400" height="200"></canvas>
          </div>
        </div>
      </div>
    </div>

    <!-- Capacity Forecasting -->
    <div v-if="forecasts" class="forecasting-section">
      <h3 class="subsection-title">Capacity Forecasting</h3>
      <div class="forecast-cards">
        <div class="forecast-card">
          <div class="forecast-header">
            <h4 class="forecast-title">CPU Usage</h4>
            <span class="forecast-period">Next 30 days</span>
          </div>
          <div class="forecast-content">
            <div class="forecast-current">
              Current: {{ forecasts.cpu.current }}%
            </div>
            <div class="forecast-predicted">
              Predicted: {{ forecasts.cpu.predicted }}%
            </div>
            <div class="forecast-alert" :class="getAlertClass(forecasts.cpu.alert_level)">
              {{ getAlertMessage(forecasts.cpu.alert_level) }}
            </div>
          </div>
        </div>

        <div class="forecast-card">
          <div class="forecast-header">
            <h4 class="forecast-title">Memory Usage</h4>
            <span class="forecast-period">Next 30 days</span>
          </div>
          <div class="forecast-content">
            <div class="forecast-current">
              Current: {{ forecasts.memory.current }}%
            </div>
            <div class="forecast-predicted">
              Predicted: {{ forecasts.memory.predicted }}%
            </div>
            <div class="forecast-alert" :class="getAlertClass(forecasts.memory.alert_level)">
              {{ getAlertMessage(forecasts.memory.alert_level) }}
            </div>
          </div>
        </div>

        <div class="forecast-card">
          <div class="forecast-header">
            <h4 class="forecast-title">Storage Usage</h4>
            <span class="forecast-period">Next 30 days</span>
          </div>
          <div class="forecast-content">
            <div class="forecast-current">
              Current: {{ forecasts.storage.current }}%
            </div>
            <div class="forecast-predicted">
              Predicted: {{ forecasts.storage.predicted }}%
            </div>
            <div class="forecast-alert" :class="getAlertClass(forecasts.storage.alert_level)">
              {{ getAlertMessage(forecasts.storage.alert_level) }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Optimization Recommendations -->
    <div v-if="recommendations" class="recommendations-section">
      <h3 class="subsection-title">Optimization Recommendations</h3>
      <div class="recommendations-list">
        <div
          v-for="recommendation in recommendations"
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
          <div class="recommendation-details">
            <div class="detail-item">
              <span class="detail-label">Current Value:</span>
              <span class="detail-value">{{ recommendation.current_value }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">Target Value:</span>
              <span class="detail-value">{{ recommendation.target_value }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">Implementation Effort:</span>
              <span class="detail-value">{{ recommendation.effort }}</span>
            </div>
          </div>
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

    <!-- Empty State -->
    <div v-if="!metrics && !loading" class="empty-state">
      <ChartBarIcon class="w-12 h-12 text-gray-400 mx-auto mb-4" />
      <h3 class="empty-title">No Performance Data Available</h3>
      <p class="empty-description">
        Performance metrics will appear here once data is collected.
      </p>
      <button @click="$emit('refresh')" class="btn-primary mt-4">
        Refresh Metrics
      </button>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, nextTick } from 'vue'
import {
  ChartBarIcon,
  ArrowPathIcon,
  ClockIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  ArrowUpIcon,
  ArrowDownIcon,
  MinusIcon,
  ExclamationCircleIcon
} from '@heroicons/vue/24/outline'

export default {
  name: 'PerformanceAnalytics',
  props: {
    metrics: {
      type: Object,
      default: null
    },
    forecasts: {
      type: Object,
      default: null
    },
    recommendations: {
      type: Array,
      default: () => []
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  emits: ['refresh'],
  setup() {
    const responseTimeChart = ref(null)
    const throughputChart = ref(null)

    const formatDuration = (seconds) => {
      if (!seconds) return '0ms'
      if (seconds < 1) return `${(seconds * 1000).toFixed(0)}ms`
      return `${seconds.toFixed(2)}s`
    }

    const formatNumber = (number) => {
      if (!number) return '0'
      return new Intl.NumberFormat().format(number)
    }

    const formatTrend = (trend) => {
      if (!trend) return 'No change'
      const sign = trend > 0 ? '+' : ''
      return `${sign}${trend.toFixed(1)}%`
    }

    const getTrendIcon = (trend) => {
      if (trend > 0) return ArrowUpIcon
      if (trend < 0) return ArrowDownIcon
      return MinusIcon
    }

    const getTrendClass = (trend) => {
      if (trend > 0) return 'text-green-600 bg-green-100'
      if (trend < 0) return 'text-red-600 bg-red-100'
      return 'text-gray-600 bg-gray-100'
    }

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

    const getAlertClass = (alertLevel) => {
      const classMap = {
        'critical': 'text-red-600 bg-red-100',
        'warning': 'text-yellow-600 bg-yellow-100',
        'info': 'text-blue-600 bg-blue-100',
        'ok': 'text-green-600 bg-green-100'
      }
      return classMap[alertLevel] || 'text-gray-600 bg-gray-100'
    }

    const getAlertMessage = (alertLevel) => {
      const messageMap = {
        'critical': 'Immediate action required',
        'warning': 'Monitor closely',
        'info': 'Within normal range',
        'ok': 'All systems optimal'
      }
      return messageMap[alertLevel] || 'Unknown status'
    }

    const createSimpleChart = (canvas, data, label, color) => {
      if (!canvas || !data) return

      const ctx = canvas.getContext('2d')
      const width = canvas.width
      const height = canvas.height

      // Clear canvas
      ctx.clearRect(0, 0, width, height)

      // Draw simple line chart
      ctx.strokeStyle = color
      ctx.lineWidth = 2
      ctx.beginPath()

      const stepX = width / (data.length - 1)
      const maxValue = Math.max(...data)
      const minValue = Math.min(...data)
      const range = maxValue - minValue || 1

      data.forEach((value, index) => {
        const x = index * stepX
        const y = height - ((value - minValue) / range) * height
        
        if (index === 0) {
          ctx.moveTo(x, y)
        } else {
          ctx.lineTo(x, y)
        }
      })

      ctx.stroke()

      // Draw points
      ctx.fillStyle = color
      data.forEach((value, index) => {
        const x = index * stepX
        const y = height - ((value - minValue) / range) * height
        ctx.beginPath()
        ctx.arc(x, y, 3, 0, 2 * Math.PI)
        ctx.fill()
      })
    }

    onMounted(() => {
      nextTick(() => {
        // Create sample charts if data is available
        if (responseTimeChart.value) {
          const sampleData = [0.1, 0.15, 0.12, 0.18, 0.14, 0.16, 0.13]
          createSimpleChart(responseTimeChart.value, sampleData, 'Response Time', '#3B82F6')
        }

        if (throughputChart.value) {
          const sampleData = [100, 120, 110, 140, 130, 135, 125]
          createSimpleChart(throughputChart.value, sampleData, 'Throughput', '#10B981')
        }
      })
    })

    return {
      responseTimeChart,
      throughputChart,
      formatDuration,
      formatNumber,
      formatTrend,
      getTrendIcon,
      getTrendClass,
      getPriorityIcon,
      getPriorityClass,
      getAlertClass,
      getAlertMessage
    }
  }
}
</script>

<style scoped>
.performance-analytics {
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

.metrics-overview {
  @apply space-y-4;
}

.subsection-title {
  @apply text-lg font-medium text-gray-900;
}

.metrics-grid {
  @apply grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4;
}

.metric-card {
  @apply bg-white border border-gray-200 rounded-lg p-4;
}

.metric-icon {
  @apply p-2 rounded-lg mb-3;
}

.metric-content {
  @apply space-y-2;
}

.metric-title {
  @apply text-sm font-medium text-gray-600;
}

.metric-value {
  @apply text-2xl font-bold;
}

.metric-trend {
  @apply flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium;
}

.charts-section {
  @apply space-y-4;
}

.charts-grid {
  @apply grid grid-cols-1 lg:grid-cols-2 gap-6;
}

.chart-card {
  @apply bg-white border border-gray-200 rounded-lg p-4;
}

.chart-title {
  @apply font-medium text-gray-900 mb-4;
}

.chart-container {
  @apply w-full h-48;
}

.forecasting-section {
  @apply space-y-4;
}

.forecast-cards {
  @apply grid grid-cols-1 md:grid-cols-3 gap-4;
}

.forecast-card {
  @apply bg-white border border-gray-200 rounded-lg p-4;
}

.forecast-header {
  @apply flex items-center justify-between mb-3;
}

.forecast-title {
  @apply font-medium text-gray-900;
}

.forecast-period {
  @apply text-xs text-gray-500;
}

.forecast-content {
  @apply space-y-2;
}

.forecast-current {
  @apply text-sm text-gray-600;
}

.forecast-predicted {
  @apply text-sm text-gray-600;
}

.forecast-alert {
  @apply px-2 py-1 rounded-full text-xs font-medium;
}

.recommendations-section {
  @apply space-y-4;
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

.recommendation-details {
  @apply grid grid-cols-3 gap-4 mb-3;
}

.detail-item {
  @apply flex flex-col;
}

.detail-label {
  @apply text-xs text-gray-500;
}

.detail-value {
  @apply text-sm font-medium text-gray-900;
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
</style>
