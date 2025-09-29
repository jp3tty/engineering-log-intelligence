<template>
  <div
    class="widget-item bg-white border border-gray-200 rounded-lg p-3 cursor-pointer hover:shadow-md transition-shadow duration-200 hover:border-blue-300"
    @click="handleAddWidget"
    @dragstart="handleDragStart"
    @dragend="handleDragEnd"
    draggable="true"
  >
    <div class="flex items-center space-x-2 mb-2">
      <span class="text-lg">{{ widget.icon }}</span>
      <h4 class="text-sm font-medium text-gray-900 truncate">{{ widget.name }}</h4>
    </div>
    <p class="text-xs text-gray-600 mb-2 line-clamp-2">{{ widget.description }}</p>
    <div class="flex items-center justify-between text-xs text-gray-500">
      <span>{{ widget.defaultSize.width }}×{{ widget.defaultSize.height }}</span>
      <button
        @click.stop="handleAddWidget"
        class="px-2 py-1 bg-blue-100 text-blue-700 rounded hover:bg-blue-200 transition-colors"
      >
        Add
      </button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'WidgetItem',
  props: {
    widget: {
      type: Object,
      required: true
    }
  },
  emits: ['add-widget'],
  setup(props, { emit }) {
    const handleAddWidget = () => {
      emit('add-widget', props.widget.type)
    }

    const handleDragStart = (event) => {
      event.dataTransfer.setData('application/json', JSON.stringify({
        type: 'widget',
        widgetType: props.widget.type,
        widget: props.widget
      }))
      event.dataTransfer.effectAllowed = 'copy'
      
      // Add visual feedback
      event.target.style.opacity = '0.5'
    }

    const handleDragEnd = (event) => {
      event.target.style.opacity = '1'
    }

    return {
      handleAddWidget,
      handleDragStart,
      handleDragEnd
    }
  }
}
</script>

<style scoped>
.widget-item {
  min-height: 80px;
}

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
