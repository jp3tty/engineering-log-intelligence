<template>
  <div id="app" class="min-h-screen bg-gray-50">
    <!-- Navigation Header -->
    <AppHeader />
    
    <!-- Main Content Area -->
    <main class="flex-1">
      <!-- Router View - This is where different pages are displayed -->
      <router-view v-slot="{ Component, route }">
        <transition name="page" mode="out-in">
          <component :is="Component" :key="route.path" />
        </transition>
      </router-view>
    </main>
    
    <!-- Footer -->
    <AppFooter />
    
    <!-- Global Notifications -->
    <NotificationContainer />
    
    <!-- Loading Overlay -->
    <LoadingOverlay v-if="isLoading" />
  </div>
</template>

<script>
/**
 * Main App Component
 * =================
 * 
 * This is the root component of our Vue.js application.
 * It provides the overall layout and structure for the entire app.
 * 
 * For beginners: This is like the "main layout" of our website.
 * It includes the header, main content area, and footer that appear
 * on every page.
 * 
 * Author: Engineering Log Intelligence Team
 * Date: September 22, 2025
 */

import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useNotificationStore } from '@/stores/notifications'
import { useSystemStore } from '@/stores/system'

// Import components
import AppHeader from '@/components/layout/AppHeader.vue'
import AppFooter from '@/components/layout/AppFooter.vue'
import NotificationContainer from '@/components/common/NotificationContainer.vue'
import LoadingOverlay from '@/components/common/LoadingOverlay.vue'

export default {
  name: 'App',
  components: {
    AppHeader,
    AppFooter,
    NotificationContainer,
    LoadingOverlay,
  },
  setup() {
    const router = useRouter()
    const authStore = useAuthStore()
    const notificationStore = useNotificationStore()
    const systemStore = useSystemStore()
    
    // Reactive data
    const isLoading = ref(false)
    
    // Initialize application
    const initializeApp = async () => {
      try {
        isLoading.value = true
        
        // Initialize authentication
        await authStore.initializeAuth()
        
        // Initialize system status
        await systemStore.initializeSystem()
        
        // Check for any pending notifications
        notificationStore.loadStoredNotifications()
        
        console.log('✅ Application initialized successfully')
        
      } catch (error) {
        console.error('❌ Failed to initialize application:', error)
        notificationStore.addNotification({
          type: 'error',
          title: 'Initialization Error',
          message: 'Failed to initialize the application. Please refresh the page.',
          duration: 0, // Persistent notification
        })
      } finally {
        isLoading.value = false
      }
    }
    
    // Handle route changes
    const handleRouteChange = (to, from) => {
      // Track page views (in production, you might send this to analytics)
      console.log(`📄 Navigating from ${from?.path || 'unknown'} to ${to.path}`)
      
      // Update page title with portfolio label
      document.title = to.meta?.title 
        ? `${to.meta.title} - Engineering Log Intelligence | Portfolio Project`
        : 'Engineering Log Intelligence | Portfolio Project'
    }
    
    // Handle global errors
    const handleGlobalError = (event) => {
      console.error('🚨 Global error:', event.error)
      notificationStore.addNotification({
        type: 'error',
        title: 'Unexpected Error',
        message: 'An unexpected error occurred. Please try again.',
        duration: 5000,
      })
    }
    
    // Handle unhandled promise rejections
    const handleUnhandledRejection = (event) => {
      console.error('🚨 Unhandled promise rejection:', event.reason)
      notificationStore.addNotification({
        type: 'error',
        title: 'Network Error',
        message: 'A network error occurred. Please check your connection.',
        duration: 5000,
      })
    }
    
    // Lifecycle hooks
    onMounted(() => {
      // Initialize the application
      initializeApp()
      
      // Set up global error handlers
      window.addEventListener('error', handleGlobalError)
      window.addEventListener('unhandledrejection', handleUnhandledRejection)
      
      // Set up route change handler
      router.afterEach(handleRouteChange)
    })
    
    onUnmounted(() => {
      // Clean up event listeners
      window.removeEventListener('error', handleGlobalError)
      window.removeEventListener('unhandledrejection', handleUnhandledRejection)
    })
    
    return {
      isLoading,
    }
  },
}
</script>

<style scoped>
/* Page transition animations */
.page-enter-active,
.page-leave-active {
  transition: all 0.3s ease;
}

.page-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

.page-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}

/* Global app styles */
#app {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

main {
  flex: 1;
  padding-top: 4rem; /* Account for fixed header */
}
</style>
