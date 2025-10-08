<template>
  <div class="dashboard-canvas bg-gray-100 min-h-full">
    <!-- Canvas Header -->
    <div class="bg-white border-b px-6 py-4">
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-4">
          <h2 class="text-lg font-semibold text-gray-900">Dashboard Canvas</h2>
          <div class="flex items-center space-x-2 text-sm text-gray-600">
            <span>{{ widgets.length }} widgets</span>
            <span>•</span>
            <span>{{ gridSize }}px grid</span>
          </div>
        </div>
        <div class="flex items-center space-x-2">
          <button
            @click="toggleGrid"
            :class="[
              'px-3 py-1 rounded-md text-sm font-medium transition-colors',
              showGrid ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            ]"
          >
            Grid
          </button>
          <button
            @click="clearCanvas"
            class="px-3 py-1 bg-red-100 text-red-700 rounded-md text-sm font-medium hover:bg-red-200 transition-colors"
          >
            Clear All
          </button>
        </div>
      </div>
    </div>

    <!-- Canvas Content -->
    <div class="p-6">
      <div
        ref="canvasRef"
        class="canvas-container relative bg-white rounded-lg shadow-sm border border-gray-200 min-h-96"
        @drop="handleDrop"
        @dragover="handleDragOver"
        @dragenter="handleDragEnter"
        @dragleave="handleDragLeave"
      >
        <!-- Grid Overlay -->
        <div
          v-if="showGrid"
          class="grid-overlay absolute inset-0 pointer-events-none"
          :style="gridStyle"
        ></div>

        <!-- Empty State -->
        <div v-if="widgets.length === 0" class="empty-state flex flex-col items-center justify-center h-96 text-gray-500">
          <div class="text-6xl mb-4">📊</div>
          <h3 class="text-lg font-medium text-gray-900 mb-2">Start Building Your Dashboard</h3>
          <p class="text-sm text-gray-600 mb-4">Drag widgets from the library to get started</p>
          <div class="flex space-x-2">
            <button
              @click="addSampleWidgets"
              class="px-4 py-2 bg-blue-600 text-white rounded-md text-sm font-medium hover:bg-blue-700 transition-colors"
            >
              Add Sample Widgets
            </button>
            <button
              @click="loadTemplate('system-overview')"
              class="px-4 py-2 bg-gray-600 text-white rounded-md text-sm font-medium hover:bg-gray-700 transition-colors"
            >
              Load Template
            </button>
          </div>
        </div>

        <!-- Widgets -->
        <div
          v-for="widget in widgets"
          :key="widget.id"
          class="widget-container absolute"
          :style="getWidgetStyle(widget)"
          @click="selectWidget(widget)"
          @mousedown="startDrag(widget, $event)"
          @contextmenu.prevent="showWidgetMenu(widget, $event)"
        >
          <div
            :class="[
              'widget-content bg-white border-2 rounded-lg shadow-sm transition-all duration-200',
              selectedWidgetId === widget.id ? 'border-blue-500 shadow-lg' : 'border-gray-200 hover:border-gray-300',
              previewMode ? 'cursor-default' : 'cursor-move'
            ]"
          >
            <!-- Widget Header -->
            <div
              v-if="!previewMode"
              class="widget-header flex items-center justify-between p-2 border-b border-gray-100"
            >
              <div class="flex items-center space-x-2">
                <span class="text-sm font-medium text-gray-700">{{ widget.title }}</span>
                <span class="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">{{ widget.type }}</span>
              </div>
              <div class="flex items-center space-x-1">
                <button
                  @click.stop="editWidget(widget)"
                  class="p-1 text-gray-400 hover:text-blue-600 transition-colors"
                  title="Edit Widget"
                >
                  <CogIcon class="w-4 h-4" />
                </button>
                <button
                  @click.stop="removeWidget(widget.id)"
                  class="p-1 text-gray-400 hover:text-red-600 transition-colors"
                  title="Remove Widget"
                >
                  <XMarkIcon class="w-4 h-4" />
                </button>
              </div>
            </div>

            <!-- Widget Body -->
            <div class="widget-body p-3">
              <component
                :is="getWidgetComponent(widget.type)"
                :widget="widget"
                :preview-mode="previewMode"
                @update-widget="updateWidget"
              />
            </div>

            <!-- Resize Handles -->
            <div
              v-if="!previewMode"
              class="resize-handles"
            >
              <div class="resize-handle resize-handle-se" @mousedown.stop="startResize(widget, 'se')"></div>
              <div class="resize-handle resize-handle-sw" @mousedown.stop="startResize(widget, 'sw')"></div>
              <div class="resize-handle resize-handle-ne" @mousedown.stop="startResize(widget, 'ne')"></div>
              <div class="resize-handle resize-handle-nw" @mousedown.stop="startResize(widget, 'nw')"></div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Context Menu -->
    <div
      v-if="contextMenu.visible"
      class="context-menu fixed bg-white border border-gray-200 rounded-lg shadow-lg py-1 z-50"
      :style="contextMenuStyle"
      @click.stop
    >
      <button
        @click="editWidget(contextMenu.widget)"
        class="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-100 flex items-center space-x-2"
      >
        <CogIcon class="w-4 h-4" />
        <span>Edit Widget</span>
      </button>
      <button
        @click="duplicateWidget(contextMenu.widget)"
        class="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-100 flex items-center space-x-2"
      >
        <DocumentDuplicateIcon class="w-4 h-4" />
        <span>Duplicate</span>
      </button>
      <button
        @click="removeWidget(contextMenu.widget.id)"
        class="w-full px-4 py-2 text-left text-sm text-red-700 hover:bg-red-50 flex items-center space-x-2"
      >
        <TrashIcon class="w-4 h-4" />
        <span>Delete</span>
      </button>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { CogIcon, XMarkIcon, DocumentDuplicateIcon, TrashIcon } from '@heroicons/vue/24/outline'
import MetricWidget from '@/components/widgets/MetricWidget.vue'
import ChartWidget from '@/components/widgets/ChartWidget.vue'
import AlertWidget from '@/components/widgets/AlertWidget.vue'
import LogWidget from '@/components/widgets/LogWidget.vue'

export default {
  name: 'DashboardCanvas',
  components: {
    CogIcon,
    XMarkIcon,
    DocumentDuplicateIcon,
    TrashIcon,
    MetricWidget,
    ChartWidget,
    AlertWidget,
    LogWidget
  },
  props: {
    widgets: {
      type: Array,
      required: true
    },
    previewMode: {
      type: Boolean,
      default: false
    }
  },
    emits: ['update-widget', 'remove-widget', 'reorder-widgets', 'load-template', 'select-widget'],
  setup(props, { emit }) {
    const canvasRef = ref(null)
    const selectedWidgetId = ref(null)
    const showGrid = ref(true)
    const gridSize = ref(20)
    
    const contextMenu = reactive({
      visible: false,
      x: 0,
      y: 0,
      widget: null
    })

    const isResizing = ref(false)
    const isDragging = ref(false)
    const resizeData = ref(null)
    const dragData = ref(null)

    // Computed properties
    const gridStyle = computed(() => ({
      backgroundImage: `
        linear-gradient(to right, #e5e7eb 1px, transparent 1px),
        linear-gradient(to bottom, #e5e7eb 1px, transparent 1px)
      `,
      backgroundSize: `${gridSize.value}px ${gridSize.value}px`
    }))

    const contextMenuStyle = computed(() => ({
      left: `${contextMenu.x}px`,
      top: `${contextMenu.y}px`
    }))

    // Methods
    const getWidgetStyle = (widget) => {
      const cellSize = gridSize.value
      return {
        left: `${widget.position.x * cellSize}px`,
        top: `${widget.position.y * cellSize}px`,
        width: `${widget.size.width * cellSize}px`,
        height: `${widget.size.height * cellSize}px`
      }
    }

    const getWidgetComponent = (type) => {
      const components = {
        'metric': 'MetricWidget',
        'line-chart': 'ChartWidget',
        'bar-chart': 'ChartWidget',
        'pie-chart': 'ChartWidget',
        'chart': 'ChartWidget',  // Added for template widgets
        'alert-list': 'AlertWidget',
        'alert': 'AlertWidget',  // Added for template widgets
        'log-viewer': 'LogWidget',
        'log': 'LogWidget'       // Added for template widgets
      }
      return components[type] || 'MetricWidget'
    }

    const selectWidget = (widget) => {
      selectedWidgetId.value = widget.id
      // Emit to parent to open Widget Editor
      emit('select-widget', widget)
    }

    const editWidget = (widget) => {
      emit('update-widget', widget.id, { editing: true })
      contextMenu.visible = false
    }

    const duplicateWidget = (widget) => {
      const newWidget = {
        ...widget,
        id: `widget-${Date.now()}`,
        title: `${widget.title} (Copy)`,
        position: {
          x: widget.position.x + 2,
          y: widget.position.y + 2
        }
      }
      emit('update-widget', newWidget.id, newWidget)
      contextMenu.visible = false
    }

    const removeWidget = (widgetId) => {
      emit('remove-widget', widgetId)
      contextMenu.visible = false
    }

    const showWidgetMenu = (widget, event) => {
      contextMenu.visible = true
      contextMenu.x = event.clientX
      contextMenu.y = event.clientY
      contextMenu.widget = widget
    }

    const handleDrop = (event) => {
      event.preventDefault()
      
      try {
        const data = JSON.parse(event.dataTransfer.getData('application/json'))
        if (data.type === 'widget') {
          const rect = canvasRef.value.getBoundingClientRect()
          const x = Math.floor((event.clientX - rect.left) / gridSize.value)
          const y = Math.floor((event.clientY - rect.top) / gridSize.value)
          
          const newWidget = {
            id: `widget-${Date.now()}`,
            type: data.widgetType,
            title: data.widget.name,
            position: { x, y },
            size: data.widget.defaultSize,
            config: {},
            data: null,
            lastUpdated: new Date()
          }
          
          emit('update-widget', newWidget.id, newWidget)
        }
      } catch (error) {
        console.error('Error handling drop:', error)
      }
    }

    const handleDragOver = (event) => {
      event.preventDefault()
      event.dataTransfer.dropEffect = 'copy'
    }

    const handleDragEnter = (event) => {
      event.preventDefault()
    }

    const handleDragLeave = (event) => {
      event.preventDefault()
    }

    const toggleGrid = () => {
      showGrid.value = !showGrid.value
    }

    const clearCanvas = () => {
      if (confirm('Are you sure you want to clear all widgets?')) {
        props.widgets.forEach(widget => {
          emit('remove-widget', widget.id)
        })
      }
    }

    const addSampleWidgets = () => {
      const sampleWidgets = [
        {
          id: `widget-${Date.now()}-1`,
          type: 'metric',
          title: 'System Health',
          position: { x: 1, y: 1 },
          size: { width: 3, height: 2 },
          config: { value: 95, unit: '%', trend: 'up' }
        },
        {
          id: `widget-${Date.now()}-2`,
          type: 'line-chart',
          title: 'CPU Usage',
          position: { x: 5, y: 1 },
          size: { width: 6, height: 4 },
          config: { chartType: 'line', dataSource: 'cpu' }
        },
        {
          id: `widget-${Date.now()}-3`,
          type: 'alert-list',
          title: 'Active Alerts',
          position: { x: 1, y: 4 },
          size: { width: 10, height: 3 },
          config: { severity: 'all', limit: 5 }
        }
      ]
      
      sampleWidgets.forEach(widget => {
        emit('update-widget', widget.id, widget)
      })
    }

    const loadTemplate = (templateName) => {
      // Emit to parent to load the template
      emit('load-template', templateName)
    }

    const startResize = (widget, direction) => {
      isResizing.value = true
      resizeData.value = { widget, direction }
      
      const handleMouseMove = (e) => {
        if (!isResizing.value) return
        
        const rect = canvasRef.value.getBoundingClientRect()
        const x = Math.floor((e.clientX - rect.left) / gridSize.value)
        const y = Math.floor((e.clientY - rect.top) / gridSize.value)
        
        const newSize = { ...widget.size }
        const newPosition = { ...widget.position }
        
        switch (direction) {
          case 'se': // Southeast
            newSize.width = Math.max(1, x - widget.position.x)
            newSize.height = Math.max(1, y - widget.position.y)
            break
          case 'sw': // Southwest
            newSize.width = Math.max(1, widget.position.x + widget.size.width - x)
            newSize.height = Math.max(1, y - widget.position.y)
            newPosition.x = Math.min(x, widget.position.x + widget.size.width - 1)
            break
          case 'ne': // Northeast
            newSize.width = Math.max(1, x - widget.position.x)
            newSize.height = Math.max(1, widget.position.y + widget.size.height - y)
            newPosition.y = Math.min(y, widget.position.y + widget.size.height - 1)
            break
          case 'nw': // Northwest
            newSize.width = Math.max(1, widget.position.x + widget.size.width - x)
            newSize.height = Math.max(1, widget.position.y + widget.size.height - y)
            newPosition.x = Math.min(x, widget.position.x + widget.size.width - 1)
            newPosition.y = Math.min(y, widget.position.y + widget.size.height - 1)
            break
        }
        
        emit('update-widget', widget.id, {
          size: newSize,
          position: newPosition
        })
      }
      
      const handleMouseUp = () => {
        isResizing.value = false
        resizeData.value = null
        document.removeEventListener('mousemove', handleMouseMove)
        document.removeEventListener('mouseup', handleMouseUp)
      }
      
      document.addEventListener('mousemove', handleMouseMove)
      document.addEventListener('mouseup', handleMouseUp)
    }

    const startDrag = (widget, event) => {
      // Don't start drag if clicking on resize handles or buttons
      if (event.target.closest('.resize-handle') || event.target.closest('button')) {
        return
      }
      
      isDragging.value = true
      dragData.value = {
        widget,
        startX: event.clientX,
        startY: event.clientY,
        startPosition: { ...widget.position }
      }
      
      const handleMouseMove = (e) => {
        if (!isDragging.value) return
        
        const rect = canvasRef.value.getBoundingClientRect()
        const deltaX = e.clientX - dragData.value.startX
        const deltaY = e.clientY - dragData.value.startY
        
        const gridDeltaX = Math.floor(deltaX / gridSize.value)
        const gridDeltaY = Math.floor(deltaY / gridSize.value)
        
        const newPosition = {
          x: Math.max(0, dragData.value.startPosition.x + gridDeltaX),
          y: Math.max(0, dragData.value.startPosition.y + gridDeltaY)
        }
        
        emit('update-widget', widget.id, { position: newPosition })
      }
      
      const handleMouseUp = () => {
        isDragging.value = false
        dragData.value = null
        document.removeEventListener('mousemove', handleMouseMove)
        document.removeEventListener('mouseup', handleMouseUp)
      }
      
      document.addEventListener('mousemove', handleMouseMove)
      document.addEventListener('mouseup', handleMouseUp)
    }

    const updateWidget = (widgetId, updates) => {
      emit('update-widget', widgetId, updates)
    }

    // Event listeners
    const handleClickOutside = (event) => {
      if (!event.target.closest('.context-menu')) {
        contextMenu.visible = false
      }
      if (!event.target.closest('.widget-container')) {
        selectedWidgetId.value = null
      }
    }

    onMounted(() => {
      document.addEventListener('click', handleClickOutside)
    })

    onUnmounted(() => {
      document.removeEventListener('click', handleClickOutside)
    })

    return {
      canvasRef,
      selectedWidgetId,
      showGrid,
      gridSize,
      contextMenu,
      isDragging,
      dragData,
      gridStyle,
      contextMenuStyle,
      getWidgetStyle,
      getWidgetComponent,
      selectWidget,
      editWidget,
      duplicateWidget,
      removeWidget,
      showWidgetMenu,
      handleDrop,
      handleDragOver,
      handleDragEnter,
      handleDragLeave,
      toggleGrid,
      clearCanvas,
      addSampleWidgets,
      loadTemplate,
      startResize,
      startDrag,
      updateWidget
    }
  }
}
</script>

<style scoped>
.dashboard-canvas {
  height: calc(100vh - 80px);
  overflow: auto;
}

.canvas-container {
  min-height: 600px;
  position: relative;
}

.grid-overlay {
  opacity: 0.3;
}

.widget-container {
  z-index: 10;
}

.widget-content {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.widget-header {
  flex-shrink: 0;
}

.widget-body {
  flex: 1;
  overflow: hidden;
}

.resize-handles {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
}

.resize-handle {
  position: absolute;
  width: 8px;
  height: 8px;
  background: #3b82f6;
  border: 1px solid white;
  pointer-events: all;
  cursor: se-resize;
}

.resize-handle-se {
  bottom: -4px;
  right: -4px;
  cursor: se-resize;
}

.resize-handle-sw {
  bottom: -4px;
  left: -4px;
  cursor: sw-resize;
}

.resize-handle-ne {
  top: -4px;
  right: -4px;
  cursor: ne-resize;
}

.resize-handle-nw {
  top: -4px;
  left: -4px;
  cursor: nw-resize;
}

.context-menu {
  min-width: 150px;
}

.empty-state {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}
</style>
