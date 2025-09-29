<template>
  <div class="widget-editor p-4">
    <div class="mb-6">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-lg font-semibold text-gray-900">Widget Editor</h2>
        <button
          @click="$emit('close-editor')"
          class="p-2 text-gray-400 hover:text-gray-600 transition-colors"
        >
          <XMarkIcon class="w-5 h-5" />
        </button>
      </div>
      <div class="flex items-center space-x-2 text-sm text-gray-600">
        <span class="bg-gray-100 px-2 py-1 rounded">{{ widget.type }}</span>
        <span>•</span>
        <span>{{ widget.size.width }}×{{ widget.size.height }}</span>
      </div>
    </div>

    <div class="space-y-6">
      <!-- Basic Settings -->
      <div class="settings-section">
        <h3 class="text-sm font-medium text-gray-700 mb-3">Basic Settings</h3>
        <div class="space-y-3">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Title</label>
            <input
              v-model="localWidget.title"
              type="text"
              class="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              @input="updateWidget"
            />
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Description</label>
            <textarea
              v-model="localWidget.description"
              rows="2"
              class="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              @input="updateWidget"
            ></textarea>
          </div>
        </div>
      </div>

      <!-- Size & Position -->
      <div class="settings-section">
        <h3 class="text-sm font-medium text-gray-700 mb-3">Size & Position</h3>
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Width</label>
            <input
              v-model.number="localWidget.size.width"
              type="number"
              min="1"
              max="12"
              class="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              @input="updateWidget"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Height</label>
            <input
              v-model.number="localWidget.size.height"
              type="number"
              min="1"
              max="8"
              class="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              @input="updateWidget"
            />
          </div>
        </div>
      </div>

      <!-- Widget-specific Settings -->
      <div class="settings-section">
        <h3 class="text-sm font-medium text-gray-700 mb-3">Widget Configuration</h3>
        
        <!-- Metric Widget Settings -->
        <div v-if="widget.type === 'metric'" class="space-y-3">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Value</label>
            <input
              v-model.number="localWidget.config.value"
              type="number"
              class="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              @input="updateWidget"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Unit</label>
            <input
              v-model="localWidget.config.unit"
              type="text"
              placeholder="%, MB, ms, etc."
              class="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              @input="updateWidget"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Trend</label>
            <select
              v-model="localWidget.config.trend"
              class="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              @change="updateWidget"
            >
              <option value="up">Trending Up</option>
              <option value="down">Trending Down</option>
              <option value="neutral">Neutral</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Color</label>
            <select
              v-model="localWidget.config.color"
              class="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              @change="updateWidget"
            >
              <option value="blue">Blue</option>
              <option value="green">Green</option>
              <option value="yellow">Yellow</option>
              <option value="red">Red</option>
              <option value="purple">Purple</option>
            </select>
          </div>
        </div>

        <!-- Chart Widget Settings -->
        <div v-else-if="widget.type.includes('chart')" class="space-y-3">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Chart Type</label>
            <select
              v-model="localWidget.config.chartType"
              class="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              @change="updateWidget"
            >
              <option value="line">Line Chart</option>
              <option value="bar">Bar Chart</option>
              <option value="pie">Pie Chart</option>
              <option value="scatter">Scatter Plot</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Data Source</label>
            <select
              v-model="localWidget.config.dataSource"
              class="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              @change="updateWidget"
            >
              <option value="system_metrics">System Metrics</option>
              <option value="application_logs">Application Logs</option>
              <option value="performance_data">Performance Data</option>
              <option value="custom_query">Custom Query</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Time Range</label>
            <select
              v-model="localWidget.config.timeRange"
              class="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              @change="updateWidget"
            >
              <option value="5m">Last 5 minutes</option>
              <option value="15m">Last 15 minutes</option>
              <option value="1h">Last hour</option>
              <option value="6h">Last 6 hours</option>
              <option value="24h">Last 24 hours</option>
              <option value="7d">Last 7 days</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Refresh Interval (seconds)</label>
            <input
              v-model.number="localWidget.config.refreshInterval"
              type="number"
              min="10"
              max="3600"
              class="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              @input="updateWidget"
            />
          </div>
        </div>

        <!-- Alert Widget Settings -->
        <div v-else-if="widget.type === 'alert-list'" class="space-y-3">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Severity Filter</label>
            <select
              v-model="localWidget.config.severity"
              class="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              @change="updateWidget"
            >
              <option value="all">All Severities</option>
              <option value="critical">Critical Only</option>
              <option value="high">High and Critical</option>
              <option value="medium">Medium and Above</option>
              <option value="low">All Including Low</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Alert Limit</label>
            <input
              v-model.number="localWidget.config.limit"
              type="number"
              min="1"
              max="100"
              class="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              @input="updateWidget"
            />
          </div>
          <div class="flex items-center">
            <input
              v-model="localWidget.config.autoRefresh"
              type="checkbox"
              id="autoRefresh"
              class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              @change="updateWidget"
            />
            <label for="autoRefresh" class="ml-2 block text-sm text-gray-700">
              Auto-refresh
            </label>
          </div>
        </div>

        <!-- Log Widget Settings -->
        <div v-else-if="widget.type === 'log-viewer'" class="space-y-3">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Log Level</label>
            <select
              v-model="localWidget.config.logLevel"
              class="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              @change="updateWidget"
            >
              <option value="all">All Levels</option>
              <option value="error">Error Only</option>
              <option value="warning">Warning and Error</option>
              <option value="info">Info and Above</option>
              <option value="debug">All Including Debug</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Log Limit</label>
            <input
              v-model.number="localWidget.config.limit"
              type="number"
              min="10"
              max="1000"
              class="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              @input="updateWidget"
            />
          </div>
          <div class="flex items-center">
            <input
              v-model="localWidget.config.autoRefresh"
              type="checkbox"
              id="logAutoRefresh"
              class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              @change="updateWidget"
            />
            <label for="logAutoRefresh" class="ml-2 block text-sm text-gray-700">
              Auto-refresh
            </label>
          </div>
        </div>

        <!-- Default Settings -->
        <div v-else class="text-sm text-gray-500">
          No specific configuration options for this widget type.
        </div>
      </div>

      <!-- Advanced Settings -->
      <div class="settings-section">
        <h3 class="text-sm font-medium text-gray-700 mb-3">Advanced Settings</h3>
        <div class="space-y-3">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Custom CSS Class</label>
            <input
              v-model="localWidget.config.cssClass"
              type="text"
              placeholder="custom-class"
              class="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              @input="updateWidget"
            />
          </div>
          <div class="flex items-center">
            <input
              v-model="localWidget.config.hidden"
              type="checkbox"
              id="hidden"
              class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              @change="updateWidget"
            />
            <label for="hidden" class="ml-2 block text-sm text-gray-700">
              Hide widget
            </label>
          </div>
        </div>
      </div>

      <!-- Actions -->
      <div class="settings-section border-t pt-4">
        <div class="flex space-x-2">
          <button
            @click="resetWidget"
            class="flex-1 px-3 py-2 bg-gray-100 text-gray-700 rounded-md text-sm font-medium hover:bg-gray-200 transition-colors"
          >
            Reset
          </button>
          <button
            @click="duplicateWidget"
            class="flex-1 px-3 py-2 bg-blue-100 text-blue-700 rounded-md text-sm font-medium hover:bg-blue-200 transition-colors"
          >
            Duplicate
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, watch } from 'vue'
import { XMarkIcon } from '@heroicons/vue/24/outline'

export default {
  name: 'WidgetEditor',
  components: {
    XMarkIcon
  },
  props: {
    widget: {
      type: Object,
      required: true
    }
  },
  emits: ['update-widget', 'close-editor'],
  setup(props, { emit }) {
    const localWidget = ref({ ...props.widget })

    // Watch for prop changes
    watch(() => props.widget, (newWidget) => {
      localWidget.value = { ...newWidget }
    }, { deep: true })

    const updateWidget = () => {
      emit('update-widget', props.widget.id, localWidget.value)
    }

    const resetWidget = () => {
      if (confirm('Are you sure you want to reset this widget to default settings?')) {
        localWidget.value = { ...props.widget }
        updateWidget()
      }
    }

    const duplicateWidget = () => {
      const duplicatedWidget = {
        ...localWidget.value,
        id: `widget-${Date.now()}`,
        title: `${localWidget.value.title} (Copy)`,
        position: {
          x: localWidget.value.position.x + 2,
          y: localWidget.value.position.y + 2
        }
      }
      emit('update-widget', duplicatedWidget.id, duplicatedWidget)
    }

    return {
      localWidget,
      updateWidget,
      resetWidget,
      duplicateWidget
    }
  }
}
</script>

<style scoped>
.widget-editor {
  height: 100vh;
  overflow-y: auto;
}

.settings-section {
  padding-bottom: 1.5rem;
}

.settings-section:last-child {
  padding-bottom: 0;
}
</style>
