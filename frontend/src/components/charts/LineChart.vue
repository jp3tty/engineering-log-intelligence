<template>
  <div class="line-chart-container">
    <div class="chart-header" v-if="options?.plugins?.title?.text">
      <h3 class="chart-title">{{ options.plugins.title.text }}</h3>
    </div>
    <div class="chart-content">
      <svg :width="chartWidth" :height="chartHeight" class="line-chart-svg">
        <!-- Grid lines -->
        <defs>
          <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
            <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#f3f4f6" stroke-width="1"/>
          </pattern>
        </defs>
        <rect width="100%" height="100%" fill="url(#grid)" />
        
        <!-- Chart area -->
        <g :transform="`translate(${padding.left}, ${padding.top})`">
          <!-- Y-axis labels -->
          <g class="y-axis">
            <text
              v-for="(label, index) in yAxisLabels"
              :key="index"
              :x="-15"
              :y="yScale(label)"
              text-anchor="end"
              dominant-baseline="middle"
              class="axis-label"
            >
              {{ label }}
            </text>
          </g>
          
          <!-- X-axis labels -->
          <g class="x-axis">
            <text
              v-for="(label, index) in xAxisLabels"
              :key="index"
              :x="xScale(index)"
              :y="chartAreaHeight + 20"
              text-anchor="middle"
              class="axis-label"
            >
              {{ label }}
            </text>
          </g>
          
          <!-- Y-axis title background -->
          <rect x="-85" y="80" width="30" height="140" fill="white" stroke="#e5e7eb" stroke-width="1" rx="4"/>
          
          <!-- Y-axis title -->
          <text
            x="20"
            y="60"
            text-anchor="middle"
            dominant-baseline="middle"
            class="axis-title"
            transform="rotate(-90, 20, 150)"
          >
            {{ yAxisTitle }}
          </text>
          
          <!-- X-axis title background -->
          <rect x="150" y="310" width="100" height="25" fill="white" stroke="#e5e7eb" stroke-width="1" rx="4"/>
          
          <!-- X-axis title -->
          <text
            x="200"
            y="325"
            text-anchor="middle"
            dominant-baseline="middle"
            class="axis-title"
          >
            {{ xAxisTitle }}
          </text>
          
          <!-- Data lines -->
          <g v-for="(dataset, datasetIndex) in chartData" :key="datasetIndex">
            <path
              :d="createLinePath(dataset.data)"
              :stroke="dataset.borderColor || '#3b82f6'"
              :stroke-width="dataset.borderWidth || 2"
              :fill="'none'"
              class="data-line"
            />
            
            <!-- Data points -->
            <circle
              v-for="(point, pointIndex) in dataset.data"
              :key="pointIndex"
              :cx="xScale(pointIndex)"
              :cy="yScale(point)"
              :r="4"
              :fill="dataset.borderColor || '#3b82f6'"
              :stroke="'#ffffff'"
              :stroke-width="2"
              class="data-point"
            />
          </g>
        </g>
      </svg>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch } from 'vue'

export default {
  name: 'LineChart',
  props: {
    data: {
      type: Object,
      required: true
    },
    options: {
      type: Object,
      default: () => ({})
    },
    height: {
      type: Number,
      default: 300
    }
  },
  setup(props) {
    const chartWidth = ref(500) // Increased to accommodate axis titles
    const chartHeight = ref(350) // Increased to accommodate axis titles
    const padding = ref({ top: 20, right: 20, bottom: 60, left: 100 }) // Increased left and bottom padding

    // Chart data processing
    const chartData = computed(() => {
      if (!props.data || !props.data.datasets) {
        return []
      }
      return props.data.datasets.map(dataset => ({
        ...dataset,
        data: dataset.data || []
      }))
    })

    const xAxisLabels = computed(() => {
      return props.data?.labels || []
    })

    // Axis titles from options
    const xAxisTitle = computed(() => {
      return props.options?.scales?.x?.title?.text || 'X Axis'
    })

    const yAxisTitle = computed(() => {
      return props.options?.scales?.y?.title?.text || 'Y Axis'
    })

    // Calculate Y-axis range and labels
    const yAxisRange = computed(() => {
      if (!chartData.value.length) return { min: 0, max: 100 }
      
      const allValues = chartData.value.flatMap(dataset => dataset.data)
      const min = Math.min(...allValues)
      const max = Math.max(...allValues)
      
      const padding = (max - min) * 0.1
      return {
        min: Math.max(0, min - padding),
        max: max + padding
      }
    })

    const yAxisLabels = computed(() => {
      const { min, max } = yAxisRange.value
      const step = (max - min) / 4
      return Array.from({ length: 5 }, (_, i) => Math.round(min + step * i))
    })

    const chartAreaHeight = computed(() => chartHeight.value - padding.value.top - padding.value.bottom)
    const chartAreaWidth = computed(() => chartWidth.value - padding.value.left - padding.value.right)

    // Scaling functions
    const xScale = (index) => {
      if (xAxisLabels.value.length <= 1) return chartAreaWidth.value / 2
      return (index / (xAxisLabels.value.length - 1)) * chartAreaWidth.value
    }

    const yScale = (value) => {
      const { min, max } = yAxisRange.value
      if (max === min) return chartAreaHeight.value / 2
      return chartAreaHeight.value - ((value - min) / (max - min)) * chartAreaHeight.value
    }

    // Create line path
    const createLinePath = (data) => {
      if (!data || data.length === 0) return ''
      
      const points = data.map((value, index) => {
        const x = xScale(index)
        const y = yScale(value)
        return `${x},${y}`
      })
      
      return `M ${points.join(' L ')}`
    }

    // Watch for data changes
    watch(() => props.data, () => {
      // Recalculate when data changes
    }, { deep: true })

    return {
      chartWidth,
      chartHeight,
      padding,
      chartData,
      xAxisLabels,
      yAxisLabels,
      xAxisTitle,
      yAxisTitle,
      chartAreaHeight,
      chartAreaWidth,
      xScale,
      yScale,
      createLinePath
    }
  }
}
</script>

<style scoped>
.line-chart-container {
  width: 100%;
  height: 100%;
  min-height: 300px;
}

.chart-header {
  margin-bottom: 16px;
}

.chart-title {
  font-size: 16px;
  font-weight: 600;
  color: #374151;
  margin: 0;
}

.chart-content {
  width: 100%;
  height: 100%;
  overflow: visible;
}

.line-chart-svg {
  width: 100%;
  height: 100%;
  display: block;
}

.axis-label {
  font-size: 12px;
  fill: #374151;
  font-family: system-ui, -apple-system, sans-serif;
  font-weight: 500;
}

.data-line {
  stroke-linecap: round;
  stroke-linejoin: round;
  transition: stroke-width 0.2s ease;
}

.data-line:hover {
  stroke-width: 3;
}

.data-point {
  transition: r 0.2s ease;
  cursor: pointer;
}

.data-point:hover {
  r: 6;
}

.y-axis text {
  font-size: 12px;
  fill: #374151;
  font-weight: 500;
}

.x-axis text {
  font-size: 11px;
}

.axis-title {
  font-size: 12px;
  font-weight: bold;
  fill: #374151;
  font-family: system-ui, -apple-system, sans-serif;
}

/* Responsive adjustments */
@media (max-width: 640px) {
  .chart-title {
    font-size: 14px;
  }
  
  .axis-label {
    font-size: 10px;
  }
}
</style>