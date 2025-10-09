<template>
  <div class="test-page">
    <div class="container">
      <h1>Vue.js Test Page</h1>
      <p>If you can see this, Vue.js is working correctly!</p>
      
      <div class="test-section">
        <h2>Authentication Test</h2>
        <p>User: {{ user?.name || 'Not loaded' }}</p>
        <p>Role: {{ user?.role || 'Not loaded' }}</p>
        <p>Authenticated: {{ isAuthenticated ? 'Yes' : 'No' }}</p>
      </div>
      
      <div class="test-section">
        <h2>Bar Chart Test</h2>
        <p>The Log Distribution bar chart should be visible on the dashboard.</p>
        <button @click="goToDashboard" class="btn-primary">
          Go to Dashboard
        </button>
      </div>
      
      <div class="test-section">
        <h2>System Status</h2>
        <p>Current time: {{ currentTime }}</p>
        <p>Page loaded: {{ pageLoaded }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const currentTime = ref('')
const pageLoaded = ref('')

const user = computed(() => authStore.user)
const isAuthenticated = computed(() => authStore.isAuthenticated)

const goToDashboard = () => {
  router.push('/dashboard')
}

const updateTime = () => {
  currentTime.value = new Date().toLocaleTimeString()
}

onMounted(() => {
  pageLoaded.value = new Date().toLocaleString()
  updateTime()
  setInterval(updateTime, 1000)
  
  console.log('✅ TestPage mounted successfully')
  console.log('User:', user.value)
  console.log('Authenticated:', isAuthenticated.value)
})
</script>

<style scoped>
.test-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.container {
  max-width: 800px;
  margin: 0 auto;
  background: white;
  border-radius: 12px;
  padding: 30px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
}

h1 {
  color: #333;
  text-align: center;
  margin-bottom: 20px;
}

.test-section {
  margin: 20px 0;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid #007bff;
}

.btn-primary {
  background: #007bff;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 5px;
  cursor: pointer;
  font-size: 16px;
}

.btn-primary:hover {
  background: #0056b3;
}

p {
  margin: 10px 0;
  font-size: 16px;
}
</style>
