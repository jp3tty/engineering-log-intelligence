<template>
  <div class="treemap-container">
    <div class="chart-content">
      <svg :width="chartWidth" :height="chartHeight" class="treemap-svg">
        <!-- Service Blocks -->
        <g v-for="(service, index) in services" :key="index">
          <rect
            :x="service.x"
            :y="service.y"
            :width="service.width"
            :height="service.height"
            :fill="getStatusColor(service.status)"
            :stroke="'#ffffff'"
            :stroke-width="2"
            class="service-block"
            @mouseenter="showTooltip($event, service)"
            @mouseleave="hideTooltip"
            @mousemove="updateTooltipPosition($event)"
          />
          
          <!-- Service Label -->
          <text
            v-if="service.width > 60 && service.height > 40"
            :x="service.x + service.width / 2"
            :y="service.y + service.height / 2 - 8"
            text-anchor="middle"
            dominant-baseline="middle"
            class="service-label"
            fill="white"
            font-weight="600"
            font-size="13"
          >
            {{ service.name }}
          </text>
          
          <!-- Service Status -->
          <text
            v-if="service.width > 60 && service.height > 60"
            :x="service.x + service.width / 2"
            :y="service.y + service.height / 2 + 8"
            text-anchor="middle"
            dominant-baseline="middle"
            class="service-status"
            fill="white"
            font-size="11"
          >
            {{ service.status }}
          </text>
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
import { ref, computed, onMounted } from 'vue'

export default {
  name: 'TreeMapChart',
  props: {
    data: {
      type: Array,
      default: () => []
    },
    height: {
      type: Number,
      default: 300
    }
  },
  setup(props) {
    const chartWidth = ref(500)
    const chartHeight = ref(300)
    
    // Tooltip state
    const tooltip = ref({
      visible: false,
      x: 0,
      y: 0,
      title: '',
      lines: []
    })

    // Default service data if none provided
    const defaultServices = [
      { name: 'PostgreSQL', status: 'healthy', importance: 30, responseTime: 25, uptime: 99.9 },
      { name: 'Elasticsearch', status: 'healthy', importance: 25, responseTime: 45, uptime: 99.5 },
      { name: 'Kafka', status: 'warning', importance: 20, responseTime: 120, uptime: 98.2 },
      { name: 'API Gateway', status: 'healthy', importance: 15, responseTime: 15, uptime: 99.8 },
      { name: 'Auth Service', status: 'healthy', importance: 10, responseTime: 10, uptime: 99.9 }
    ]

    // Process service data for treemap layout
    const services = computed(() => {
      const serviceData = props.data.length > 0 ? props.data : defaultServices
      
      // Sort by importance (largest first) for better packing
      const sortedData = [...serviceData].sort((a, b) => b.importance - a.importance)
      
      // Calculate total importance
      const totalImportance = sortedData.reduce((sum, s) => sum + s.importance, 0)
      
      const containerWidth = chartWidth.value
      const containerHeight = chartHeight.value
      
      // Squarified treemap algorithm for better space utilization
      const result = []
      let currentY = 0
      
      // Process items in groups to create balanced rows
      let remainingItems = [...sortedData]
      
      while (remainingItems.length > 0 && currentY < containerHeight) {
        // Calculate how many rows we need
        const remainingHeight = containerHeight - currentY
        const avgItemsPerRow = Math.ceil(Math.sqrt(remainingItems.length))
        const targetRowHeight = Math.min(remainingHeight / Math.ceil(remainingItems.length / avgItemsPerRow), remainingHeight * 0.5)
        
        // Collect items for this row
        let rowItems = []
        let rowImportance = 0
        let currentX = 0
        
        // Try to fill a row
        for (let i = 0; i < remainingItems.length && currentX < containerWidth; i++) {
          const item = remainingItems[i]
          const proportion = item.importance / totalImportance
          const targetArea = proportion * (containerWidth * containerHeight)
          const estimatedWidth = targetArea / targetRowHeight
          
          // If adding this item would overflow, and we already have items, stop
          if (currentX + estimatedWidth > containerWidth * 1.1 && rowItems.length > 0) {
            break
          }
          
          rowItems.push(item)
          rowImportance += item.importance
          currentX += estimatedWidth
        }
        
        // Remove processed items
        remainingItems = remainingItems.slice(rowItems.length)
        
        // Calculate actual row height based on importance
        const rowProportion = rowImportance / totalImportance
        const rowHeight = Math.min(
          rowProportion * containerHeight * 1.2, // Allow slightly more height for better fit
          remainingHeight
        )
        
        // Layout items in this row
        currentX = 0
        rowItems.forEach(service => {
          const proportion = service.importance / rowImportance
          const width = proportion * containerWidth
          
          result.push({
            ...service,
            x: currentX,
            y: currentY,
            width: width,
            height: rowHeight
          })
          
          currentX += width
        })
        
        currentY += rowHeight
      }
      
      return result
    })

    // Get color based on service status
    const getStatusColor = (status) => {
      const colors = {
        'healthy': '#10b981',  // green
        'warning': '#f59e0b',  // yellow/orange
        'critical': '#ef4444', // red
        'unknown': '#6b7280'   // gray
      }
      return colors[status.toLowerCase()] || colors.unknown
    }

    // Tooltip functions
    const showTooltip = (event, service) => {
      tooltip.value = {
        visible: true,
        x: event.clientX + 15,
        y: event.clientY - 60,
        title: service.name,
        lines: [
          `Status: ${service.status.charAt(0).toUpperCase() + service.status.slice(1)}`,
          `Response Time: ${service.responseTime}ms`,
          `Uptime: ${service.uptime}%`,
          `Importance: ${service.importance}%`
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

    onMounted(() => {
      // Set responsive dimensions
      chartHeight.value = props.height
    })

    return {
      chartWidth,
      chartHeight,
      tooltip,
      services,
      getStatusColor,
      showTooltip,
      hideTooltip,
      updateTooltipPosition
    }
  }
}
</script>

<style scoped>
.treemap-container {
  width: 100%;
  height: 100%;
  min-height: 300px;
  max-height: 450px;
}

.chart-content {
  width: 100%;
  height: 100%;
  position: relative;
  overflow: hidden;
}

.treemap-svg {
  width: 100%;
  height: 100%;
  display: block;
  max-height: 400px;
}

.service-block {
  transition: all 0.2s ease;
  cursor: pointer;
}

.service-block:hover {
  opacity: 0.85;
  filter: brightness(1.1);
}

.service-label {
  pointer-events: none;
  user-select: none;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

.service-status {
  pointer-events: none;
  user-select: none;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
  opacity: 0.9;
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
  .service-label {
    font-size: 11px;
  }
  
  .service-status {
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

