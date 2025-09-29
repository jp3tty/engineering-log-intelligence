<template>
  <div class="metric-widget h-full flex flex-col">
    <!-- Widget Content -->
    <div class="flex-1 flex items-center justify-center p-4">
      <div class="text-center">
        <!-- Main Value -->
        <div class="mb-2">
          <span 
            :class="[
              'text-3xl font-bold',
              getValueColor()
            ]"
          >
            {{ formatValue(widget.config.value || 0) }}
          </span>
          <span v-if="widget.config.unit" class="text-lg text-gray-600 ml-1">
            {{ widget.config.unit }}
          </span>
        </div>

        <!-- Trend Indicator -->
        <div v-if="widget.config.trend" class="flex items-center justify-center space-x-1">
          <component
            :is="getTrendIcon()"
            :class="[
              'w-4 h-4',
              getTrendColor()
            ]"
          />
          <span :class="['text-sm font-medium', getTrendColor()]">
            {{ getTrendText() }}
          </span>
        </div>

        <!-- Additional Info -->
        <div v-if="widget.config.description" class="mt-2">
          <p class="text-xs text-gray-500">{{ widget.config.description }}</p>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="absolute inset-0 bg-white bg-opacity-75 flex items-center justify-center">
      <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
    </div>

    <!-- Error State -->
    <div v-if="error" class="absolute inset-0 bg-red-50 flex items-center justify-center">
      <div class="text-center">
        <ExclamationTriangleIcon class="w-6 h-6 text-red-500 mx-auto mb-1" />
        <p class="text-xs text-red-600">{{ error }}</p>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue'
import { 
  ArrowUpIcon, 
  ArrowDownIcon, 
  MinusIcon,
  ExclamationTriangleIcon 
} from '@heroicons/vue/24/outline'

export default {
  name: 'MetricWidget',
  components: {
    ArrowUpIcon,
    ArrowDownIcon,
    MinusIcon,
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
    const loading = ref(false)
    const error = ref(null)
    const refreshInterval = ref(null)

    // Methods
    const formatValue = (value) => {
      if (typeof value !== 'number') return '0'
      
      // Format large numbers with K, M, B suffixes
      if (value >= 1000000000) {
        return (value / 1000000000).toFixed(1) + 'B'
      } else if (value >= 1000000) {
        return (value / 1000000).toFixed(1) + 'M'
      } else if (value >= 1000) {
        return (value / 1000).toFixed(1) + 'K'
      }
      
      return value.toString()
    }

    const getValueColor = () => {
      const value = widget.config.value || 0
      const color = widget.config.color || 'blue'
      
      // Color mapping
      const colors = {
        blue: 'text-blue-600',
        green: 'text-green-600',
        yellow: 'text-yellow-600',
        red: 'text-red-600',
        purple: 'text-purple-600'
      }
      
      return colors[color] || 'text-gray-600'
    }

    const getTrendIcon = () => {
      const trend = widget.config.trend
      switch (trend) {
        case 'up': return 'ArrowUpIcon'
        case 'down': return 'ArrowDownIcon'
        default: return 'MinusIcon'
      }
    }

    const getTrendColor = () => {
      const trend = widget.config.trend
      switch (trend) {
        case 'up': return 'text-green-600'
        case 'down': return 'text-red-600'
        default: return 'text-gray-500'
      }
    }

    const getTrendText = () => {
      const trend = widget.config.trend
      switch (trend) {
        case 'up': return 'Trending Up'
        case 'down': return 'Trending Down'
        default: return 'Stable'
      }
    }

    const fetchData = async () => {
      if (props.previewMode) return
      
      loading.value = true
      error.value = null
      
      try {
        // Simulate API call - replace with actual API call
        await new Promise(resolve => setTimeout(resolve, 1000))
        
        // Mock data - replace with actual data fetching
        const mockValue = Math.floor(Math.random() * 100)
        const mockTrend = ['up', 'down', 'neutral'][Math.floor(Math.random() * 3)]
        
        // Update widget config
        props.widget.config.value = mockValue
        props.widget.config.trend = mockTrend
        
      } catch (err) {
        error.value = 'Failed to fetch data'
        console.error('Error fetching metric data:', err)
      } finally {
        loading.value = false
      }
    }

    const startAutoRefresh = () => {
      if (props.previewMode) return
      
      const interval = widget.config.refreshInterval || 30
      refreshInterval.value = setInterval(fetchData, interval * 1000)
    }

    const stopAutoRefresh = () => {
      if (refreshInterval.value) {
        clearInterval(refreshInterval.value)
        refreshInterval.value = null
      }
    }

    // Lifecycle
    onMounted(() => {
      if (!props.previewMode) {
        fetchData()
        startAutoRefresh()
      }
    })

    onUnmounted(() => {
      stopAutoRefresh()
    })

    return {
      loading,
      error,
      formatValue,
      getValueColor,
      getTrendIcon,
      getTrendColor,
      getTrendText
    }
  }
}
</script>

<style scoped>
.metric-widget {
  position: relative;
}
</style>
