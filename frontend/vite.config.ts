import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Docker Compose define ADAN_API_URL=http://backend:8000; en local se usa el puerto de .claude/launch.json
const apiTarget = process.env.ADAN_API_URL || 'http://localhost:8020'
// Demos temporales: túneles gratuitos (Cloudflare Quick Tunnel, ngrok, Pinggy, localhost.run) al servidor de desarrollo.
// ADAN_ALLOWED_HOSTS agrega otros dominios separados por comas.
const allowedHosts = ['localhost', '.trycloudflare.com', '.ngrok-free.app', '.pinggy.link', '.pinggy.online', '.lhr.life',
  ...(process.env.ADAN_ALLOWED_HOSTS ?? '').split(',').map((h) => h.trim()).filter(Boolean)]

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    allowedHosts,
    proxy: {
      '/api': {
        target: apiTarget,
        changeOrigin: true,
      },
    },
  },
})
