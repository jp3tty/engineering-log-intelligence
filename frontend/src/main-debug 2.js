// Debug version of main.js to test Vue.js
import { createApp, ref } from 'vue'

console.log('🚀 Debug main.js loading...')

const app = createApp({
  setup() {
    const message = ref('Vue.js is working!')
    const currentTime = ref('')
    
    const updateTime = () => {
      currentTime.value = new Date().toLocaleTimeString()
    }
    
    // Update time every second
    setInterval(updateTime, 1000)
    updateTime()
    
    return {
      message,
      currentTime,
      updateTime
    }
  },
  template: `
    <div style="padding: 20px; background: white; color: black; min-height: 100vh;">
      <h1>{{ message }}</h1>
      <p>Current time: {{ currentTime }}</p>
      <p>If you can see this, Vue.js is working correctly!</p>
      
      <div style="margin-top: 20px; padding: 20px; background: #f0f0f0; border-radius: 8px;">
        <h2>Log Distribution Bar Chart Test</h2>
        <p>This would show the bar chart when the full app loads.</p>
        <div style="background: white; padding: 15px; border-radius: 5px; margin-top: 10px;">
          <p><strong>Chart Data:</strong></p>
          <ul>
            <li>INFO: 60 logs (Green)</li>
            <li>WARN: 25 logs (Yellow)</li>
            <li>ERROR: 10 logs (Red)</li>
            <li>DEBUG: 4 logs (Gray)</li>
            <li>FATAL: 1 log (Purple)</li>
          </ul>
        </div>
      </div>
    </div>
  `,
  mounted() {
    console.log('✅ Debug Vue.js app mounted successfully!')
    // Hide the loading screen
    const loadingScreen = document.getElementById('loading-screen')
    if (loadingScreen) {
      loadingScreen.style.display = 'none'
    }
  }
})

console.log('🚀 Creating Vue app...')
app.mount('#app')
console.log('✅ Vue app mounted!')
