import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import basicSsl from '@vitejs/plugin-basic-ssl'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), basicSsl()],
  server: {
    // Bind to 0.0.0.0 so the dev server is reachable from other devices on
    // the same Wi-Fi (e.g. testing the camera flow on an actual phone).
    host: true,
    // HTTPS (self-signed, via basicSsl) is required for getUserMedia to work
    // on a non-localhost origin — browsers treat plain http://<lan-ip> as an
    // insecure context and don't expose the camera API there at all.
    https: true,
    // Proxy API calls to the backend server-side, so the browser only ever
    // talks to this https origin (no CORS, no https-page-calling-http
    // mixed-content block).
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
