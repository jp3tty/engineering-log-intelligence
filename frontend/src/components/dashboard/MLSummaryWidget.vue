<template>
  <div class="ml-widget">
    <div class="ml-widget-header">
      <h3>🤖 ML Anomaly Detection</h3>
      <router-link to="/ml-analytics" class="view-details-link">
        View Details →
      </router-link>
    </div>
    
    <div v-if="loading" class="widget-loading">
      <div class="spinner-small"></div>
      <span>Loading ML data...</span>
    </div>
    
    <div v-else-if="isMLActive" class="widget-content">
      <div class="ml-stats-grid">
        <div class="ml-stat">
          <div class="stat-icon anomaly">⚠️</div>
          <div class="stat-info">
            <div class="stat-value">{{ anomalyCount }}</div>
            <div class="stat-label">Anomalies</div>
          </div>
        </div>
        
        <div class="ml-stat">
          <div class="stat-icon severity">🔥</div>
          <div class="stat-info">
            <div class="stat-value">{{ highSeverityCount }}</div>
            <div class="stat-label">High Severity</div>
          </div>
        </div>
        
        <div class="ml-stat">
          <div class="stat-icon rate">📊</div>
          <div class="stat-info">
            <div class="stat-value">{{ anomalyRate.toFixed(1) }}%</div>
            <div class="stat-label">Anomaly Rate</div>
          </div>
        </div>
      </div>
      
      <div v-if="mlStats" class="ml-footer">
        <span class="status-badge active">🟢 ML Active</span>
        <span class="last-update">Updated {{ formatLastUpdate }}</span>
      </div>
    </div>
    
    <div v-else class="widget-inactive">
      <p>ML system initializing...</p>
      <router-link to="/ml-analytics" class="btn-small">View Status</router-link>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useMLData } from '@/composables/useMLData'

const {
  mlStats,
  loading,
  isMLActive,
  anomalyCount,
  highSeverityCount,
  anomalyRate,
  fetchMLStatus,
  fetchMLStats
} = useMLData()

onMounted(async () => {
  // Fetch both status and stats to properly initialize the widget
  loading.value = true
  try {
    await Promise.all([
      fetchMLStatus(),  // Needed for isMLActive check
      fetchMLStats()     // Needed for anomaly counts
    ])
  } catch (error) {
    console.error('Error loading ML data for widget:', error)
  } finally {
    loading.value = false
  }
})

const formatLastUpdate = computed(() => {
  if (!mlStats.value?.timestamp) return 'just now'
  const now = new Date()
  const updated = new Date(mlStats.value.timestamp)
  const diffMs = now - updated
  const diffMins = Math.floor(diffMs / 60000)
  
  if (diffMins < 1) return 'just now'
  if (diffMins < 60) return `${diffMins}m ago`
  const diffHours = Math.floor(diffMins / 60)
  if (diffHours < 24) return `${diffHours}h ago`
  return `${Math.floor(diffHours / 24)}d ago`
})
</script>

<style scoped>
.ml-widget {
  @apply bg-white border border-gray-200 rounded-lg p-6 shadow-sm;
}

.ml-widget-header {
  @apply flex items-center justify-between mb-4;
}

.ml-widget-header h3 {
  @apply text-lg font-semibold text-gray-900;
}

.view-details-link {
  @apply text-sm text-blue-600 hover:text-blue-700 font-medium transition-colors;
}

.widget-loading {
  @apply flex items-center justify-center gap-2 py-8 text-gray-500;
}

.spinner-small {
  @apply w-5 h-5 border-2 border-gray-300 border-t-blue-600 rounded-full animate-spin;
}

.widget-content {
  @apply space-y-4;
}

.ml-stats-grid {
  @apply grid grid-cols-3 gap-4;
}

.ml-stat {
  @apply flex items-center gap-3 p-3 bg-gray-50 rounded-lg;
}

.stat-icon {
  @apply text-2xl flex-shrink-0;
}

.stat-info {
  @apply flex flex-col;
}

.stat-value {
  @apply text-2xl font-bold text-gray-900;
}

.stat-label {
  @apply text-xs text-gray-500;
}

.ml-footer {
  @apply flex items-center justify-between pt-4 border-t border-gray-200;
}

.status-badge {
  @apply px-2 py-1 text-xs font-medium rounded;
}

.status-badge.active {
  @apply bg-green-100 text-green-700;
}

.last-update {
  @apply text-xs text-gray-500;
}

.widget-inactive {
  @apply text-center py-8;
}

.widget-inactive p {
  @apply text-gray-500 mb-3;
}

.btn-small {
  @apply px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors;
}
</style>

