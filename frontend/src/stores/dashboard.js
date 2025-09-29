import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useDashboardStore = defineStore('dashboard', () => {
  // State
  const dashboards = ref([])
  const currentDashboard = ref(null)
  const selectedWidget = ref(null)
  const isEditing = ref(false)
  const previewMode = ref(false)
  
  // Widget templates
  const widgetTemplates = ref({
    'metric': {
      type: 'metric',
      name: 'Metric Card',
      description: 'Display a single metric with trend indicator',
      icon: '📊',
      defaultSize: { width: 3, height: 2 },
      defaultConfig: {
        value: 0,
        unit: '',
        trend: 'neutral',
        color: 'blue'
      }
    },
    'line-chart': {
      type: 'line-chart',
      name: 'Line Chart',
      description: 'Time series data visualization',
      icon: '📈',
      defaultSize: { width: 6, height: 4 },
      defaultConfig: {
        chartType: 'line',
        dataSource: 'system_metrics',
        timeRange: '1h',
        refreshInterval: 30
      }
    },
    'bar-chart': {
      type: 'bar-chart',
      name: 'Bar Chart',
      description: 'Comparative data visualization',
      icon: '📊',
      defaultSize: { width: 6, height: 4 },
      defaultConfig: {
        chartType: 'bar',
        dataSource: 'application_logs',
        timeRange: '24h',
        refreshInterval: 60
      }
    },
    'pie-chart': {
      type: 'pie-chart',
      name: 'Pie Chart',
      description: 'Proportional data visualization',
      icon: '🥧',
      defaultSize: { width: 4, height: 4 },
      defaultConfig: {
        chartType: 'pie',
        dataSource: 'performance_data',
        timeRange: '6h',
        refreshInterval: 120
      }
    },
    'alert-list': {
      type: 'alert-list',
      name: 'Alert List',
      description: 'List of active alerts and incidents',
      icon: '🚨',
      defaultSize: { width: 6, height: 4 },
      defaultConfig: {
        severity: 'all',
        limit: 10,
        autoRefresh: true,
        refreshInterval: 30
      }
    },
    'log-viewer': {
      type: 'log-viewer',
      name: 'Log Viewer',
      description: 'Real-time log stream viewer',
      icon: '📝',
      defaultSize: { width: 8, height: 6 },
      defaultConfig: {
        logLevel: 'all',
        limit: 50,
        autoRefresh: true,
        refreshInterval: 15
      }
    }
  })

  // Dashboard templates
  const dashboardTemplates = ref({
    'system-overview': {
      name: 'System Overview',
      description: 'High-level system health and performance metrics',
      widgets: [
        {
          type: 'metric',
          title: 'System Health',
          position: { x: 1, y: 1 },
          size: { width: 3, height: 2 },
          config: { value: 95, unit: '%', trend: 'up', color: 'green' }
        },
        {
          type: 'line-chart',
          title: 'CPU Usage',
          position: { x: 5, y: 1 },
          size: { width: 6, height: 4 },
          config: { chartType: 'line', dataSource: 'cpu_usage', timeRange: '1h' }
        },
        {
          type: 'line-chart',
          title: 'Memory Usage',
          position: { x: 1, y: 4 },
          size: { width: 6, height: 4 },
          config: { chartType: 'line', dataSource: 'memory_usage', timeRange: '1h' }
        },
        {
          type: 'alert-list',
          title: 'Active Alerts',
          position: { x: 8, y: 1 },
          size: { width: 3, height: 4 },
          config: { severity: 'high', limit: 5 }
        },
        {
          type: 'metric',
          title: 'Response Time',
          position: { x: 8, y: 6 },
          size: { width: 3, height: 2 },
          config: { value: 150, unit: 'ms', trend: 'down', color: 'blue' }
        }
      ]
    },
    'incident-management': {
      name: 'Incident Management',
      description: 'Alert and incident management dashboard',
      widgets: [
        {
          type: 'alert-list',
          title: 'Critical Incidents',
          position: { x: 1, y: 1 },
          size: { width: 6, height: 4 },
          config: { severity: 'critical', limit: 10 }
        },
        {
          type: 'line-chart',
          title: 'Incident Timeline',
          position: { x: 8, y: 1 },
          size: { width: 6, height: 4 },
          config: { chartType: 'line', dataSource: 'incidents', timeRange: '24h' }
        },
        {
          type: 'metric',
          title: 'MTTR',
          position: { x: 1, y: 6 },
          size: { width: 3, height: 2 },
          config: { value: 45, unit: 'min', trend: 'down', color: 'green' }
        },
        {
          type: 'metric',
          title: 'MTBF',
          position: { x: 5, y: 6 },
          size: { width: 3, height: 2 },
          config: { value: 720, unit: 'hrs', trend: 'up', color: 'blue' }
        },
        {
          type: 'log-viewer',
          title: 'Recent Logs',
          position: { x: 9, y: 6 },
          size: { width: 5, height: 4 },
          config: { logLevel: 'error', limit: 20 }
        }
      ]
    },
    'performance-monitoring': {
      name: 'Performance Monitoring',
      description: 'System performance and metrics monitoring',
      widgets: [
        {
          type: 'line-chart',
          title: 'Response Time',
          position: { x: 1, y: 1 },
          size: { width: 6, height: 4 },
          config: { chartType: 'line', dataSource: 'response_time', timeRange: '1h' }
        },
        {
          type: 'line-chart',
          title: 'Throughput',
          position: { x: 8, y: 1 },
          size: { width: 6, height: 4 },
          config: { chartType: 'line', dataSource: 'throughput', timeRange: '1h' }
        },
        {
          type: 'metric',
          title: 'Error Rate',
          position: { x: 1, y: 6 },
          size: { width: 3, height: 2 },
          config: { value: 0.2, unit: '%', trend: 'down', color: 'green' }
        },
        {
          type: 'metric',
          title: 'Uptime',
          position: { x: 5, y: 6 },
          size: { width: 3, height: 2 },
          config: { value: 99.9, unit: '%', trend: 'up', color: 'green' }
        },
        {
          type: 'bar-chart',
          title: 'Performance Heatmap',
          position: { x: 9, y: 6 },
          size: { width: 5, height: 4 },
          config: { chartType: 'bar', dataSource: 'performance_metrics', timeRange: '24h' }
        }
      ]
    }
  })

  // Computed properties
  const currentWidgets = computed(() => {
    return currentDashboard.value?.widgets || []
  })

  const widgetCount = computed(() => {
    return currentWidgets.value.length
  })

  const hasUnsavedChanges = computed(() => {
    return currentDashboard.value?.hasUnsavedChanges || false
  })

  // Actions
  const createDashboard = (name, description = '') => {
    const newDashboard = {
      id: `dashboard-${Date.now()}`,
      name,
      description,
      widgets: [],
      layout: 'grid',
      settings: {
        gridSize: 20,
        gutter: 16,
        breakpoints: {
          xs: 480,
          sm: 768,
          md: 1024,
          lg: 1280,
          xl: 1536
        }
      },
      createdAt: new Date(),
      updatedAt: new Date(),
      hasUnsavedChanges: false
    }
    
    dashboards.value.push(newDashboard)
    currentDashboard.value = newDashboard
    return newDashboard
  }

  const loadDashboard = (dashboardId) => {
    const dashboard = dashboards.value.find(d => d.id === dashboardId)
    if (dashboard) {
      currentDashboard.value = dashboard
      return dashboard
    }
    return null
  }

  const saveDashboard = (dashboard) => {
    const index = dashboards.value.findIndex(d => d.id === dashboard.id)
    if (index !== -1) {
      dashboards.value[index] = { ...dashboard, updatedAt: new Date(), hasUnsavedChanges: false }
    } else {
      dashboards.value.push({ ...dashboard, updatedAt: new Date(), hasUnsavedChanges: false })
    }
    currentDashboard.value = dashboards.value[index] || dashboards.value[dashboards.value.length - 1]
  }

  const deleteDashboard = (dashboardId) => {
    const index = dashboards.value.findIndex(d => d.id === dashboardId)
    if (index !== -1) {
      dashboards.value.splice(index, 1)
      if (currentDashboard.value?.id === dashboardId) {
        currentDashboard.value = dashboards.value[0] || null
      }
    }
  }

  const addWidget = (widgetType, position = { x: 0, y: 0 }) => {
    if (!currentDashboard.value) return null
    
    const template = widgetTemplates.value[widgetType]
    if (!template) return null
    
    const newWidget = {
      id: `widget-${Date.now()}`,
      type: widgetType,
      title: template.name,
      position,
      size: template.defaultSize,
      config: { ...template.defaultConfig },
      data: null,
      lastUpdated: new Date()
    }
    
    currentDashboard.value.widgets.push(newWidget)
    currentDashboard.value.hasUnsavedChanges = true
    return newWidget
  }

  const updateWidget = (widgetId, updates) => {
    if (!currentDashboard.value) return false
    
    const widget = currentDashboard.value.widgets.find(w => w.id === widgetId)
    if (widget) {
      Object.assign(widget, updates)
      widget.lastUpdated = new Date()
      currentDashboard.value.hasUnsavedChanges = true
      return true
    }
    return false
  }

  const removeWidget = (widgetId) => {
    if (!currentDashboard.value) return false
    
    const index = currentDashboard.value.widgets.findIndex(w => w.id === widgetId)
    if (index !== -1) {
      currentDashboard.value.widgets.splice(index, 1)
      currentDashboard.value.hasUnsavedChanges = true
      
      if (selectedWidget.value?.id === widgetId) {
        selectedWidget.value = null
      }
      return true
    }
    return false
  }

  const reorderWidgets = (newOrder) => {
    if (!currentDashboard.value) return false
    
    currentDashboard.value.widgets = newOrder
    currentDashboard.value.hasUnsavedChanges = true
    return true
  }

  const loadTemplate = (templateName) => {
    const template = dashboardTemplates.value[templateName]
    if (!template) return false
    
    const newDashboard = createDashboard(template.name, template.description)
    
    template.widgets.forEach((widgetTemplate, index) => {
      const widget = {
        id: `widget-${Date.now()}-${index}`,
        type: widgetTemplate.type,
        title: widgetTemplate.title,
        position: widgetTemplate.position,
        size: widgetTemplate.size,
        config: { ...widgetTemplate.config },
        data: null,
        lastUpdated: new Date()
      }
      newDashboard.widgets.push(widget)
    })
    
    return newDashboard
  }

  const selectWidget = (widget) => {
    selectedWidget.value = widget
  }

  const clearSelection = () => {
    selectedWidget.value = null
  }

  const setEditing = (editing) => {
    isEditing.value = editing
  }

  const setPreviewMode = (preview) => {
    previewMode.value = preview
  }

  const exportDashboard = (dashboard) => {
    const dataStr = JSON.stringify(dashboard, null, 2)
    const dataBlob = new Blob([dataStr], { type: 'application/json' })
    const url = URL.createObjectURL(dataBlob)
    const link = document.createElement('a')
    link.href = url
    link.download = `${dashboard.name.replace(/\s+/g, '_').toLowerCase()}.json`
    link.click()
    URL.revokeObjectURL(url)
  }

  const importDashboard = (file) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader()
      reader.onload = (e) => {
        try {
          const dashboard = JSON.parse(e.target.result)
          dashboard.id = `dashboard-${Date.now()}` // Generate new ID
          dashboard.createdAt = new Date()
          dashboard.updatedAt = new Date()
          dashboard.hasUnsavedChanges = false
          
          dashboards.value.push(dashboard)
          currentDashboard.value = dashboard
          resolve(dashboard)
        } catch (error) {
          reject(error)
        }
      }
      reader.onerror = reject
      reader.readAsText(file)
    })
  }

  return {
    // State
    dashboards,
    currentDashboard,
    selectedWidget,
    isEditing,
    previewMode,
    widgetTemplates,
    dashboardTemplates,
    
    // Computed
    currentWidgets,
    widgetCount,
    hasUnsavedChanges,
    
    // Actions
    createDashboard,
    loadDashboard,
    saveDashboard,
    deleteDashboard,
    addWidget,
    updateWidget,
    removeWidget,
    reorderWidgets,
    loadTemplate,
    selectWidget,
    clearSelection,
    setEditing,
    setPreviewMode,
    exportDashboard,
    importDashboard
  }
})
