<template>
  <div class="fixed top-4 right-4 z-50 space-y-2">
    <transition-group name="notification" tag="div">
      <div
        v-for="notification in activeNotifications"
        :key="notification.id"
        class="notification"
        :class="getNotificationClass(notification.type)"
      >
        <div class="flex">
          <div class="flex-shrink-0">
            <component :is="getNotificationIcon(notification.type)" class="w-5 h-5" />
          </div>
          <div class="ml-3 flex-1">
            <h4 class="text-sm font-medium">{{ notification.title }}</h4>
            <p class="text-sm opacity-90">{{ notification.message }}</p>
          </div>
          <div class="ml-4 flex-shrink-0">
            <button
              @click="dismissNotification(notification.id)"
              class="inline-flex text-white hover:text-gray-200 focus:outline-none"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </transition-group>
  </div>
</template>

<script>
/**
 * Notification Container Component
 * ===============================
 * 
 * This component displays notifications to the user.
 * It shows success, error, warning, and info messages.
 * 
 * For beginners: This component shows popup messages
 * that appear in the top-right corner of the screen.
 * 
 * Author: Engineering Log Intelligence Team
 * Date: September 22, 2025
 */

import { computed } from 'vue'
import { useNotificationStore } from '@/stores/notifications'

// Icon components
const SuccessIcon = { template: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>' }
const ErrorIcon = { template: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>' }
const WarningIcon = { template: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" /></svg>' }
const InfoIcon = { template: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>' }

export default {
  name: 'NotificationContainer',
  components: {
    SuccessIcon,
    ErrorIcon,
    WarningIcon,
    InfoIcon,
  },
  setup() {
    const notificationStore = useNotificationStore()

    // Computed properties
    const activeNotifications = computed(() => notificationStore.activeNotifications)

    // Methods
    const getNotificationClass = (type) => {
      switch (type) {
        case 'success':
          return 'bg-success-50 border-success-200 text-success-800'
        case 'error':
          return 'bg-danger-50 border-danger-200 text-danger-800'
        case 'warning':
          return 'bg-warning-50 border-warning-200 text-warning-800'
        case 'info':
        default:
          return 'bg-primary-50 border-primary-200 text-primary-800'
      }
    }

    const getNotificationIcon = (type) => {
      switch (type) {
        case 'success':
          return 'SuccessIcon'
        case 'error':
          return 'ErrorIcon'
        case 'warning':
          return 'WarningIcon'
        case 'info':
        default:
          return 'InfoIcon'
      }
    }

    const dismissNotification = (id) => {
      notificationStore.dismissNotification(id)
    }

    return {
      // Computed
      activeNotifications,
      
      // Methods
      getNotificationClass,
      getNotificationIcon,
      dismissNotification,
    }
  },
}
</script>

<style scoped>
.notification {
  @apply max-w-sm w-full bg-white shadow-lg rounded-lg pointer-events-auto ring-1 ring-black ring-opacity-5 overflow-hidden border;
}

.notification-enter-active,
.notification-leave-active {
  transition: all 0.3s ease;
}

.notification-enter-from {
  opacity: 0;
  transform: translateX(100%);
}

.notification-leave-to {
  opacity: 0;
  transform: translateX(100%);
}
</style>
