<template>
  <div class="metric-card">
    <div class="metric-header">
      <div class="metric-icon" :class="iconClass">
        <component :is="metricIcon" class="w-6 h-6" />
      </div>
      <div class="metric-trend" :class="trendClass">
        <component :is="trendIcon" class="w-4 h-4" />
        <span class="trend-value">{{ formattedTrend }}</span>
      </div>
    </div>
    
    <div class="metric-content">
      <h3 class="metric-title">{{ metric.title }}</h3>
      <div class="metric-value" :class="valueClass">
        {{ formattedValue }}
      </div>
      <div class="metric-description" v-if="metric.description">
        {{ metric.description }}
      </div>
    </div>
  </div>
</template>

<script>
import { computed } from 'vue'
import {
  ChartBarIcon,
  ExclamationTriangleIcon,
  ClockIcon,
  CheckCircleIcon,
  ArrowUpIcon,
  ArrowDownIcon,
  MinusIcon
} from '@heroicons/vue/24/outline'

export default {
  name: 'MetricCard',
  props: {
    metric: {
      type: Object,
      required: true
    },
    trend: {
      type: Number,
      default: 0
    }
  },
  emits: [],
  setup(props) {
    // Icon mapping based on metric color
    const iconMap = {
      blue: ChartBarIcon,
      red: ExclamationTriangleIcon,
      green: CheckCircleIcon,
      emerald: CheckCircleIcon,
      yellow: ClockIcon,
      purple: ChartBarIcon,
      indigo: ChartBarIcon,
      pink: ExclamationTriangleIcon
    }

    // Metric icon
    const metricIcon = computed(() => {
      return iconMap[props.metric.color] || ChartBarIcon
    })

    // Icon class based on color
    const iconClass = computed(() => {
      const colorMap = {
        blue: 'bg-blue-100 text-blue-600',
        red: 'bg-red-100 text-red-600',
        green: 'bg-green-100 text-green-600',
        emerald: 'bg-emerald-100 text-emerald-600',
        yellow: 'bg-yellow-100 text-yellow-600',
        purple: 'bg-purple-100 text-purple-600',
        indigo: 'bg-indigo-100 text-indigo-600',
        pink: 'bg-pink-100 text-pink-600'
      }
      return colorMap[props.metric.color] || 'bg-gray-100 text-gray-600'
    })

    // Value class based on color
    const valueClass = computed(() => {
      const colorMap = {
        blue: 'text-blue-600',
        red: 'text-red-600',
        green: 'text-green-600',
        emerald: 'text-emerald-600',
        yellow: 'text-yellow-600',
        purple: 'text-purple-600',
        indigo: 'text-indigo-600',
        pink: 'text-pink-600'
      }
      return colorMap[props.metric.color] || 'text-gray-600'
    })

    // Trend icon and class
    const trendIcon = computed(() => {
      if (props.trend > 0) return ArrowUpIcon
      if (props.trend < 0) return ArrowDownIcon
      return MinusIcon
    })

    const trendClass = computed(() => {
      if (props.trend > 0) return 'text-green-600 bg-green-100'
      if (props.trend < 0) return 'text-red-600 bg-red-100'
      return 'text-gray-600 bg-gray-100'
    })

    // Formatted value based on format type
    const formattedValue = computed(() => {
      const value = props.metric.value
      const format = props.metric.format || 'number'

      switch (format) {
        case 'number':
          return new Intl.NumberFormat().format(value)
        
        case 'percentage':
          return `${value}%`
        
        case 'duration':
          return formatDuration(value)
        
        case 'currency':
          return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD'
          }).format(value)
        
        case 'bytes':
          return formatBytes(value)
        
        default:
          return value
      }
    })

    // Formatted trend
    const formattedTrend = computed(() => {
      const trend = props.trend
      if (trend === 0) return 'No change'
      
      const sign = trend > 0 ? '+' : ''
      return `${sign}${trend.toFixed(1)}%`
    })

    // Helper functions
    const formatDuration = (seconds) => {
      if (seconds < 60) return `${seconds.toFixed(2)}s`
      if (seconds < 3600) return `${(seconds / 60).toFixed(1)}m`
      return `${(seconds / 3600).toFixed(1)}h`
    }

    const formatBytes = (bytes) => {
      if (bytes === 0) return '0 B'
      
      const k = 1024
      const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      
      return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`
    }

    return {
      metricIcon,
      iconClass,
      valueClass,
      trendIcon,
      trendClass,
      formattedValue,
      formattedTrend
    }
  }
}
</script>

<style scoped>
.metric-card {
  @apply bg-white rounded-lg border border-gray-200 p-6 hover:shadow-md transition-shadow;
}

.metric-header {
  @apply flex items-center justify-between mb-4;
}

.metric-icon {
  @apply p-2 rounded-lg;
}

.metric-trend {
  @apply flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium;
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

.metric-description {
  @apply text-xs text-gray-500;
}
</style>
