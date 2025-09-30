<template>
  <div class="pie-chart-container">
    <div class="chart-content">
      <!-- Pie Chart -->
      <div class="pie-chart">
        <svg :width="chartSize" :height="chartSize" class="pie-svg">
          <g :transform="`translate(${chartSize/2}, ${chartSize/2})`">
            <path
              v-for="(slice, index) in pieSlices"
              :key="index"
              :d="slice.path"
              :fill="slice.color"
              :stroke="'#ffffff'"
              :stroke-width="2"
              class="pie-slice"
              @mouseenter="highlightSlice(index)"
              @mouseleave="unhighlightSlice(index)"
            />
          </g>
        </svg>
      </div>
      
      <!-- Legend -->
      <div class="legend">
        <div class="legend-title">Log Levels</div>
        <div class="legend-items">
          <div
            v-for="(item, index) in legendItems"
            :key="index"
            class="legend-item"
            @mouseenter="highlightSlice(index)"
            @mouseleave="unhighlightSlice(index)"
          >
            <div class="legend-color" :style="{ backgroundColor: item.color }"></div>
            <div class="legend-text">
              <span class="legend-label">{{ item.label }}</span>
              <span class="legend-percentage">{{ item.percentage }}%</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch } from 'vue'

export default {
  name: 'PieChart',
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
    const chartSize = ref(200)
    const highlightedSlice = ref(-1)

    // Calculate pie slices
    const pieSlices = computed(() => {
      if (!props.data || !props.data.datasets || !props.data.datasets[0]) {
        return []
      }

      const dataset = props.data.datasets[0]
      const labels = props.data.labels || []
      const data = dataset.data || []
      const colors = dataset.backgroundColor || []

      const total = data.reduce((sum, value) => sum + value, 0)
      let currentAngle = 0

      return data.map((value, index) => {
        const percentage = (value / total) * 100
        const angle = (value / total) * 2 * Math.PI
        const radius = chartSize.value / 2 - 10

        const startAngle = currentAngle
        const endAngle = currentAngle + angle

        // Create arc path
        const x1 = Math.cos(startAngle) * radius
        const y1 = Math.sin(startAngle) * radius
        const x2 = Math.cos(endAngle) * radius
        const y2 = Math.sin(endAngle) * radius

        const largeArcFlag = angle > Math.PI ? 1 : 0

        const path = [
          `M 0 0`,
          `L ${x1} ${y1}`,
          `A ${radius} ${radius} 0 ${largeArcFlag} 1 ${x2} ${y2}`,
          'Z'
        ].join(' ')

        currentAngle += angle

        return {
          path,
          color: colors[index] || '#cccccc',
          label: labels[index] || `Item ${index + 1}`,
          value,
          percentage: Math.round(percentage * 10) / 10
        }
      })
    })

    // Create legend items
    const legendItems = computed(() => {
      return pieSlices.value.map(slice => ({
        label: slice.label,
        color: slice.color,
        percentage: slice.percentage
      }))
    })

    // Highlight functions
    const highlightSlice = (index) => {
      highlightedSlice.value = index
    }

    const unhighlightSlice = (index) => {
      highlightedSlice.value = -1
    }

    // Watch for data changes
    watch(() => props.data, () => {
      // Recalculate when data changes
    }, { deep: true })

    return {
      chartSize,
      pieSlices,
      legendItems,
      highlightedSlice,
      highlightSlice,
      unhighlightSlice
    }
  }
}
</script>

<style scoped>
.pie-chart-container {
  width: 100%;
  height: 100%;
  min-height: 300px;
}

.chart-content {
  display: flex;
  align-items: center;
  gap: 20px;
  height: 100%;
}

.pie-chart {
  flex-shrink: 0;
}

.pie-svg {
  display: block;
}

.pie-slice {
  cursor: pointer;
  transition: all 0.2s ease;
  opacity: 0.8;
}

.pie-slice:hover {
  opacity: 1;
  transform: scale(1.05);
  transform-origin: center;
}

.legend {
  flex: 1;
  padding: 10px;
}

.legend-title {
  font-size: 14px;
  font-weight: 600;
  color: #374151;
  margin-bottom: 12px;
}

.legend-items {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 8px;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.legend-item:hover {
  background-color: #f3f4f6;
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  flex-shrink: 0;
  border: 2px solid #ffffff;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.legend-text {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex: 1;
  font-size: 13px;
}

.legend-label {
  color: #374151;
  font-weight: 500;
}

.legend-percentage {
  color: #6b7280;
  font-weight: 600;
  margin-left: 8px;
}

/* Responsive design */
@media (max-width: 640px) {
  .chart-content {
    flex-direction: column;
    gap: 16px;
  }
  
  .legend {
    width: 100%;
  }
  
  .legend-items {
    flex-direction: row;
    flex-wrap: wrap;
    gap: 12px;
  }
  
  .legend-item {
    flex: 1;
    min-width: 120px;
  }
}
</style>