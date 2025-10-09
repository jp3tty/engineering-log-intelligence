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
              :x="xScale(index) + barWidth / 2"
              :y="chartAreaHeight + 20"
              text-anchor="middle"
              class="axis-label"
            >
              {{ label }}
            </text>
          </g>
          
          <!-- Y-axis title background -->
          <rect x="-75" y="80" width="30" height="140" fill="white" stroke="#e5e7eb" stroke-width="1" rx="4"/>
          
          <!-- Y-axis title -->
          <text
            x="20"
            y="70"
            text-anchor="middle"
            dominant-baseline="middle"
            class="axis-title"
            transform="rotate(-90, 20, 150)"
          >
            {{ yAxisTitle }}
          </text>
          
          <!-- X-axis title background -->
          <rect x="130" y="300" width="120" height="30" fill="white" stroke="#e5e7eb" stroke-width="1" rx="4"/>

          <!-- X-axis title -->
          <text
            x="190"
            y="318"
            text-anchor="middle"
            dominant-baseline="middle"
            class="axis-title"
          >
            {{ xAxisTitle }}
          </text>
          
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
              @mouseenter="showTooltip($event, index, value, dataset)"
              @mouseleave="hideTooltip"
              @mousemove="updateTooltipPosition($event)"
            />
          </g>
        </g>
      </svg>
      
      <!-- Tooltip -->
      <div 
        v-if="tooltip.visible" 
        class="chart-tooltip"
        :style="{
          left: tooltip.x + 'px',
          top: tooltip.y + 'px'
        }"
      >
        <div class="tooltip-title">{{ tooltip.title }}</div>
        <div class="tooltip-content">
          <div v-for="(line, idx) in tooltip.lines" :key="idx" class="tooltip-line">
            {{ line }}
          </div>
        </div>
      </div>
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
    const chartWidth = ref(500)
    const chartHeight = ref(350)
    const padding = ref({ top: 20, right: 20, bottom: 60, left: 100 })
    
    // Tooltip state
    const tooltip = ref({
      visible: false,
      x: 0,
      y: 0,
      title: '',
      lines: []
    })

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

    // Tooltip functions
    const showTooltip = (event, index, value, dataset) => {
      const label = xAxisLabels.value[index]
      const total = dataset.data.reduce((a, b) => a + b, 0)
      const percentage = ((value / total) * 100).toFixed(1)
      
      tooltip.value = {
        visible: true,
        x: event.clientX + 15,
        y: event.clientY - 60,
        title: `Log Level: ${label}`,
        lines: [
          `Count: ${value.toLocaleString()} logs`,
          `Percentage: ${percentage}% of total`,
          `Total 24h: ${total.toLocaleString()} logs`
        ]
      }
    }
    
    const hideTooltip = () => {
      tooltip.value.visible = false
    }
    
    const updateTooltipPosition = (event) => {
      if (tooltip.value.visible) {
        tooltip.value.x = event.clientX + 15
        tooltip.value.y = event.clientY - 60
      }
    }

    // Watch for data changes
    watch(() => props.data, () => {
      // Recalculate when data changes
    }, { deep: true })

    return {
      chartWidth,
      chartHeight,
      padding,
      tooltip,
      chartData,
      xAxisLabels,
      yAxisLabels,
      xAxisTitle,
      yAxisTitle,
      chartAreaHeight,
      chartAreaWidth,
      barWidth,
      xScale,
      yScale,
      showTooltip,
      hideTooltip,
      updateTooltipPosition
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
  padding: 0 10px;
}

.bar-chart-svg {
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

/* Specific styling for Y-axis title */
.y-axis-title {
  font-size: 12px;
  font-weight: bold;
  fill: #374151;
  font-family: system-ui, -apple-system, sans-serif;
}

/* Tooltip styling */
.chart-tooltip {
  position: fixed;
  background: rgba(0, 0, 0, 0.9);
  color: white;
  padding: 12px 16px;
  border-radius: 8px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  pointer-events: none;
  z-index: 10000;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  font-family: system-ui, -apple-system, sans-serif;
  min-width: 200px;
}

.tooltip-title {
  font-size: 14px;
  font-weight: bold;
  margin-bottom: 8px;
  padding-bottom: 8px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
}

.tooltip-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.tooltip-line {
  font-size: 13px;
  line-height: 1.5;
}

/* Responsive adjustments */
@media (max-width: 640px) {
  .chart-title {
    font-size: 14px;
  }
  
  .axis-label {
    font-size: 10px;
  }
  
  .chart-tooltip {
    font-size: 12px;
    padding: 10px 12px;
    min-width: 180px;
  }
  
  .tooltip-title {
    font-size: 13px;
  }
  
  .tooltip-line {
    font-size: 12px;
  }
}
</style>