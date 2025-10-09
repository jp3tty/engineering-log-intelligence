// Minimal main.js to test Vue.js loading
import { createApp, ref, onMounted } from 'vue'
import { createPinia } from 'pinia'

console.log('🚀 Minimal main.js loading...')

// Create a simple app first
const app = createApp({
  template: `
    <div style="padding: 20px; background: white; color: black; min-height: 100vh;">
      <h1>Minimal Vue.js Test</h1>
      <p>If you can see this, basic Vue.js is working!</p>
      <p>Current time: {{ currentTime }}</p>
      <button @click="updateTime">Update Time</button>
    </div>
  `,
  setup() {
    const currentTime = ref('')
    
    const updateTime = () => {
      currentTime.value = new Date().toLocaleTimeString()
    }
    
    onMounted(() => {
      updateTime()
      setInterval(updateTime, 1000)
      console.log('✅ Minimal Vue.js app mounted!')
      
      // Hide loading screen
      const loadingScreen = document.getElementById('loading-screen')
      if (loadingScreen) {
        loadingScreen.style.display = 'none'
      }
    })
    
    return {
      currentTime,
      updateTime
    }
  }
})

// Add Pinia
const pinia = createPinia()
app.use(pinia)

console.log('🚀 Mounting minimal app...')
app.mount('#app')
console.log('✅ Minimal app mounted!')