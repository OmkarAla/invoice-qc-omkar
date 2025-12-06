import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'  // ✅ This is the real v4 Vite plugin

export default defineConfig({
  plugins: [react(), tailwindcss()],  // Add it here
})