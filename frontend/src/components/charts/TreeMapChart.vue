<template>
  <div class="treemap-chart">
    <div ref="chartContainer" class="w-full h-full relative"></div>
  </div>
</template>

<script setup>
/**
 * TreeMap Chart Component
 * ======================
 * 
 * This component creates a TreeMap visualization showing service health.
 * Each rectangle represents a service, with size based on importance
 * and color based on health status.
 * 
 * For beginners: A TreeMap is like a grid of rectangles where:
 * - Bigger rectangles = more important services
 * - Green rectangles = healthy services
 * - Red rectangles = unhealthy services
 * - Yellow rectangles = degraded services
 * 
 * Component: TreeMapChart
 * Author: Engineering Log Intelligence Team
 * Date: September 29, 2025
 */

import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'

// Define props
const props = defineProps({
  data: {
    type: Array,
    required: true,
    default: () => []
  },
  height: {
    type: Number,
    default: 300
  },
  options: {
    type: Object,
    default: () => ({})
  }
})
// Reactive references for template
const chartContainer = ref(null)
let resizeObserver = null

// Service health data
const servicesData = ref([
  {
    name: 'PostgreSQL Database',
    status: 'healthy',
    importance: 100,
    responseTime: 15,
    uptime: 99.9,
    description: 'Primary database for structured data storage'
  },
  {
    name: 'Elasticsearch Cluster',
    status: 'healthy',
    importance: 95,
    responseTime: 45,
    uptime: 99.8,
    description: 'Search engine for log analysis and queries'
  },
  {
    name: 'Kafka Streaming',
    status: 'degraded',
    importance: 90,
    responseTime: 120,
    uptime: 98.5,
    description: 'Real-time message streaming platform'
  },
  {
    name: 'Vercel Functions',
    status: 'healthy',
    importance: 85,
    responseTime: 89,
    uptime: 99.9,
    description: 'Serverless API functions'
  },
  {
    name: 'Vue.js Frontend',
    status: 'healthy',
    importance: 80,
    responseTime: 65,
    uptime: 99.7,
    description: 'User interface and dashboard'
  },
  {
    name: 'ML Models',
    status: 'healthy',
    importance: 75,
    responseTime: 150,
    uptime: 99.5,
    description: 'Machine learning inference engine'
  },
  {
    name: 'Monitoring System',
    status: 'warning',
    importance: 70,
    responseTime: 200,
    uptime: 97.2,
    description: 'System health monitoring and alerting'
  },
  {
    name: 'Authentication',
    status: 'healthy',
    importance: 65,
    responseTime: 25,
    uptime: 99.8,
    description: 'JWT authentication and authorization'
  }
])

// Color mapping for service status
const getStatusColor = (status) => {
  switch (status) {
    case 'healthy': return '#10b981' // Green
    case 'warning': return '#f59e0b' // Yellow
    case 'degraded': return '#f97316' // Orange
    case 'unhealthy': return '#ef4444' // Red
    default: return '#6b7280' // Gray
  }
}

// Create TreeMap visualization
const createTreeMap = () => {
  if (!chartContainer.value) return

  // Clear existing content
  chartContainer.value.innerHTML = ''

  // Calculate total area
  const totalImportance = servicesData.value.reduce((sum, service) => sum + service.importance, 0)
  const containerWidth = chartContainer.value.clientWidth
  const containerHeight = props.height

  // Create SVG element
  const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg')
  svg.setAttribute('width', '100%')
  svg.setAttribute('height', '100%')
  svg.setAttribute('viewBox', `0 0 ${containerWidth} ${containerHeight}`)
  svg.style.overflow = 'visible'

  // Calculate grid layout (simple grid approach) - leave space for legend
  const legendWidth = 120
  const availableWidth = containerWidth - legendWidth - 20 // 20px margin
  const cols = Math.ceil(Math.sqrt(servicesData.value.length))
  const rows = Math.ceil(servicesData.value.length / cols)
  const cellWidth = availableWidth / cols
  const cellHeight = containerHeight / rows

  // Sort services by importance (largest first)
  const sortedServices = [...servicesData.value].sort((a, b) => b.importance - a.importance)

  // Create rectangles for each service
  sortedServices.forEach((service, index) => {
    const col = index % cols
    const row = Math.floor(index / cols)
    
    // Calculate position and size based on importance
    const importanceRatio = service.importance / 100
    const width = cellWidth * (0.7 + importanceRatio * 0.3)
    const height = cellHeight * (0.7 + importanceRatio * 0.3)
    const x = col * cellWidth + (cellWidth - width) / 2
    const y = row * cellHeight + (cellHeight - height) / 2

    // Create rectangle
    const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect')
    rect.setAttribute('x', x)
    rect.setAttribute('y', y)
    rect.setAttribute('width', width)
    rect.setAttribute('height', height)
    rect.setAttribute('rx', 4)
    rect.setAttribute('ry', 4)
    rect.setAttribute('fill', getStatusColor(service.status))
    rect.setAttribute('stroke', '#ffffff')
    rect.setAttribute('stroke-width', 2)
    rect.setAttribute('opacity', 0.8)
    
    // Add hover effect
    rect.addEventListener('mouseenter', () => {
      rect.setAttribute('opacity', 1)
      rect.setAttribute('stroke-width', 3)
    })
    
    rect.addEventListener('mouseleave', () => {
      rect.setAttribute('opacity', 0.8)
      rect.setAttribute('stroke-width', 2)
    })

    // Create text label
    const text = document.createElementNS('http://www.w3.org/2000/svg', 'text')
    text.setAttribute('x', x + width / 2)
    text.setAttribute('y', y + height / 2 - 8)
    text.setAttribute('text-anchor', 'middle')
    text.setAttribute('fill', '#ffffff')
    text.setAttribute('font-size', Math.min(12, width / 8))
    text.setAttribute('font-weight', 'bold')
    text.setAttribute('font-family', 'system-ui, -apple-system, sans-serif')
    text.textContent = service.name.split(' ')[0] // First word only

    // Create status indicator
    const statusCircle = document.createElementNS('http://www.w3.org/2000/svg', 'circle')
    statusCircle.setAttribute('cx', x + width - 8)
    statusCircle.setAttribute('cy', y + 8)
    statusCircle.setAttribute('r', 4)
    statusCircle.setAttribute('fill', getStatusColor(service.status))
    statusCircle.setAttribute('stroke', '#ffffff')
    statusCircle.setAttribute('stroke-width', 1)

    // Create tooltip
    const tooltip = document.createElementNS('http://www.w3.org/2000/svg', 'title')
    tooltip.textContent = `${service.name}\nStatus: ${service.status}\nResponse Time: ${service.responseTime}ms\nUptime: ${service.uptime}%\n${service.description}`

    // Add elements to SVG
    rect.appendChild(tooltip)
    svg.appendChild(rect)
    svg.appendChild(text)
    svg.appendChild(statusCircle)
  })

  // Add legend to the right side
  const legend = createLegend(availableWidth + 20, 20)
  svg.appendChild(legend)

  chartContainer.value.appendChild(svg)
}

// Create legend
const createLegend = (x, y) => {
  const legendGroup = document.createElementNS('http://www.w3.org/2000/svg', 'g')
  legendGroup.setAttribute('transform', `translate(${x}, ${y})`)

  const statuses = [
    { status: 'healthy', label: 'Healthy' },
    { status: 'warning', label: 'Warning' },
    { status: 'degraded', label: 'Degraded' },
    { status: 'unhealthy', label: 'Unhealthy' }
  ]

  statuses.forEach((item, index) => {
    // Legend circle
    const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle')
    circle.setAttribute('cx', 0)
    circle.setAttribute('cy', index * 20)
    circle.setAttribute('r', 6)
    circle.setAttribute('fill', getStatusColor(item.status))
    circle.setAttribute('stroke', '#ffffff')
    circle.setAttribute('stroke-width', 1)

    // Legend text
    const text = document.createElementNS('http://www.w3.org/2000/svg', 'text')
    text.setAttribute('x', 15)
    text.setAttribute('y', index * 20 + 4)
    text.setAttribute('fill', '#374151')
    text.setAttribute('font-size', '12')
    text.setAttribute('font-family', 'system-ui, -apple-system, sans-serif')
    text.textContent = item.label

    legendGroup.appendChild(circle)
    legendGroup.appendChild(text)
  })

  return legendGroup
}

// Handle resize
const handleResize = () => {
  nextTick(() => {
    createTreeMap()
  })
}

// Watch for data changes
watch(() => props.data, () => {
  if (props.data && props.data.length > 0) {
    servicesData.value = props.data
  }
  createTreeMap()
}, { deep: true })

// Lifecycle
onMounted(() => {
  createTreeMap()
  
  // Set up resize observer
  if (window.ResizeObserver) {
    resizeObserver = new ResizeObserver(handleResize)
    resizeObserver.observe(chartContainer.value)
  }
  
  // Fallback resize listener
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  if (resizeObserver) {
    resizeObserver.disconnect()
  }
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.treemap-chart {
  width: 100%;
  height: 100%;
}

.treemap-chart svg {
  display: block;
}

/* Hover effects */
.treemap-chart rect:hover {
  cursor: pointer;
  filter: brightness(1.1);
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .treemap-chart {
    height: 250px;
  }
}
</style>
