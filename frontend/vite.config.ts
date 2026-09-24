import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Docker Compose define ADAN_API_URL=http://backend:8000; en local se usa el puerto de .claude/launch.json
const apiTarget = process.env.ADAN_API_URL || 'http://localhost:8020'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: apiTarget,
        changeOrigin: true,
      },
    },
  },
})
