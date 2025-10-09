<template>
  <div class="dashboard-builder min-h-screen bg-gray-50">
    <!-- Header -->
    <div class="bg-white shadow-sm border-b">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center py-4">
          <div class="flex items-center space-x-4">
            <h1 class="text-2xl font-bold text-gray-900">Dashboard Builder</h1>
            <div class="flex items-center space-x-2">
              <span class="text-sm text-gray-500">Template:</span>
              <select 
                v-model="selectedTemplate" 
                @change="loadTemplate"
                class="border border-gray-300 rounded-md px-3 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Custom</option>
                <option value="system-overview">System Overview</option>
                <option value="incident-management">Incident Management</option>
                <option value="performance-monitoring">Performance Monitoring</option>
                <option value="security-dashboard">Security Dashboard</option>
              </select>
            </div>
          </div>
          <div class="flex items-center space-x-3">
            <button
              @click="previewMode = !previewMode"
              :class="[
                'px-4 py-2 rounded-md text-sm font-medium transition-colors',
                previewMode 
                  ? 'bg-blue-600 text-white' 
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              ]"
            >
              {{ previewMode ? 'Edit Mode' : 'Preview Mode' }}
            </button>
            <button
              @click="saveDashboard"
              class="px-4 py-2 bg-green-600 text-white rounded-md text-sm font-medium hover:bg-green-700 transition-colors"
            >
              Save Dashboard
            </button>
            <button
              @click="exportDashboard"
              class="px-4 py-2 bg-purple-600 text-white rounded-md text-sm font-medium hover:bg-purple-700 transition-colors"
            >
              Export
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="flex h-screen">
      <!-- Widget Library Sidebar -->
      <div v-if="!previewMode" class="w-80 bg-white shadow-lg border-r overflow-y-auto">
        <WidgetLibrary @add-widget="addWidget" />
      </div>

      <!-- Dashboard Canvas -->
      <div class="flex-1 overflow-auto">
        <DashboardCanvas
          :widgets="dashboard.widgets"
          :preview-mode="previewMode"
          @update-widget="updateWidget"
          @remove-widget="removeWidget"
          @reorder-widgets="reorderWidgets"
          @load-template="loadTemplate"
          @select-widget="selectWidget"
        />
      </div>

      <!-- Widget Editor Sidebar -->
      <div v-if="!previewMode && selectedWidget" class="w-80 bg-white shadow-lg border-l overflow-y-auto">
        <WidgetEditor
          :widget="selectedWidget"
          @update-widget="updateWidget"
          @close-editor="selectedWidget = null"
        />
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { useDashboardStore } from '@/stores/dashboard'
import WidgetLibrary from './WidgetLibrary.vue'
import DashboardCanvas from './DashboardCanvas.vue'
import WidgetEditor from './WidgetEditor.vue'

export default {
  name: 'DashboardBuilder',
  components: {
    WidgetLibrary,
    DashboardCanvas,
    WidgetEditor
  },
  setup() {
    const dashboardStore = useDashboardStore()
    
    // Reactive state
    const previewMode = ref(false)
    const selectedTemplate = ref('')
    const selectedWidget = ref(null)
    
    const dashboard = reactive({
      id: null,
      name: 'My Dashboard',
      widgets: [],
      layout: 'grid',
      settings: {
        gridSize: 12,
        gutter: 16,
        breakpoints: {
          xs: 480,
          sm: 768,
          md: 1024,
          lg: 1280,
          xl: 1536
        }
      }
    })

    // Methods
    const addWidget = (widgetType) => {
      const newWidget = {
        id: `widget-${Date.now()}`,
        type: widgetType,
        title: `${widgetType} Widget`,
        position: { x: 0, y: 0 },
        size: { width: 4, height: 3 },
        config: getDefaultWidgetConfig(widgetType),
        data: null,
        lastUpdated: new Date()
      }
      
      dashboard.widgets.push(newWidget)
      selectedWidget.value = newWidget
    }

    const updateWidget = (widgetId, updates) => {
      const index = dashboard.widgets.findIndex(w => w.id === widgetId)
      if (index !== -1) {
        // Update existing widget
        Object.assign(dashboard.widgets[index], updates)
        dashboard.widgets[index].lastUpdated = new Date()
      } else {
        // Add new widget if it doesn't exist
        dashboard.widgets.push({
          ...updates,
          id: widgetId,
          lastUpdated: new Date()
        })
      }
    }

    const selectWidget = (widget) => {
      selectedWidget.value = widget
    }

    const removeWidget = (widgetId) => {
      const index = dashboard.widgets.findIndex(w => w.id === widgetId)
      if (index !== -1) {
        dashboard.widgets.splice(index, 1)
        if (selectedWidget.value?.id === widgetId) {
          selectedWidget.value = null
        }
      }
    }

    const reorderWidgets = (newOrder) => {
      dashboard.widgets = newOrder
    }

    const loadTemplate = (templateName) => {
      // If called with a parameter, use it; otherwise use selectedTemplate.value
      const templateToLoad = templateName || selectedTemplate.value
      if (!templateToLoad) return
      
      const templates = {
        'system-overview': {
          widgets: [
            { type: 'metric', title: 'System Health', size: { width: 3, height: 2 } },
            { type: 'chart', title: 'CPU Usage', size: { width: 6, height: 4 } },
            { type: 'chart', title: 'Memory Usage', size: { width: 3, height: 4 } },
            { type: 'alert', title: 'Active Alerts', size: { width: 12, height: 3 } }
          ]
        },
        'incident-management': {
          widgets: [
            { type: 'alert', title: 'Critical Incidents', size: { width: 6, height: 4 } },
            { type: 'chart', title: 'Incident Timeline', size: { width: 6, height: 4 } },
            { type: 'metric', title: 'MTTR', size: { width: 3, height: 2 } },
            { type: 'metric', title: 'MTBF', size: { width: 3, height: 2 } },
            { type: 'log', title: 'Recent Logs', size: { width: 6, height: 4 } }
          ]
        },
        'performance-monitoring': {
          widgets: [
            { type: 'chart', title: 'Response Time', size: { width: 6, height: 4 } },
            { type: 'chart', title: 'Throughput', size: { width: 6, height: 4 } },
            { type: 'metric', title: 'Error Rate', size: { width: 3, height: 2 } },
            { type: 'metric', title: 'Uptime', size: { width: 3, height: 2 } },
            { type: 'heatmap', title: 'Performance Heatmap', size: { width: 12, height: 4 } }
          ]
        },
        'security-dashboard': {
          widgets: [
            { type: 'alert', title: 'Security Alerts', size: { width: 6, height: 4 } },
            { type: 'chart', title: 'Threat Detection', size: { width: 6, height: 4 } },
            { type: 'metric', title: 'Failed Logins', size: { width: 3, height: 2 } },
            { type: 'metric', title: 'Blocked IPs', size: { width: 3, height: 2 } },
            { type: 'log', title: 'Security Logs', size: { width: 12, height: 4 } }
          ]
        }
      }
      
      const template = templates[templateToLoad]
      if (template) {
        // Update selectedTemplate if called with parameter
        if (templateName) {
          selectedTemplate.value = templateName
        }
        // Calculate positions to avoid overlap
        let currentX = 0
        let currentY = 0
        const maxWidth = 12 // Grid width
        const cellSize = 20 // Grid cell size
        
        dashboard.widgets = template.widgets.map((widget, index) => {
          // Calculate position based on widget size and previous widgets
          const position = { x: currentX, y: currentY }
          
          // Move to next position
          currentX += widget.size.width
          if (currentX >= maxWidth) {
            currentX = 0
            currentY += Math.max(...template.widgets.slice(0, index + 1).map(w => w.size.height))
          }
          
          return {
            id: `widget-${Date.now()}-${index}`,
            type: widget.type,
            title: widget.title,
            position: position,
            size: widget.size,
            config: getDefaultWidgetConfig(widget.type),
            data: null,
            lastUpdated: new Date()
          }
        })
      }
    }

    const getDefaultWidgetConfig = (type) => {
      const configs = {
        metric: {
          value: 0,
          unit: '',
          trend: 'neutral',
          color: 'blue'
        },
        chart: {
          chartType: 'line',
          dataSource: 'system_metrics',
          timeRange: '1h',
          refreshInterval: 30
        },
        alert: {
          severity: 'all',
          limit: 10,
          autoRefresh: true
        },
        log: {
          logLevel: 'all',
          limit: 50,
          autoRefresh: true
        },
        heatmap: {
          dataSource: 'performance_metrics',
          timeRange: '24h',
          refreshInterval: 60
        }
      }
      return configs[type] || {}
    }

    const saveDashboard = () => {
      dashboardStore.saveDashboard(dashboard)
      // Show success notification
      console.log('Dashboard saved successfully!')
    }

    const exportDashboard = () => {
      const dataStr = JSON.stringify(dashboard, null, 2)
      const dataBlob = new Blob([dataStr], { type: 'application/json' })
      const url = URL.createObjectURL(dataBlob)
      const link = document.createElement('a')
      link.href = url
      link.download = `${dashboard.name.replace(/\s+/g, '_').toLowerCase()}.json`
      link.click()
      URL.revokeObjectURL(url)
    }

    // Lifecycle
    onMounted(() => {
      dashboardStore.loadDashboard()
    })

    return {
      previewMode,
      selectedTemplate,
      selectedWidget,
      dashboard,
      addWidget,
      updateWidget,
      selectWidget,
      removeWidget,
      reorderWidgets,
      loadTemplate,
      saveDashboard,
      exportDashboard
    }
  }
}
</script>

<style scoped>
.dashboard-builder {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}
</style>
