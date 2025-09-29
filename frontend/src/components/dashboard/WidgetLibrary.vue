<template>
  <div class="widget-library p-4">
    <div class="mb-6">
      <h2 class="text-lg font-semibold text-gray-900 mb-2">Widget Library</h2>
      <p class="text-sm text-gray-600">Drag widgets to the canvas to build your dashboard</p>
    </div>

    <!-- Search -->
    <div class="mb-4">
      <input
        v-model="searchQuery"
        type="text"
        placeholder="Search widgets..."
        class="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
      />
    </div>

    <!-- Widget Categories -->
    <div class="space-y-4">
      <!-- Chart Widgets -->
      <div class="widget-category">
        <h3 class="text-sm font-medium text-gray-700 mb-2 flex items-center">
          <ChartBarIcon class="w-4 h-4 mr-2" />
          Charts & Visualizations
        </h3>
        <div class="grid grid-cols-2 gap-2">
          <WidgetItem
            v-for="widget in filteredChartWidgets"
            :key="widget.type"
            :widget="widget"
            @add-widget="$emit('add-widget', widget.type)"
          />
        </div>
      </div>

      <!-- Metric Widgets -->
      <div class="widget-category">
        <h3 class="text-sm font-medium text-gray-700 mb-2 flex items-center">
          <ChartPieIcon class="w-4 h-4 mr-2" />
          Metrics & KPIs
        </h3>
        <div class="grid grid-cols-2 gap-2">
          <WidgetItem
            v-for="widget in filteredMetricWidgets"
            :key="widget.type"
            :widget="widget"
            @add-widget="$emit('add-widget', widget.type)"
          />
        </div>
      </div>

      <!-- Alert Widgets -->
      <div class="widget-category">
        <h3 class="text-sm font-medium text-gray-700 mb-2 flex items-center">
          <ExclamationTriangleIcon class="w-4 h-4 mr-2" />
          Alerts & Monitoring
        </h3>
        <div class="grid grid-cols-2 gap-2">
          <WidgetItem
            v-for="widget in filteredAlertWidgets"
            :key="widget.type"
            :widget="widget"
            @add-widget="$emit('add-widget', widget.type)"
          />
        </div>
      </div>

      <!-- Data Widgets -->
      <div class="widget-category">
        <h3 class="text-sm font-medium text-gray-700 mb-2 flex items-center">
          <DocumentTextIcon class="w-4 h-4 mr-2" />
          Data & Logs
        </h3>
        <div class="grid grid-cols-2 gap-2">
          <WidgetItem
            v-for="widget in filteredDataWidgets"
            :key="widget.type"
            :widget="widget"
            @add-widget="$emit('add-widget', widget.type)"
          />
        </div>
      </div>

      <!-- Advanced Widgets -->
      <div class="widget-category">
        <h3 class="text-sm font-medium text-gray-700 mb-2 flex items-center">
          <CogIcon class="w-4 h-4 mr-2" />
          Advanced
        </h3>
        <div class="grid grid-cols-2 gap-2">
          <WidgetItem
            v-for="widget in filteredAdvancedWidgets"
            :key="widget.type"
            :widget="widget"
            @add-widget="$emit('add-widget', widget.type)"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import {
  ChartBarIcon,
  ChartPieIcon,
  ExclamationTriangleIcon,
  DocumentTextIcon,
  CogIcon
} from '@heroicons/vue/24/outline'
import WidgetItem from './WidgetItem.vue'

export default {
  name: 'WidgetLibrary',
  components: {
    WidgetItem,
    ChartBarIcon,
    ChartPieIcon,
    ExclamationTriangleIcon,
    DocumentTextIcon,
    CogIcon
  },
  emits: ['add-widget'],
  setup() {
    const searchQuery = ref('')

    const widgetDefinitions = {
      // Chart Widgets
      'line-chart': {
        type: 'line-chart',
        name: 'Line Chart',
        description: 'Time series data visualization',
        icon: '📈',
        category: 'chart',
        defaultSize: { width: 6, height: 4 }
      },
      'bar-chart': {
        type: 'bar-chart',
        name: 'Bar Chart',
        description: 'Comparative data visualization',
        icon: '📊',
        category: 'chart',
        defaultSize: { width: 6, height: 4 }
      },
      'pie-chart': {
        type: 'pie-chart',
        name: 'Pie Chart',
        description: 'Proportional data visualization',
        icon: '🥧',
        category: 'chart',
        defaultSize: { width: 4, height: 4 }
      },
      'scatter-plot': {
        type: 'scatter-plot',
        name: 'Scatter Plot',
        description: 'Correlation data visualization',
        icon: '⚪',
        category: 'chart',
        defaultSize: { width: 6, height: 4 }
      },
      'heatmap': {
        type: 'heatmap',
        name: 'Heatmap',
        description: 'Density and intensity visualization',
        icon: '🔥',
        category: 'chart',
        defaultSize: { width: 8, height: 4 }
      },

      // Metric Widgets
      'metric': {
        type: 'metric',
        name: 'Metric Card',
        description: 'Single value with trend indicator',
        icon: '📊',
        category: 'metric',
        defaultSize: { width: 3, height: 2 }
      },
      'gauge': {
        type: 'gauge',
        name: 'Gauge',
        description: 'Circular progress indicator',
        icon: '⭕',
        category: 'metric',
        defaultSize: { width: 3, height: 3 }
      },
      'counter': {
        type: 'counter',
        name: 'Counter',
        description: 'Animated number counter',
        icon: '🔢',
        category: 'metric',
        defaultSize: { width: 3, height: 2 }
      },
      'progress-bar': {
        type: 'progress-bar',
        name: 'Progress Bar',
        description: 'Linear progress indicator',
        icon: '📊',
        category: 'metric',
        defaultSize: { width: 4, height: 2 }
      },

      // Alert Widgets
      'alert-list': {
        type: 'alert-list',
        name: 'Alert List',
        description: 'List of active alerts',
        icon: '🚨',
        category: 'alert',
        defaultSize: { width: 6, height: 4 }
      },
      'alert-summary': {
        type: 'alert-summary',
        name: 'Alert Summary',
        description: 'Alert statistics overview',
        icon: '📋',
        category: 'alert',
        defaultSize: { width: 4, height: 3 }
      },
      'incident-timeline': {
        type: 'incident-timeline',
        name: 'Incident Timeline',
        description: 'Chronological incident view',
        icon: '⏰',
        category: 'alert',
        defaultSize: { width: 8, height: 4 }
      },

      // Data Widgets
      'log-viewer': {
        type: 'log-viewer',
        name: 'Log Viewer',
        description: 'Real-time log stream',
        icon: '📝',
        category: 'data',
        defaultSize: { width: 8, height: 6 }
      },
      'data-table': {
        type: 'data-table',
        name: 'Data Table',
        description: 'Tabular data display',
        icon: '📋',
        category: 'data',
        defaultSize: { width: 8, height: 6 }
      },
      'statistics': {
        type: 'statistics',
        name: 'Statistics',
        description: 'Statistical data summary',
        icon: '📊',
        category: 'data',
        defaultSize: { width: 6, height: 4 }
      },

      // Advanced Widgets
      'custom-query': {
        type: 'custom-query',
        name: 'Custom Query',
        description: 'Custom data query widget',
        icon: '🔍',
        category: 'advanced',
        defaultSize: { width: 6, height: 4 }
      },
      'iframe': {
        type: 'iframe',
        name: 'External Content',
        description: 'Embed external content',
        icon: '🌐',
        category: 'advanced',
        defaultSize: { width: 8, height: 6 }
      },
      'markdown': {
        type: 'markdown',
        name: 'Markdown',
        description: 'Rich text content',
        icon: '📄',
        category: 'advanced',
        defaultSize: { width: 6, height: 4 }
      }
    }

    const filteredWidgets = computed(() => {
      if (!searchQuery.value) return Object.values(widgetDefinitions)
      
      return Object.values(widgetDefinitions).filter(widget =>
        widget.name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
        widget.description.toLowerCase().includes(searchQuery.value.toLowerCase())
      )
    })

    const filteredChartWidgets = computed(() => 
      filteredWidgets.value.filter(w => w.category === 'chart')
    )

    const filteredMetricWidgets = computed(() => 
      filteredWidgets.value.filter(w => w.category === 'metric')
    )

    const filteredAlertWidgets = computed(() => 
      filteredWidgets.value.filter(w => w.category === 'alert')
    )

    const filteredDataWidgets = computed(() => 
      filteredWidgets.value.filter(w => w.category === 'data')
    )

    const filteredAdvancedWidgets = computed(() => 
      filteredWidgets.value.filter(w => w.category === 'advanced')
    )

    return {
      searchQuery,
      filteredChartWidgets,
      filteredMetricWidgets,
      filteredAlertWidgets,
      filteredDataWidgets,
      filteredAdvancedWidgets
    }
  }
}
</script>

<style scoped>
.widget-library {
  height: 100vh;
  overflow-y: auto;
}

.widget-category {
  margin-bottom: 1.5rem;
}

.widget-category:last-child {
  margin-bottom: 0;
}
</style>
