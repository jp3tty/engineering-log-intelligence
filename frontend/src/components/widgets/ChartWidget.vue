<template>
  <div class="chart-widget h-full flex flex-col">
    <!-- Chart Container -->
    <div class="flex-1 relative">
      <canvas ref="chartCanvas" class="w-full h-full"></canvas>
    </div>

    <!-- Chart Controls -->
    <div v-if="!previewMode" class="flex items-center justify-between p-2 border-t border-gray-100">
      <div class="flex items-center space-x-2">
        <select
          v-model="localTimeRange"
          @change="updateTimeRange"
          class="text-xs border border-gray-300 rounded px-2 py-1 focus:outline-none focus:ring-1 focus:ring-blue-500"
        >
          <option value="5m">5m</option>
          <option value="15m">15m</option>
          <option value="1h">1h</option>
          <option value="6h">6h</option>
          <option value="24h">24h</option>
        </select>
        <button
          @click="refreshChart"
          :disabled="loading"
          class="p-1 text-gray-400 hover:text-blue-600 transition-colors disabled:opacity-50"
          title="Refresh Chart"
        >
          <ArrowPathIcon :class="['w-4 h-4', loading ? 'animate-spin' : '']" />
        </button>
      </div>
      <div class="text-xs text-gray-500">
        {{ lastUpdated }}
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="absolute inset-0 bg-white bg-opacity-75 flex items-center justify-center">
      <div class="text-center">
        <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600 mx-auto mb-2"></div>
        <p class="text-xs text-gray-600">Loading chart data...</p>
      </div>
    </div>

    <!-- Error State -->
    <div v-if="error" class="absolute inset-0 bg-red-50 flex items-center justify-center">
      <div class="text-center">
        <ExclamationTriangleIcon class="w-6 h-6 text-red-500 mx-auto mb-1" />
        <p class="text-xs text-red-600">{{ error }}</p>
        <button
          @click="refreshChart"
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
import { Chart, registerables } from 'chart.js'
import { ArrowPathIcon, ExclamationTriangleIcon } from '@heroicons/vue/24/outline'

// Register Chart.js components
Chart.register(...registerables)

export default {
  name: 'ChartWidget',
  components: {
    ArrowPathIcon,
    ExclamationTriangleIcon
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
  setup(props) {
    const chartCanvas = ref(null)
    const chartInstance = ref(null)
    const loading = ref(false)
    const error = ref(null)
    const refreshInterval = ref(null)
    const localTimeRange = ref(props.widget.config.timeRange || '1h')

    // Computed properties
    const lastUpdated = computed(() => {
      if (!props.widget.lastUpdated) return 'Never updated'
      return new Date(props.widget.lastUpdated).toLocaleTimeString()
    })

    // Methods
    const getChartType = () => {
      return props.widget.config.chartType || 'line'
    }

    const generateMockData = () => {
      const timeRange = localTimeRange.value
      const now = new Date()
      let dataPoints = 20
      let interval = 300000 // 5 minutes

      // Adjust based on time range
      switch (timeRange) {
        case '5m':
          dataPoints = 12
          interval = 25000 // 25 seconds
          break
        case '15m':
          dataPoints = 15
          interval = 60000 // 1 minute
          break
        case '1h':
          dataPoints = 20
          interval = 180000 // 3 minutes
          break
        case '6h':
          dataPoints = 24
          interval = 900000 // 15 minutes
          break
        case '24h':
          dataPoints = 24
          interval = 3600000 // 1 hour
          break
      }

      const labels = []
      const data = []

      for (let i = dataPoints; i >= 0; i--) {
        const time = new Date(now.getTime() - (i * interval))
        labels.push(time.toLocaleTimeString())
        
        // Generate mock data based on widget type
        let value = 0
        switch (props.widget.config.dataSource) {
          case 'system_metrics':
            value = Math.random() * 100
            break
          case 'application_logs':
            value = Math.floor(Math.random() * 1000)
            break
          case 'performance_data':
            value = Math.random() * 1000
            break
          default:
            value = Math.random() * 100
        }
        
        data.push(value)
      }

      return { labels, data }
    }

    const createChart = () => {
      if (!chartCanvas.value) return

      // Destroy existing chart
      if (chartInstance.value) {
        chartInstance.value.destroy()
      }

      const { labels, data } = generateMockData()
      const chartType = getChartType()

      const config = {
        type: chartType,
        data: {
          labels,
          datasets: [{
            label: props.widget.title,
            data,
            borderColor: '#3b82f6',
            backgroundColor: chartType === 'line' ? 'transparent' : '#3b82f6',
            borderWidth: 2,
            fill: chartType === 'line',
            tension: 0.4
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              display: false
            }
          },
          scales: {
            x: {
              display: true,
              ticks: {
                maxTicksLimit: 6
              }
            },
            y: {
              display: true,
              beginAtZero: true
            }
          },
          interaction: {
            intersect: false,
            mode: 'index'
          }
        }
      }

      chartInstance.value = new Chart(chartCanvas.value, config)
    }

    const updateTimeRange = () => {
      props.widget.config.timeRange = localTimeRange.value
      refreshChart()
    }

    const refreshChart = async () => {
      if (props.previewMode) return

      loading.value = true
      error.value = null

      try {
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 500))
        
        // Update chart with new data
        createChart()
        
        // Update widget timestamp
        props.widget.lastUpdated = new Date()
        
      } catch (err) {
        error.value = 'Failed to refresh chart data'
        console.error('Error refreshing chart:', err)
      } finally {
        loading.value = false
      }
    }

    const startAutoRefresh = () => {
      if (props.previewMode) return
      
      const interval = props.widget.config.refreshInterval || 30
      refreshInterval.value = setInterval(refreshChart, interval * 1000)
    }

    const stopAutoRefresh = () => {
      if (refreshInterval.value) {
        clearInterval(refreshInterval.value)
        refreshInterval.value = null
      }
    }

    // Lifecycle
    onMounted(() => {
      createChart()
      if (!props.previewMode) {
        startAutoRefresh()
      }
    })

    onUnmounted(() => {
      stopAutoRefresh()
      if (chartInstance.value) {
        chartInstance.value.destroy()
      }
    })

    return {
      chartCanvas,
      loading,
      error,
      localTimeRange,
      lastUpdated,
      updateTimeRange,
      refreshChart
    }
  }
}
</script>

<style scoped>
.chart-widget {
  position: relative;
}
</style>
