<template>
  <div id="app" class="min-h-screen bg-gray-50">
    <div class="container mx-auto px-4 py-8">
      <h1 class="text-3xl font-bold text-center mb-8">Engineering Log Intelligence</h1>
      
      <!-- Simple test content -->
      <div class="bg-white rounded-lg shadow-lg p-6 mb-6">
        <h2 class="text-xl font-semibold mb-4">Vue.js Test</h2>
        <p>If you can see this, Vue.js is working!</p>
        <p>Current time: {{ currentTime }}</p>
        <button @click="updateTime" class="bg-blue-500 text-white px-4 py-2 rounded mt-4">
          Update Time
        </button>
      </div>
      
      <!-- Router View -->
      <div class="bg-white rounded-lg shadow-lg p-6">
        <h2 class="text-xl font-semibold mb-4">Router Test</h2>
        <router-view />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const currentTime = ref('')

const updateTime = () => {
  currentTime.value = new Date().toLocaleTimeString()
}

onMounted(() => {
  updateTime()
  setInterval(updateTime, 1000)
  console.log('✅ Simple App.vue mounted successfully')
})
</script>

<style>
/* Basic styles */
.container {
  max-width: 1200px;
  margin: 0 auto;
}
</style>