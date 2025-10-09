// Simple Vue.js test to see if the app loads
import { createApp } from 'vue'

const app = createApp({
  template: `
    <div style="padding: 20px; background: white; color: black; min-height: 100vh;">
      <h1>Vue.js Test - Engineering Log Intelligence</h1>
      <p>If you can see this, Vue.js is working!</p>
      <p>Current time: {{ currentTime }}</p>
      <div style="margin-top: 20px;">
        <h2>Log Distribution Bar Chart Test</h2>
        <p>This would show the bar chart when the full app loads.</p>
        <div style="background: #f0f0f0; padding: 20px; border-radius: 8px; margin-top: 10px;">
          <p><strong>Chart Data:</strong></p>
          <ul>
            <li>INFO: 60 logs</li>
            <li>WARN: 25 logs</li>
            <li>ERROR: 10 logs</li>
            <li>DEBUG: 4 logs</li>
            <li>FATAL: 1 log</li>
          </ul>
        </div>
      </div>
    </div>
  `,
  data() {
    return {
      currentTime: new Date().toLocaleTimeString()
    }
  },
  mounted() {
    console.log('✅ Simple Vue.js test app mounted successfully!')
    // Hide the loading screen
    const loadingScreen = document.getElementById('loading-screen')
    if (loadingScreen) {
      loadingScreen.style.display = 'none'
    }
  }
})

app.mount('#app')
