import { defineConfig } from 'vite'

export default defineConfig({
  build: {
    outDir: '../frontend-vite-dist',
    emptyOutDir: true,
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
      }
    }
  }
})
