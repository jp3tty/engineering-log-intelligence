<template>
  <div class="treemap-chart">
    <!-- Main Chart Area -->
    <div class="treemap-container">
      <div ref="chartContainer" class="chart-area">
      </div>
    </div>

    <!-- Service Details Panel -->
    <div v-if="selectedService" class="service-details-panel">
      <div class="panel-header">
        <h3>{{ selectedService.name }}</h3>
        <button @click="closeServiceDetails" class="close-button">×</button>
      </div>
      <div class="panel-content">
        <div class="service-details">
          <div class="detail-item">
            <span class="label">Status:</span>
            <span :class="['status', selectedService.status]">{{ selectedService.status }}</span>
          </div>
          <div class="detail-item">
            <span class="label">Importance:</span>
            <span class="value">{{ selectedService.importance }}%</span>
          </div>
          <div class="detail-item">
            <span class="label">Response Time:</span>
            <span class="value">{{ selectedService.responseTime }}ms</span>
          </div>
          <div class="detail-item">
            <span class="label">Uptime:</span>
            <span class="value">{{ selectedService.uptime }}%</span>
          </div>
          <div class="detail-item">
            <span class="label">Description:</span>
            <span class="value">{{ selectedService.description }}</span>
          </div>
          <div v-if="selectedService.children && selectedService.children.length > 0" class="sub-services">
            <span class="label">Sub-Services:</span>
            <div class="sub-service-list">
              <div 
                v-for="child in selectedService.children" 
                :key="child.name"
                class="sub-service-item"
              >
                <span :class="['status-indicator', child.status]"></span>
                <span class="sub-service-name">{{ child.name }}</span>
                <span class="sub-service-importance">{{ child.importance }}%</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
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
const selectedService = ref(null)
let resizeObserver = null

// Hierarchical service health data with drill-down capability
const servicesData = ref([
  {
    name: 'Database Services',
    status: 'healthy',
    importance: 100,
    responseTime: 15,
    uptime: 99.9,
    description: 'Core database infrastructure and data storage systems',
    children: [
      {
        name: 'PostgreSQL Primary',
        status: 'healthy',
        importance: 90,
        responseTime: 12,
        uptime: 99.9,
        description: 'Primary database for structured data storage',
        children: [
          {
            name: 'Connection Pool',
            status: 'healthy',
            importance: 85,
            responseTime: 5,
            uptime: 99.8,
            description: 'Database connection management'
          },
          {
            name: 'Query Processor',
            status: 'warning',
            importance: 80,
            responseTime: 25,
            uptime: 98.5,
            description: 'SQL query execution engine'
          },
          {
            name: 'Storage Engine',
            status: 'healthy',
            importance: 75,
            responseTime: 8,
            uptime: 99.9,
            description: 'Data persistence layer'
          }
        ]
      },
      {
        name: 'PostgreSQL Replica',
        status: 'healthy',
        importance: 70,
        responseTime: 18,
        uptime: 99.7,
        description: 'Read-only replica for load balancing',
        children: [
          {
            name: 'Replication Process',
            status: 'healthy',
            importance: 65,
            responseTime: 10,
            uptime: 99.5,
            description: 'Data synchronization from primary'
          }
        ]
      },
      {
        name: 'Redis Cache',
        status: 'healthy',
        importance: 60,
        responseTime: 2,
        uptime: 99.8,
        description: 'In-memory caching layer'
      }
    ]
  },
  {
    name: 'API Services',
    status: 'healthy',
    importance: 95,
    responseTime: 45,
    uptime: 99.8,
    description: 'RESTful API endpoints and microservices',
    children: [
      {
        name: 'Authentication API',
        status: 'healthy',
        importance: 90,
        responseTime: 25,
        uptime: 99.8,
        description: 'JWT authentication and authorization',
        children: [
          {
            name: 'Token Validator',
            status: 'healthy',
            importance: 85,
            responseTime: 5,
            uptime: 99.9,
            description: 'JWT token validation service'
          },
          {
            name: 'User Manager',
            status: 'healthy',
            importance: 80,
            responseTime: 15,
            uptime: 99.7,
            description: 'User account management'
          }
        ]
      },
      {
        name: 'Analytics API',
        status: 'healthy',
        importance: 85,
        responseTime: 120,
        uptime: 99.5,
        description: 'Data analytics and reporting endpoints',
        children: [
          {
            name: 'Query Engine',
            status: 'healthy',
            importance: 80,
            responseTime: 100,
            uptime: 99.4,
            description: 'Analytics query processing'
          },
          {
            name: 'Report Generator',
            status: 'warning',
            importance: 75,
            responseTime: 200,
            uptime: 98.8,
            description: 'Automated report generation'
          }
        ]
      },
      {
        name: 'Log Processing API',
        status: 'degraded',
        importance: 80,
        responseTime: 150,
        uptime: 98.5,
        description: 'Log ingestion and processing endpoints'
      }
    ]
  },
  {
    name: 'Frontend Services',
    status: 'healthy',
    importance: 75,
    responseTime: 65,
    uptime: 99.7,
    description: 'User interface and client-side applications',
    children: [
      {
        name: 'Web Application',
        status: 'healthy',
        importance: 70,
        responseTime: 50,
        uptime: 99.6,
        description: 'Main Vue.js dashboard application'
      },
      {
        name: 'Admin Dashboard',
        status: 'healthy',
        importance: 60,
        responseTime: 45,
        uptime: 99.5,
        description: 'Administrative interface'
      }
    ]
  },
  {
    name: 'Infrastructure Services',
    status: 'warning',
    importance: 70,
    responseTime: 200,
    uptime: 97.2,
    description: 'Core infrastructure and monitoring systems',
    children: [
      {
        name: 'Elasticsearch Cluster',
        status: 'healthy',
        importance: 85,
        responseTime: 45,
        uptime: 99.8,
        description: 'Search engine for log analysis and queries'
      },
      {
        name: 'Kafka Streaming',
        status: 'degraded',
        importance: 80,
        responseTime: 120,
        uptime: 98.5,
        description: 'Real-time message streaming platform'
      },
      {
        name: 'Monitoring System',
        status: 'warning',
        importance: 75,
        responseTime: 200,
        uptime: 97.2,
        description: 'System health monitoring and alerting'
      }
    ]
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

// Service selection functionality
const selectService = (service) => {
  selectedService.value = service
}

const closeServiceDetails = () => {
  selectedService.value = null
}

// Create TreeMap visualization
const createTreeMap = () => {
  if (!chartContainer.value) return

  // Clear existing content
  chartContainer.value.innerHTML = ''

  // Use props data for display, fallback to servicesData if no props data
  // Fixed: Now properly uses props.data instead of hardcoded servicesData
  const displayData = props.data && props.data.length > 0 ? props.data : servicesData.value
  if (!displayData || displayData.length === 0) return

  // Calculate total area
  const totalImportance = displayData.reduce((sum, service) => sum + service.importance, 0)
  const containerWidth = chartContainer.value.clientWidth
  const containerHeight = props.height

  // Create SVG element
  const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg')
  svg.setAttribute('width', '100%')
  svg.setAttribute('height', '100%')
  svg.setAttribute('viewBox', `0 0 ${containerWidth} ${containerHeight}`)
  svg.style.overflow = 'visible'

  // Calculate grid layout (simple grid approach)
  const cols = Math.ceil(Math.sqrt(displayData.length))
  const rows = Math.ceil(displayData.length / cols)
  const cellWidth = containerWidth / cols
  const cellHeight = containerHeight / rows

  // Sort services by importance (largest first)
  const sortedServices = [...displayData].sort((a, b) => b.importance - a.importance)

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
    
    // Add visual indicator for services with sub-services
    if (service.children && service.children.length > 0) {
      rect.setAttribute('stroke-dasharray', '3,3')
      rect.setAttribute('stroke-width', 3)
    }
    
    // Add hover effect
    rect.addEventListener('mouseenter', () => {
      rect.setAttribute('opacity', 1)
      rect.setAttribute('stroke-width', service.children && service.children.length > 0 ? 4 : 3)
    })
    
    rect.addEventListener('mouseleave', () => {
      rect.setAttribute('opacity', 0.8)
      rect.setAttribute('stroke-width', service.children && service.children.length > 0 ? 3 : 2)
    })

    // Add click handler for service selection
    rect.addEventListener('click', () => {
      selectService(service)
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

    // Create drill-down indicator (arrow) if service has children
    if (service.children && service.children.length > 0) {
      const drillDownArrow = document.createElementNS('http://www.w3.org/2000/svg', 'polygon')
      const arrowSize = 6
      const arrowX = x + width - 20
      const arrowY = y + height - 15
      
      drillDownArrow.setAttribute('points', 
        `${arrowX},${arrowY} ${arrowX + arrowSize},${arrowY + arrowSize/2} ${arrowX},${arrowY + arrowSize}`
      )
      drillDownArrow.setAttribute('fill', '#ffffff')
      drillDownArrow.setAttribute('opacity', 0.8)
      svg.appendChild(drillDownArrow)
    }

    // Create tooltip
    const tooltip = document.createElementNS('http://www.w3.org/2000/svg', 'title')
    const drillDownText = service.children && service.children.length > 0 ? '\nClick to drill down' : ''
    tooltip.textContent = `${service.name}\nStatus: ${service.status}\nResponse Time: ${service.responseTime}ms\nUptime: ${service.uptime}%\n${service.description}${drillDownText}`

    // Add elements to SVG
    rect.appendChild(tooltip)
    svg.appendChild(rect)
    svg.appendChild(text)
    svg.appendChild(statusCircle)
  })

  chartContainer.value.appendChild(svg)
}


// Handle resize
const handleResize = () => {
  nextTick(() => {
    createTreeMap()
  })
}

// Watch for data changes
watch(() => props.data, () => {
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
  position: relative;
}


.treemap-container {
  width: 100%;
  height: 100%;
}

.chart-area {
  width: 100%;
  height: 100%;
  position: relative;
}

.floating-back-button {
  position: absolute;
  top: 16px;
  left: 16px;
  background: rgba(59, 130, 246, 0.9);
  color: white;
  border: none;
  border-radius: 8px;
  padding: 8px 16px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 100;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 6px;
}

.floating-back-button:hover {
  background: rgba(37, 99, 235, 0.95);
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
}


.treemap-chart svg {
  display: block;
  width: 100%;
  height: 100%;
}


/* Drill-down Info Panel */
.service-details-panel {
  position: absolute;
  top: 80px;
  right: 20px;
  width: 320px;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
  z-index: 1000;
  max-height: 400px;
  overflow-y: auto;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid #e5e7eb;
  background: #f8f9fa;
  border-radius: 8px 8px 0 0;
}

.panel-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #374151;
}

.close-button {
  background: none;
  border: none;
  font-size: 20px;
  color: #6b7280;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.close-button:hover {
  background: #e5e7eb;
}

.panel-content {
  padding: 16px;
}

.service-details {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
}

.detail-item .label {
  font-weight: 600;
  color: #374151;
  font-size: 14px;
  min-width: 100px;
}

.detail-item .value {
  color: #6b7280;
  font-size: 14px;
  text-align: right;
  flex: 1;
}

.status {
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  text-transform: capitalize;
}

.status.healthy {
  background: #dcfce7;
  color: #166534;
}

.status.warning {
  background: #fef3c7;
  color: #92400e;
}

.status.degraded {
  background: #fed7aa;
  color: #c2410c;
}

.status.unhealthy {
  background: #fecaca;
  color: #dc2626;
}

.sub-services {
  margin-top: 8px;
}

.sub-service-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: 8px;
}

.sub-service-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px;
  background: #f8f9fa;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.sub-service-item:hover {
  background: #e5e7eb;
}

.status-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.status-indicator.healthy {
  background: #10b981;
}

.status-indicator.warning {
  background: #f59e0b;
}

.status-indicator.degraded {
  background: #f97316;
}

.status-indicator.unhealthy {
  background: #ef4444;
}

.sub-service-name {
  flex: 1;
  font-size: 14px;
  color: #374151;
  font-weight: 500;
}

.sub-service-importance {
  font-size: 12px;
  color: #6b7280;
  font-weight: 600;
}

/* Hover effects */
.treemap-chart rect:hover {
  cursor: pointer;
  filter: brightness(1.1);
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .treemap-header {
    flex-direction: column;
    gap: 8px;
    align-items: flex-start;
  }
  
  .breadcrumb-container {
    width: 100%;
  }
  
  .breadcrumb-trail {
    flex-wrap: wrap;
  }
  
  .treemap-container {
    flex-direction: column;
    gap: 16px;
    height: calc(100% - 100px);
  }
  
  .legend-area {
    flex: none;
    width: 100%;
    padding: 16px 0;
  }
  
  .legend {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
  }
  
  .legend-item {
    margin-bottom: 0;
  }
  
  .treemap-chart {
    height: 250px;
  }
  
  .service-details-panel {
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 90%;
    max-width: 400px;
    max-height: 80vh;
  }
}
</style>
