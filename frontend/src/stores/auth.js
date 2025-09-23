/**
 * Authentication Store
 * ===================
 * 
 * This store manages user authentication state and operations.
 * It handles login, logout, token management, and user data.
 * 
 * For beginners: A "store" is like a global data container that
 * different parts of our app can access and modify. This one
 * specifically handles user login and authentication.
 * 
 * Author: Engineering Log Intelligence Team
 * Date: September 22, 2025
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref(null)
  const token = ref(localStorage.getItem('auth_token'))
  const refreshToken = ref(localStorage.getItem('refresh_token'))
  const isLoading = ref(false)
  const error = ref(null)

  // Getters (computed properties)
  const isAuthenticated = computed(() => !!token.value && !!user.value)
  const userRole = computed(() => user.value?.role || 'viewer')
  const userPermissions = computed(() => user.value?.permissions || [])
  const isAdmin = computed(() => userRole.value === 'admin')
  const isAnalyst = computed(() => ['analyst', 'admin'].includes(userRole.value))

  // Actions
  const setAuthData = (authData) => {
    user.value = authData.user
    token.value = authData.tokens.access_token
    refreshToken.value = authData.tokens.refresh_token
    
    // Store in localStorage
    localStorage.setItem('auth_token', token.value)
    localStorage.setItem('refresh_token', refreshToken.value)
    localStorage.setItem('user_data', JSON.stringify(user.value))
  }

  const clearAuthData = () => {
    user.value = null
    token.value = null
    refreshToken.value = null
    
    // Clear localStorage
    localStorage.removeItem('auth_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user_data')
  }

  const setError = (errorMessage) => {
    error.value = errorMessage
    setTimeout(() => {
      error.value = null
    }, 5000)
  }

  const login = async (credentials) => {
    try {
      isLoading.value = true
      error.value = null

      const response = await axios.post('/api/auth/login', credentials)
      
      if (response.data && response.data.tokens) {
        setAuthData(response.data)
        return { success: true, data: response.data }
      } else {
        throw new Error('Invalid response format')
      }
    } catch (err) {
      const errorMessage = err.response?.data?.error || err.message || 'Login failed'
      setError(errorMessage)
      return { success: false, error: errorMessage }
    } finally {
      isLoading.value = false
    }
  }

  const logout = async () => {
    try {
      // Call logout API if token exists
      if (token.value) {
        await axios.post('/api/auth/logout', {}, {
          headers: {
            Authorization: `Bearer ${token.value}`
          }
        })
      }
    } catch (err) {
      console.warn('Logout API call failed:', err.message)
      // Continue with local logout even if API call fails
    } finally {
      clearAuthData()
    }
  }

  const refreshAuthToken = async () => {
    try {
      if (!refreshToken.value) {
        throw new Error('No refresh token available')
      }

      const response = await axios.post('/api/auth/refresh', {
        refresh_token: refreshToken.value
      })

      if (response.data && response.data.tokens) {
        setAuthData(response.data)
        return true
      } else {
        throw new Error('Invalid refresh response')
      }
    } catch (err) {
      console.error('Token refresh failed:', err.message)
      clearAuthData()
      return false
    }
  }

  const initializeAuth = async () => {
    try {
      // Check if we have stored auth data
      const storedUser = localStorage.getItem('user_data')
      if (storedUser && token.value) {
        user.value = JSON.parse(storedUser)
        
        // Verify token is still valid
        try {
          await axios.get('/api/auth/verify', {
            headers: {
              Authorization: `Bearer ${token.value}`
            }
          })
          return true
        } catch (err) {
          // Token is invalid, try to refresh
          const refreshed = await refreshAuthToken()
          return refreshed
        }
      }
      
      return false
    } catch (err) {
      console.error('Auth initialization failed:', err.message)
      clearAuthData()
      return false
    }
  }

  const updateProfile = async (profileData) => {
    try {
      isLoading.value = true
      error.value = null

      const response = await axios.put('/api/users/profile', profileData, {
        headers: {
          Authorization: `Bearer ${token.value}`
        }
      })

      if (response.data) {
        user.value = { ...user.value, ...response.data }
        localStorage.setItem('user_data', JSON.stringify(user.value))
        return { success: true, data: response.data }
      } else {
        throw new Error('Invalid response format')
      }
    } catch (err) {
      const errorMessage = err.response?.data?.error || err.message || 'Profile update failed'
      setError(errorMessage)
      return { success: false, error: errorMessage }
    } finally {
      isLoading.value = false
    }
  }

  const changePassword = async (passwordData) => {
    try {
      isLoading.value = true
      error.value = null

      const response = await axios.put('/api/users/password', passwordData, {
        headers: {
          Authorization: `Bearer ${token.value}`
        }
      })

      return { success: true, data: response.data }
    } catch (err) {
      const errorMessage = err.response?.data?.error || err.message || 'Password change failed'
      setError(errorMessage)
      return { success: false, error: errorMessage }
    } finally {
      isLoading.value = false
    }
  }

  const hasPermission = (permission) => {
    return userPermissions.value.includes(permission)
  }

  const hasRole = (role) => {
    return userRole.value === role
  }

  const hasAnyRole = (roles) => {
    return roles.includes(userRole.value)
  }

  // Setup axios interceptor for automatic token refresh
  const setupAxiosInterceptor = () => {
    axios.interceptors.response.use(
      (response) => response,
      async (error) => {
        if (error.response?.status === 401 && token.value) {
          // Token expired, try to refresh
          const refreshed = await refreshAuthToken()
          if (refreshed) {
            // Retry the original request
            const originalRequest = error.config
            originalRequest.headers.Authorization = `Bearer ${token.value}`
            return axios(originalRequest)
          } else {
            // Refresh failed, redirect to login
            clearAuthData()
            window.location.href = '/login'
          }
        }
        return Promise.reject(error)
      }
    )
  }

  // Initialize axios interceptor
  setupAxiosInterceptor()

  return {
    // State
    user,
    token,
    refreshToken,
    isLoading,
    error,
    
    // Getters
    isAuthenticated,
    userRole,
    userPermissions,
    isAdmin,
    isAnalyst,
    
    // Actions
    login,
    logout,
    refreshAuthToken,
    initializeAuth,
    updateProfile,
    changePassword,
    hasPermission,
    hasRole,
    hasAnyRole,
    setError,
    clearAuthData,
  }
})
