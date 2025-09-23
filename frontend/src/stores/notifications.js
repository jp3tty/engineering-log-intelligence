/**
 * Notifications Store
 * ===================
 * 
 * This store manages application notifications and alerts.
 * It handles displaying, dismissing, and managing notifications.
 * 
 * For beginners: This store manages popup messages and alerts
 * that appear to users, like success messages or error warnings.
 * 
 * Author: Engineering Log Intelligence Team
 * Date: September 22, 2025
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useNotificationStore = defineStore('notifications', () => {
  // State
  const notifications = ref([])
  const maxNotifications = 10

  // Getters
  const activeNotifications = computed(() => 
    notifications.value.filter(n => !n.dismissed)
  )
  
  const unreadCount = computed(() => 
    notifications.value.filter(n => !n.read && !n.dismissed).length
  )

  // Actions
  const addNotification = (notification) => {
    const id = Date.now() + Math.random()
    const newNotification = {
      id,
      type: 'info', // info, success, warning, error
      title: '',
      message: '',
      duration: 5000, // Auto-dismiss after 5 seconds (0 = persistent)
      read: false,
      dismissed: false,
      timestamp: new Date().toISOString(),
      ...notification,
    }

    notifications.value.unshift(newNotification)

    // Remove oldest notifications if we exceed the limit
    if (notifications.value.length > maxNotifications) {
      notifications.value = notifications.value.slice(0, maxNotifications)
    }

    // Auto-dismiss if duration is set
    if (newNotification.duration > 0) {
      setTimeout(() => {
        dismissNotification(id)
      }, newNotification.duration)
    }

    return id
  }

  const dismissNotification = (id) => {
    const index = notifications.value.findIndex(n => n.id === id)
    if (index !== -1) {
      notifications.value[index].dismissed = true
    }
  }

  const markAsRead = (id) => {
    const notification = notifications.value.find(n => n.id === id)
    if (notification) {
      notification.read = true
    }
  }

  const markAllAsRead = () => {
    notifications.value.forEach(notification => {
      notification.read = true
    })
  }

  const clearAll = () => {
    notifications.value = []
  }

  const clearDismissed = () => {
    notifications.value = notifications.value.filter(n => !n.dismissed)
  }

  // Convenience methods for different notification types
  const showSuccess = (title, message, duration = 5000) => {
    return addNotification({
      type: 'success',
      title,
      message,
      duration,
    })
  }

  const showError = (title, message, duration = 0) => {
    return addNotification({
      type: 'error',
      title,
      message,
      duration,
    })
  }

  const showWarning = (title, message, duration = 7000) => {
    return addNotification({
      type: 'warning',
      title,
      message,
      duration,
    })
  }

  const showInfo = (title, message, duration = 5000) => {
    return addNotification({
      type: 'info',
      title,
      message,
      duration,
    })
  }

  // Load notifications from localStorage
  const loadStoredNotifications = () => {
    try {
      const stored = localStorage.getItem('notifications')
      if (stored) {
        const parsed = JSON.parse(stored)
        notifications.value = parsed.filter(n => {
          // Only load recent notifications (within last 24 hours)
          const notificationTime = new Date(n.timestamp)
          const dayAgo = new Date(Date.now() - 24 * 60 * 60 * 1000)
          return notificationTime > dayAgo
        })
      }
    } catch (err) {
      console.warn('Failed to load stored notifications:', err.message)
    }
  }

  // Save notifications to localStorage
  const saveNotifications = () => {
    try {
      localStorage.setItem('notifications', JSON.stringify(notifications.value))
    } catch (err) {
      console.warn('Failed to save notifications:', err.message)
    }
  }

  // Watch for changes and save to localStorage
  const setupPersistence = () => {
    // Save whenever notifications change
    const unwatch = ref(notifications).value // This is a simplified approach
    // In a real implementation, you'd use a watcher
  }

  return {
    // State
    notifications,
    maxNotifications,
    
    // Getters
    activeNotifications,
    unreadCount,
    
    // Actions
    addNotification,
    dismissNotification,
    markAsRead,
    markAllAsRead,
    clearAll,
    clearDismissed,
    
    // Convenience methods
    showSuccess,
    showError,
    showWarning,
    showInfo,
    
    // Persistence
    loadStoredNotifications,
    saveNotifications,
    setupPersistence,
  }
})
