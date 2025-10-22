const { defineConfig } = require('vite')
const vue = require('@vitejs/plugin-vue')
const { resolve } = require('path')

// https://vitejs.dev/config/
module.exports = defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
      'vue': 'vue/dist/vue.esm-bundler.js',
    },
  },
  server: {
    port: 3001,
    proxy: {
      '/api': {
        target: 'https://engineeringlogintelligence.vercel.app',
        changeOrigin: true,
        secure: true,
      },
    },
  },
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    sourcemap: true,
  },
})
