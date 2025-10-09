// Ultra-simple test to debug Vite module issues
console.log('🚀 main-test.js loading...')

// Test if we can import Vue at all
try {
  const { createApp, ref } = await import('vue')
  console.log('✅ Vue import successful')
  
  const app = createApp({
    template: '<div style="padding: 20px; background: white; color: black;"><h1>Vue Test Works!</h1><p>Time: {{ time }}</p></div>',
    setup() {
      const time = ref(new Date().toLocaleTimeString())
      setInterval(() => time.value = new Date().toLocaleTimeString(), 1000)
      return { time }
    }
  })
  
  app.mount('#app')
  console.log('✅ Vue app mounted')
  
  // Hide loading screen
  const loadingScreen = document.getElementById('loading-screen')
  if (loadingScreen) {
    loadingScreen.style.display = 'none'
  }
  
} catch (error) {
  console.error('❌ Vue import failed:', error)
  
  // Fallback: show error message
  document.getElementById('app').innerHTML = `
    <div style="padding: 20px; background: red; color: white;">
      <h1>Vue Import Failed</h1>
      <p>Error: ${error.message}</p>
    </div>
  `
}