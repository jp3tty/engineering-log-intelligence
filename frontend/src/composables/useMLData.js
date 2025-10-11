/**
 * ML Data Composable
 * ==================
 * 
 * Reusable composable for fetching ML predictions and anomaly data
 * from the lightweight ML API.
 * 
 * Author: Engineering Log Intelligence Team
 * Date: October 11, 2025
 */

import { ref, computed } from 'vue'

export function useMLData() {
  const mlStatus = ref(null)
  const mlStats = ref(null)
  const mlPredictions = ref([])
  const loading = ref(false)
  const error = ref(null)

  /**
   * Fetch ML system status
   */
  const fetchMLStatus = async () => {
    try {
      const response = await fetch('/api/ml_lightweight?action=status')
      const data = await response.json()
      mlStatus.value = data
      return data
    } catch (err) {
      console.error('Error fetching ML status:', err)
      error.value = err.message
      return null
    }
  }

  /**
   * Fetch ML statistics
   */
  const fetchMLStats = async () => {
    try {
      const response = await fetch('/api/ml_lightweight?action=stats')
      const data = await response.json()
      mlStats.value = data
      return data
    } catch (err) {
      console.error('Error fetching ML stats:', err)
      error.value = err.message
      return null
    }
  }

  /**
   * Fetch ML predictions
   */
  const fetchMLPredictions = async () => {
    try {
      const response = await fetch('/api/ml_lightweight?action=analyze')
      const data = await response.json()
      mlPredictions.value = data.results || []
      return data
    } catch (err) {
      console.error('Error fetching ML predictions:', err)
      error.value = err.message
      return null
    }
  }

  /**
   * Fetch all ML data at once
   */
  const fetchAllMLData = async () => {
    loading.value = true
    error.value = null
    
    try {
      await Promise.all([
        fetchMLStatus(),
        fetchMLStats(),
        fetchMLPredictions()
      ])
    } catch (err) {
      console.error('Error fetching ML data:', err)
      error.value = err.message
    } finally {
      loading.value = false
    }
  }

  /**
   * Get ML anomalies only
   */
  const mlAnomalies = computed(() => {
    return mlPredictions.value.filter(pred => pred.is_anomaly)
  })

  /**
   * Get high severity predictions
   */
  const highSeverityPredictions = computed(() => {
    return mlPredictions.value.filter(pred => pred.severity === 'high')
  })

  /**
   * Get high severity count from stats
   */
  const highSeverityCount = computed(() => {
    // Try to get from stats first
    if (mlStats.value?.statistics?.severity_distribution) {
      const highSeverity = mlStats.value.statistics.severity_distribution.find(
        s => s.severity === 'high'
      )
      if (highSeverity) return highSeverity.count
    }
    // Fall back to counting predictions
    return highSeverityPredictions.value.length
  })

  /**
   * Get anomaly count
   * Prioritizes mlStats (from /stats endpoint) over counting mlPredictions
   */
  const anomalyCount = computed(() => {
    // If we have stats data, use it (more efficient)
    if (mlStats.value?.statistics?.anomalies_detected != null) {
      return mlStats.value.statistics.anomalies_detected
    }
    // Otherwise fall back to counting predictions
    return mlAnomalies.value.length
  })

  /**
   * Get anomaly rate
   * Prioritizes mlStats over calculating from predictions
   */
  const anomalyRate = computed(() => {
    // If we have stats data, use it
    if (mlStats.value?.statistics?.anomaly_rate != null) {
      return mlStats.value.statistics.anomaly_rate * 100 // Convert to percentage
    }
    // Otherwise calculate from predictions
    if (mlPredictions.value.length === 0) return 0
    return (mlAnomalies.value.length / mlPredictions.value.length) * 100
  })

  /**
   * Get ML system health
   */
  const mlSystemHealth = computed(() => {
    if (!mlStatus.value) return 'unknown'
    return mlStatus.value.ml_system || 'unknown'
  })

  /**
   * Check if ML is active
   */
  const isMLActive = computed(() => {
    return mlSystemHealth.value === 'active'
  })

  /**
   * Get formatted ML anomalies for Analytics page
   */
  const formattedAnomalies = computed(() => {
    return mlAnomalies.value.map((anomaly, index) => ({
      id: anomaly.log_id || `anomaly-${index}`,
      title: `${anomaly.predicted_level}: ${truncate(anomaly.message, 60)}`,
      description: anomaly.message,
      severity: anomaly.severity || 'medium',
      confidence: anomaly.anomaly_score || 0.5,
      detected_at: anomaly.predicted_at,
      affected_systems: [anomaly.actual_level || 'system'], // Could be enhanced
      log_id: anomaly.log_id,
      level_confidence: anomaly.level_confidence
    }))
  })

  /**
   * Helper: Truncate text
   */
  const truncate = (text, length) => {
    if (!text) return ''
    return text.length > length ? text.substring(0, length) + '...' : text
  }

  return {
    // State
    mlStatus,
    mlStats,
    mlPredictions,
    loading,
    error,

    // Computed
    mlAnomalies,
    highSeverityPredictions,
    highSeverityCount,
    anomalyCount,
    anomalyRate,
    mlSystemHealth,
    isMLActive,
    formattedAnomalies,

    // Methods
    fetchMLStatus,
    fetchMLStats,
    fetchMLPredictions,
    fetchAllMLData
  }
}

