import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    proxy: {
      // Dev: strip the production prefix and hit the local FastAPI server.
      '/api/main': {
        target: 'http://localhost:8000',
        rewrite: (path) => path.replace(/^\/api\/main/, ''),
      },
    },
  },
})
