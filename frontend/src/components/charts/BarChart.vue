<template>
  <div class="bar-chart-container">
    <div class="chart-header" v-if="options?.plugins?.title?.text">
      <h3 class="chart-title">{{ options.plugins.title.text }}</h3>
    </div>
    <div class="chart-content">
      <svg :width="chartWidth" :height="chartHeight" class="bar-chart-svg">
        <!-- Grid lines -->
        <defs>
          <pattern id="barGrid" width="40" height="40" patternUnits="userSpaceOnUse">
            <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#f3f4f6" stroke-width="1"/>
          </pattern>
        </defs>
        <rect width="100%" height="100%" fill="url(#barGrid)" />
        
        <!-- Chart area -->
        <g :transform="`translate(${padding.left}, ${padding.top})`">
          <!-- Y-axis labels -->
          <g class="y-axis">
            <text
              v-for="(label, index) in yAxisLabels"
              :key="index"
              :x="-10"
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
              :x="xScale(index) + barWidth / 2"
              :y="chartAreaHeight + 20"
              text-anchor="middle"
              class="axis-label"
            >
              {{ label }}
            </text>
          </g>
          
          <!-- Bars -->
          <g v-for="(dataset, datasetIndex) in chartData" :key="datasetIndex">
            <rect
              v-for="(value, index) in dataset.data"
              :key="index"
              :x="xScale(index)"
              :y="yScale(value)"
              :width="barWidth"
              :height="chartAreaHeight - yScale(value)"
              :fill="dataset.backgroundColor?.[index] || dataset.backgroundColor || '#3b82f6'"
              :stroke="'#ffffff'"
              :stroke-width="1"
              class="bar"
              @mouseenter="highlightBar(index)"
              @mouseleave="unhighlightBar(index)"
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
  name: 'BarChart',
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
    const chartWidth = ref(400)
    const chartHeight = ref(300)
    const padding = ref({ top: 20, right: 20, bottom: 40, left: 60 })

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

    // Bar width calculation
    const barWidth = computed(() => {
      if (xAxisLabels.value.length === 0) return 20
      return Math.max(20, chartAreaWidth.value / xAxisLabels.value.length * 0.8)
    })

    // Scaling functions
    const xScale = (index) => {
      if (xAxisLabels.value.length <= 1) return chartAreaWidth.value / 2 - barWidth.value / 2
      return (index / xAxisLabels.value.length) * chartAreaWidth.value
    }

    const yScale = (value) => {
      const { min, max } = yAxisRange.value
      if (max === min) return chartAreaHeight.value / 2
      return chartAreaHeight.value - ((value - min) / (max - min)) * chartAreaHeight.value
    }

    // Highlight functions
    const highlightBar = (index) => {
      // Could add highlighting logic here
    }

    const unhighlightBar = (index) => {
      // Could add unhighlighting logic here
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
      chartAreaHeight,
      chartAreaWidth,
      barWidth,
      xScale,
      yScale,
      highlightBar,
      unhighlightBar
    }
  }
}
</script>

<style scoped>
.bar-chart-container {
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

.bar-chart-svg {
  width: 100%;
  height: 100%;
  display: block;
}

.axis-label {
  font-size: 12px;
  fill: #6b7280;
  font-family: system-ui, -apple-system, sans-serif;
}

.bar {
  transition: all 0.2s ease;
  cursor: pointer;
}

.bar:hover {
  opacity: 0.8;
  transform: scaleY(1.05);
  transform-origin: bottom;
}

.y-axis text {
  font-size: 11px;
}

.x-axis text {
  font-size: 11px;
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
