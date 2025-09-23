<template>
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
    <div class="bg-white rounded-lg p-8 max-w-sm w-full mx-4">
      <div class="text-center">
        <!-- Loading Spinner -->
        <div class="flex justify-center mb-4">
          <div class="spinner w-8 h-8"></div>
        </div>
        
        <!-- Loading Text -->
        <h3 class="text-lg font-medium text-gray-900 mb-2">
          {{ title }}
        </h3>
        <p class="text-sm text-gray-600">
          {{ message }}
        </p>
        
        <!-- Progress Bar (if progress is provided) -->
        <div v-if="progress !== null" class="mt-4">
          <div class="w-full bg-gray-200 rounded-full h-2">
            <div 
              class="bg-primary-600 h-2 rounded-full transition-all duration-300"
              :style="{ width: `${progress}%` }"
            ></div>
          </div>
          <p class="text-xs text-gray-500 mt-2">{{ progress }}% complete</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
/**
 * Loading Overlay Component
 * =========================
 * 
 * This component displays a loading overlay with spinner and optional progress.
 * It's used when the application is performing async operations.
 * 
 * For beginners: This component shows a loading screen that covers
 * the entire page while something is loading.
 * 
 * Author: Engineering Log Intelligence Team
 * Date: September 22, 2025
 */

export default {
  name: 'LoadingOverlay',
  props: {
    title: {
      type: String,
      default: 'Loading...',
    },
    message: {
      type: String,
      default: 'Please wait while we process your request.',
    },
    progress: {
      type: Number,
      default: null,
    },
  },
}
</script>
