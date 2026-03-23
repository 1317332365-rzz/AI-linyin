import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        // Export can run for several minutes; avoid proxy cutting the connection early.
        timeout: 30 * 60 * 1000,
        proxyTimeout: 30 * 60 * 1000,
      }
    }
  }
})
