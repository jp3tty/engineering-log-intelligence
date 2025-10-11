<template>
  <div class="ml-dashboard">
    <div class="ml-header">
      <h2>🤖 Machine Learning Analytics</h2>
      <button @click="refreshData" class="refresh-btn" :disabled="loading">
        <span v-if="!loading">🔄 Refresh</span>
        <span v-else>⏳ Loading...</span>
      </button>
    </div>

    <!-- ML System Status -->
    <div class="status-card" :class="`status-${mlStatus?.ml_system}`">
      <h3>System Status</h3>
      <div class="status-content">
        <div class="status-badge">
          {{ mlStatus?.ml_system === 'active' ? '✅ Active' : '⚠️ Offline' }}
        </div>
        <div class="status-details">
          <p><strong>Architecture:</strong> {{ mlStatus?.architecture || 'N/A' }}</p>
          <p><strong>Total Predictions:</strong> {{ mlStatus?.total_predictions?.toLocaleString() || '0' }}</p>
          <p><strong>Latest Update:</strong> {{ formatTime(mlStatus?.latest_prediction) }}</p>
          <p><strong>Query Time:</strong> {{ mlStatus?.query_time || 'N/A' }}</p>
        </div>
      </div>
    </div>

    <!-- Statistics -->
    <div v-if="stats" class="stats-grid">
      <div class="stat-card">
        <h4>Total Analyzed</h4>
        <div class="stat-value">{{ stats.statistics?.total_predictions?.toLocaleString() || '0' }}</div>
        <div class="stat-label">Last 24 hours</div>
      </div>
      
      <div class="stat-card anomaly">
        <h4>Anomalies Detected</h4>
        <div class="stat-value">{{ stats.statistics?.anomalies_detected?.toLocaleString() || '0' }}</div>
        <div class="stat-label">{{ ((stats.statistics?.anomaly_rate || 0) * 100).toFixed(1) }}% rate</div>
      </div>
      
      <div class="stat-card severity">
        <h4>High Severity</h4>
        <div class="stat-value">{{ getHighSeverityCount() }}</div>
        <div class="stat-label">Requires attention</div>
      </div>
    </div>

    <!-- Severity Distribution -->
    <div v-if="stats?.statistics?.severity_distribution" class="chart-card">
      <h3>Severity Distribution</h3>
      <div class="severity-chart">
        <div 
          v-for="item in stats.statistics.severity_distribution" 
          :key="item.severity"
          class="severity-bar"
        >
          <div class="severity-label">
            <span class="severity-badge" :class="`severity-${item.severity}`">
              {{ item.severity }}
            </span>
            <span class="severity-count">{{ item.count }}</span>
          </div>
          <div class="severity-bar-container">
            <div 
              class="severity-bar-fill" 
              :class="`severity-${item.severity}`"
              :style="{ width: `${(item.count / stats.statistics.total_predictions * 100)}%` }"
            ></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Recent Predictions -->
    <div v-if="predictions && predictions.length > 0" class="predictions-card">
      <h3>Recent Predictions (Last 100)</h3>
      <div class="predictions-table">
        <table>
          <thead>
            <tr>
              <th>Log ID</th>
              <th>Message</th>
              <th>Predicted</th>
              <th>Confidence</th>
              <th>Anomaly</th>
              <th>Severity</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="pred in predictions.slice(0, 20)" :key="pred.log_id" :class="{ 'anomaly-row': pred.is_anomaly }">
              <td><code>{{ pred.log_id }}</code></td>
              <td class="message-cell">{{ truncate(pred.message, 60) }}</td>
              <td><span class="level-badge" :class="`level-${pred.predicted_level?.toLowerCase()}`">{{ pred.predicted_level }}</span></td>
              <td>{{ (pred.level_confidence * 100).toFixed(1) }}%</td>
              <td>
                <span v-if="pred.is_anomaly" class="anomaly-badge">⚠️ Yes</span>
                <span v-else class="normal-badge">✓ No</span>
              </td>
              <td><span class="severity-badge" :class="`severity-${pred.severity}`">{{ pred.severity }}</span></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- No Data State -->
    <div v-if="!loading && (!predictions || predictions.length === 0)" class="no-data">
      <p>📊 No ML predictions available yet.</p>
      <p>Predictions are generated every 6 hours by GitHub Actions.</p>
      <p>Check the Actions tab in your repository to trigger a manual run.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const loading = ref(false)
const mlStatus = ref(null)
const stats = ref(null)
const predictions = ref([])

const refreshData = async () => {
  loading.value = true
  try {
    // Fetch ML status
    const statusResponse = await fetch('/api/ml_lightweight?action=status')
    mlStatus.value = await statusResponse.json()
    
    // Fetch statistics
    const statsResponse = await fetch('/api/ml_lightweight?action=stats')
    stats.value = await statsResponse.json()
    
    // Fetch recent predictions
    const predictionsResponse = await fetch('/api/ml_lightweight?action=analyze')
    const predictionsData = await predictionsResponse.json()
    predictions.value = predictionsData.results || []
    
    console.log('✅ ML Dashboard data loaded', { mlStatus: mlStatus.value, stats: stats.value, predictions: predictions.value.length })
  } catch (error) {
    console.error('❌ Error loading ML data:', error)
  } finally {
    loading.value = false
  }
}

const formatTime = (timestamp) => {
  if (!timestamp) return 'Never'
  const date = new Date(timestamp)
  const now = new Date()
  const diffMs = now - date
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  
  if (diffMins < 1) return 'Just now'
  if (diffMins < 60) return `${diffMins} min ago`
  if (diffHours < 24) return `${diffHours} hours ago`
  return date.toLocaleDateString()
}

const truncate = (text, length) => {
  if (!text) return ''
  return text.length > length ? text.substring(0, length) + '...' : text
}

const getHighSeverityCount = () => {
  if (!stats.value?.statistics?.severity_distribution) return 0
  const high = stats.value.statistics.severity_distribution.find(s => s.severity === 'high')
  return high ? high.count : 0
}

onMounted(() => {
  refreshData()
  // Auto-refresh every 5 minutes
  setInterval(refreshData, 300000)
})
</script>

<style scoped>
.ml-dashboard {
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
}

.ml-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.ml-header h2 {
  margin: 0;
  font-size: 28px;
  color: #1a1a1a;
}

.refresh-btn {
  padding: 10px 20px;
  background: #10b981;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.2s;
}

.refresh-btn:hover:not(:disabled) {
  background: #059669;
  transform: translateY(-1px);
}

.refresh-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.status-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  border-left: 4px solid #10b981;
}

.status-card.status-offline {
  border-left-color: #f59e0b;
}

.status-card h3 {
  margin: 0 0 16px 0;
  font-size: 18px;
  color: #374151;
}

.status-content {
  display: flex;
  gap: 24px;
  align-items: center;
}

.status-badge {
  font-size: 24px;
  font-weight: 700;
}

.status-details p {
  margin: 4px 0;
  color: #6b7280;
}

.status-details strong {
  color: #374151;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  border-top: 4px solid #3b82f6;
}

.stat-card.anomaly {
  border-top-color: #ef4444;
}

.stat-card.severity {
  border-top-color: #f59e0b;
}

.stat-card h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.stat-value {
  font-size: 36px;
  font-weight: 700;
  color: #1a1a1a;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: #9ca3af;
}

.chart-card, .predictions-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}

.chart-card h3, .predictions-card h3 {
  margin: 0 0 20px 0;
  font-size: 18px;
  color: #374151;
}

.severity-chart {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.severity-bar {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.severity-label {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.severity-badge {
  padding: 4px 12px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
  text-transform: capitalize;
}

.severity-badge.severity-high {
  background: #fee2e2;
  color: #dc2626;
}

.severity-badge.severity-medium {
  background: #fef3c7;
  color: #d97706;
}

.severity-badge.severity-low {
  background: #dbeafe;
  color: #2563eb;
}

.severity-badge.severity-info {
  background: #f3f4f6;
  color: #6b7280;
}

.severity-count {
  font-weight: 700;
  color: #374151;
}

.severity-bar-container {
  height: 24px;
  background: #f3f4f6;
  border-radius: 12px;
  overflow: hidden;
}

.severity-bar-fill {
  height: 100%;
  transition: width 0.5s ease;
}

.severity-bar-fill.severity-high {
  background: linear-gradient(90deg, #ef4444, #dc2626);
}

.severity-bar-fill.severity-medium {
  background: linear-gradient(90deg, #f59e0b, #d97706);
}

.severity-bar-fill.severity-low {
  background: linear-gradient(90deg, #3b82f6, #2563eb);
}

.severity-bar-fill.severity-info {
  background: linear-gradient(90deg, #9ca3af, #6b7280);
}

.predictions-table {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
}

thead {
  background: #f9fafb;
}

th {
  text-align: left;
  padding: 12px;
  font-size: 12px;
  font-weight: 600;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  border-bottom: 2px solid #e5e7eb;
}

td {
  padding: 12px;
  border-bottom: 1px solid #f3f4f6;
  font-size: 14px;
  color: #374151;
}

.anomaly-row {
  background: #fef2f2;
}

.message-cell {
  max-width: 300px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

code {
  font-family: monospace;
  background: #f3f4f6;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 12px;
}

.level-badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
}

.level-badge.level-error, .level-badge.level-fatal {
  background: #fee2e2;
  color: #dc2626;
}

.level-badge.level-warn {
  background: #fef3c7;
  color: #d97706;
}

.level-badge.level-info {
  background: #dbeafe;
  color: #2563eb;
}

.level-badge.level-debug {
  background: #f3f4f6;
  color: #6b7280;
}

.anomaly-badge {
  color: #dc2626;
  font-weight: 600;
}

.normal-badge {
  color: #10b981;
  font-weight: 600;
}

.no-data {
  text-align: center;
  padding: 60px 20px;
  color: #6b7280;
}

.no-data p {
  margin: 8px 0;
  font-size: 16px;
}
</style>

