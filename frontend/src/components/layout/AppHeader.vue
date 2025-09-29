<template>
  <header class="bg-white shadow-sm border-b border-gray-200 fixed top-0 left-0 right-0 z-50">
    <div class="container-custom">
      <div class="flex items-center justify-between h-16">
        <!-- Logo and Brand -->
        <div class="flex items-center space-x-4">
          <router-link to="/dashboard" class="flex items-center space-x-2">
            <div class="w-8 h-8 bg-gradient-to-r from-primary-500 to-primary-700 rounded-lg flex items-center justify-center">
              <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <span class="text-xl font-bold text-gray-900">Log Intelligence</span>
          </router-link>
        </div>

        <!-- Navigation Menu -->
        <nav class="hidden md:flex items-center space-x-1">
          <router-link
            v-for="route in navigationRoutes"
            :key="route.name"
            :to="route.path"
            class="nav-link"
            :class="{ 'nav-link-active': $route.name === route.name }"
          >
            <component :is="route.icon" class="w-4 h-4" />
            <span>{{ route.title }}</span>
          </router-link>
        </nav>

        <!-- Right Side Actions -->
        <div class="flex items-center space-x-4">
          <!-- System Status Indicator -->
          <div class="flex items-center space-x-2">
            <div 
              class="status-indicator"
              :class="statusClass"
              :title="systemStatus"
            ></div>
            <span class="text-sm text-gray-600 hidden sm:block">{{ systemStatus }}</span>
          </div>

          <!-- Notifications -->
          <button
            @click="toggleNotifications"
            class="relative p-2 text-gray-400 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-primary-500 rounded-md"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-5 5v-5zM4 19h6v-6H4v6z" />
            </svg>
            <span
              v-if="unreadCount > 0"
              class="absolute -top-1 -right-1 bg-danger-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center"
            >
              {{ unreadCount > 9 ? '9+' : unreadCount }}
            </span>
          </button>

          <!-- User Menu -->
          <div class="relative" ref="userMenuRef">
            <button
              @click="toggleUserMenu"
              class="flex items-center space-x-2 p-2 text-gray-700 hover:bg-gray-100 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <div class="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
                <span class="text-sm font-medium text-primary-700">
                  {{ userInitials }}
                </span>
              </div>
              <span class="hidden sm:block text-sm font-medium">{{ user?.username || 'User' }}</span>
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
              </svg>
            </button>

            <!-- User Dropdown Menu -->
            <div
              v-if="showUserMenu"
              class="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg py-1 z-50 border border-gray-200"
            >
              <div class="px-4 py-2 border-b border-gray-100">
                <p class="text-sm font-medium text-gray-900">{{ user?.username || 'User' }}</p>
                <p class="text-xs text-gray-500">{{ user?.email || 'user@example.com' }}</p>
                <p class="text-xs text-primary-600 capitalize">{{ user?.role || 'viewer' }}</p>
              </div>
              
              <router-link
                to="/settings"
                class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                @click="showUserMenu = false"
              >
                Settings
              </router-link>
              
              <button
                @click="handleLogout"
                class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
              >
                Sign out
              </button>
            </div>
          </div>

          <!-- Mobile Menu Button -->
          <button
            @click="toggleMobileMenu"
            class="md:hidden p-2 text-gray-400 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-primary-500 rounded-md"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
        </div>
      </div>

      <!-- Mobile Navigation Menu -->
      <div v-if="showMobileMenu" class="md:hidden border-t border-gray-200 py-4">
        <nav class="space-y-1">
          <router-link
            v-for="route in navigationRoutes"
            :key="route.name"
            :to="route.path"
            class="mobile-nav-link"
            :class="{ 'mobile-nav-link-active': $route.name === route.name }"
            @click="showMobileMenu = false"
          >
            <component :is="route.icon" class="w-5 h-5" />
            <span>{{ route.title }}</span>
          </router-link>
        </nav>
      </div>
    </div>
  </header>
</template>

<script>
/**
 * App Header Component
 * ===================
 * 
 * This component provides the main navigation header for the application.
 * It includes the logo, navigation menu, user menu, and system status.
 * 
 * For beginners: This is the top bar of our application that appears
 * on every page. It contains navigation links and user controls.
 * 
 * Author: Engineering Log Intelligence Team
 * Date: September 22, 2025
 */

import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useSystemStore } from '@/stores/system'
import { useNotificationStore } from '@/stores/notifications'

// Icon components (simplified for this example)
const ChartBarIcon = { template: '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" /></svg>' }
const DocumentTextIcon = { template: '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>' }
const BeakerIcon = { template: '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" /></svg>' }
const ChartPieIcon = { template: '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 3.055A9.001 9.001 0 1020.945 13H11V3.055z" /><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.488 9H15V3.512A9.025 9.025 0 0120.488 9z" /></svg>' }
const CogIcon = { template: '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" /><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /></svg>' }
const PuzzlePieceIcon = { template: '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 4a2 2 0 114 0v1a1 1 0 001 1h3a1 1 0 011 1v3a1 1 0 01-1 1h-1a2 2 0 100 4h1a1 1 0 011 1v3a1 1 0 01-1 1h-3a1 1 0 01-1-1v-1a2 2 0 10-4 0v1a1 1 0 01-1 1H7a1 1 0 01-1-1v-3a1 1 0 00-1-1H4a1 1 0 01-1-1V9a1 1 0 011-1h1a2 2 0 100-4H4a1 1 0 01-1-1V4a1 1 0 011-1h3a1 1 0 001 1v1z" /></svg>' }
const AnalyticsIcon = { template: '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" /></svg>' }

export default {
  name: 'AppHeader',
  components: {
    ChartBarIcon,
    DocumentTextIcon,
    BeakerIcon,
    ChartPieIcon,
    CogIcon,
    PuzzlePieceIcon,
    AnalyticsIcon,
  },
  setup() {
    const router = useRouter()
    const authStore = useAuthStore()
    const systemStore = useSystemStore()
    const notificationStore = useNotificationStore()

    // Reactive data
    const showUserMenu = ref(false)
    const showMobileMenu = ref(false)
    const userMenuRef = ref(null)

    // Navigation routes
    const navigationRoutes = [
      {
        name: 'Dashboard',
        path: '/dashboard',
        title: 'Dashboard',
        icon: 'ChartBarIcon',
      },
      {
        name: 'AnalyticsDashboard',
        path: '/analytics',
        title: 'Analytics',
        icon: 'AnalyticsIcon',
        requiresRole: ['analyst', 'admin'],
      },
      {
        name: 'DashboardBuilder',
        path: '/dashboard-builder',
        title: 'Dashboard Builder',
        icon: 'PuzzlePieceIcon',
      },
      {
        name: 'LogAnalysis',
        path: '/logs',
        title: 'Log Analysis',
        icon: 'DocumentTextIcon',
      },
      {
        name: 'ABTesting',
        path: '/ab-testing',
        title: 'A/B Testing',
        icon: 'BeakerIcon',
        requiresRole: ['analyst', 'admin'],
      },
      {
        name: 'Monitoring',
        path: '/monitoring',
        title: 'Monitoring',
        icon: 'ChartPieIcon',
      },
      {
        name: 'Settings',
        path: '/settings',
        title: 'Settings',
        icon: 'CogIcon',
      },
    ]

    // Computed properties
    const user = computed(() => authStore.user)
    const userInitials = computed(() => {
      if (!user.value) return 'U'
      const name = user.value.username || user.value.email || 'User'
      return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
    })

    const systemStatus = computed(() => {
      if (systemStore.isHealthy) return 'Healthy'
      if (systemStore.isDegraded) return 'Degraded'
      if (systemStore.isUnhealthy) return 'Unhealthy'
      return 'Unknown'
    })

    const statusClass = computed(() => {
      if (systemStore.isHealthy) return 'status-online'
      if (systemStore.isDegraded) return 'status-warning'
      if (systemStore.isUnhealthy) return 'status-error'
      return 'status-offline'
    })

    const unreadCount = computed(() => notificationStore.unreadCount)

    // Filter navigation routes based on user permissions
    const filteredNavigationRoutes = computed(() => {
      return navigationRoutes.filter(route => {
        if (route.requiresRole) {
          return authStore.hasAnyRole(route.requiresRole)
        }
        return true
      })
    })

    // Methods
    const toggleUserMenu = () => {
      showUserMenu.value = !showUserMenu.value
    }

    const toggleMobileMenu = () => {
      showMobileMenu.value = !showMobileMenu.value
    }

    const toggleNotifications = () => {
      // This would open a notifications panel
      console.log('Toggle notifications')
    }

    const handleLogout = async () => {
      try {
        await authStore.logout()
        router.push('/login')
      } catch (error) {
        console.error('Logout failed:', error)
      }
    }

    // Close dropdowns when clicking outside
    const handleClickOutside = (event) => {
      if (userMenuRef.value && !userMenuRef.value.contains(event.target)) {
        showUserMenu.value = false
      }
    }

    // Lifecycle
    onMounted(() => {
      document.addEventListener('click', handleClickOutside)
    })

    onUnmounted(() => {
      document.removeEventListener('click', handleClickOutside)
    })

    return {
      // Data
      showUserMenu,
      showMobileMenu,
      userMenuRef,
      navigationRoutes: filteredNavigationRoutes,
      
      // Computed
      user,
      userInitials,
      systemStatus,
      statusClass,
      unreadCount,
      
      // Methods
      toggleUserMenu,
      toggleMobileMenu,
      toggleNotifications,
      handleLogout,
    }
  },
}
</script>

<style scoped>
.nav-link {
  @apply flex items-center space-x-2 px-3 py-2 text-sm font-medium text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md transition-colors duration-200;
}

.nav-link-active {
  @apply text-primary-600 bg-primary-50;
}

.mobile-nav-link {
  @apply flex items-center space-x-3 px-3 py-2 text-base font-medium text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md transition-colors duration-200;
}

.mobile-nav-link-active {
  @apply text-primary-600 bg-primary-50;
}
</style>
