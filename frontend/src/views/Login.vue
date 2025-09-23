<template>
  <div class="min-h-screen bg-gradient-to-br from-primary-50 to-primary-100 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8">
      <!-- Header -->
      <div class="text-center">
        <div class="flex justify-center">
          <div class="w-16 h-16 bg-gradient-to-r from-primary-500 to-primary-700 rounded-2xl flex items-center justify-center">
            <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
          </div>
        </div>
        <h2 class="mt-6 text-3xl font-bold text-gray-900">
          Welcome back
        </h2>
        <p class="mt-2 text-sm text-gray-600">
          Sign in to your Engineering Log Intelligence account
        </p>
      </div>

      <!-- Login Form -->
      <form @submit.prevent="handleLogin" class="mt-8 space-y-6">
        <div class="space-y-4">
          <!-- Username Field -->
          <div>
            <label for="username" class="block text-sm font-medium text-gray-700">
              Username
            </label>
            <div class="mt-1">
              <input
                id="username"
                v-model="form.username"
                type="text"
                required
                class="input"
                :class="{ 'input-error': errors.username }"
                placeholder="Enter your username"
              />
              <p v-if="errors.username" class="mt-1 text-sm text-danger-600">
                {{ errors.username }}
              </p>
            </div>
          </div>

          <!-- Password Field -->
          <div>
            <label for="password" class="block text-sm font-medium text-gray-700">
              Password
            </label>
            <div class="mt-1">
              <input
                id="password"
                v-model="form.password"
                type="password"
                required
                class="input"
                :class="{ 'input-error': errors.password }"
                placeholder="Enter your password"
              />
              <p v-if="errors.password" class="mt-1 text-sm text-danger-600">
                {{ errors.password }}
              </p>
            </div>
          </div>
        </div>

        <!-- Remember Me & Forgot Password -->
        <div class="flex items-center justify-between">
          <div class="flex items-center">
            <input
              id="remember-me"
              v-model="form.rememberMe"
              type="checkbox"
              class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
            />
            <label for="remember-me" class="ml-2 block text-sm text-gray-700">
              Remember me
            </label>
          </div>

          <div class="text-sm">
            <a href="#" class="font-medium text-primary-600 hover:text-primary-500">
              Forgot your password?
            </a>
          </div>
        </div>

        <!-- Error Message -->
        <div v-if="error" class="bg-danger-50 border border-danger-200 rounded-md p-4">
          <div class="flex">
            <div class="flex-shrink-0">
              <svg class="h-5 w-5 text-danger-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div class="ml-3">
              <p class="text-sm text-danger-800">{{ error }}</p>
            </div>
          </div>
        </div>

        <!-- Submit Button -->
        <div>
          <button
            type="submit"
            :disabled="isLoading"
            class="btn btn-primary w-full"
          >
            <svg v-if="isLoading" class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            {{ isLoading ? 'Signing in...' : 'Sign in' }}
          </button>
        </div>

        <!-- Demo Credentials -->
        <div class="bg-gray-50 rounded-md p-4">
          <h4 class="text-sm font-medium text-gray-900 mb-2">Demo Credentials</h4>
          <div class="text-xs text-gray-600 space-y-1">
            <p><strong>Admin:</strong> admin / password123</p>
            <p><strong>Analyst:</strong> analyst / password123</p>
            <p><strong>User:</strong> user / password123</p>
          </div>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
/**
 * Login View Component
 * ===================
 * 
 * This component handles user authentication and login.
 * It provides a form for users to enter their credentials.
 * 
 * For beginners: This is the login page where users enter their
 * username and password to access the application.
 * 
 * Author: Engineering Log Intelligence Team
 * Date: September 22, 2025
 */

import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

export default {
  name: 'Login',
  setup() {
    const router = useRouter()
    const authStore = useAuthStore()

    // Form data
    const form = reactive({
      username: '',
      password: '',
      rememberMe: false,
    })

    // State
    const isLoading = ref(false)
    const error = ref('')
    const errors = reactive({
      username: '',
      password: '',
    })

    // Methods
    const validateForm = () => {
      errors.username = ''
      errors.password = ''

      if (!form.username.trim()) {
        errors.username = 'Username is required'
        return false
      }

      if (!form.password) {
        errors.password = 'Password is required'
        return false
      }

      if (form.password.length < 6) {
        errors.password = 'Password must be at least 6 characters'
        return false
      }

      return true
    }

    const handleLogin = async () => {
      if (!validateForm()) {
        return
      }

      isLoading.value = true
      error.value = ''

      try {
        const result = await authStore.login({
          username: form.username.trim(),
          password: form.password,
        })

        if (result.success) {
          // Redirect to dashboard or intended page
          const redirectTo = router.currentRoute.value.query.redirect || '/dashboard'
          router.push(redirectTo)
        } else {
          error.value = result.error || 'Login failed'
        }
      } catch (err) {
        error.value = 'An unexpected error occurred. Please try again.'
        console.error('Login error:', err)
      } finally {
        isLoading.value = false
      }
    }

    return {
      // Data
      form,
      isLoading,
      error,
      errors,
      
      // Methods
      handleLogin,
    }
  },
}
</script>
