import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import selfsigned from 'selfsigned'
import os from 'node:os'

// Detects every non-internal IPv4 address this machine currently has, so the
// dev cert (and the "visit this URL on your phone" instructions) stay
// correct even if the Wi-Fi IP changes later — no hardcoded IP to go stale.
function getLanIPs() {
  const ips = []
  for (const iface of Object.values(os.networkInterfaces())) {
    for (const addr of iface ?? []) {
      if (addr.family === 'IPv4' && !addr.internal) ips.push(addr.address)
    }
  }
  return ips
}

// A cert must list every hostname/IP it needs to be valid for as the
// correctly-typed SAN entry — an IP address has to be an "IP Address" SAN
// (type 7), not a "DNS" SAN (type 2) string containing the IP. Get that
// wrong (as @vitejs/plugin-basic-ssl's public API does — it has no way to
// emit type 7 entries) and mobile browsers treat the cert as genuinely
// invalid for that address, not just self-signed, and refuse to let you
// override it at all.
async function generateDevCert() {
  const pems = await selfsigned.generate([{ name: 'commonName', value: 'localhost' }], {
    algorithm: 'sha256',
    extensions: [
      { name: 'basicConstraints', cA: true },
      { name: 'keyUsage', keyCertSign: true, digitalSignature: true, keyEncipherment: true },
      { name: 'extKeyUsage', serverAuth: true },
      {
        name: 'subjectAltName',
        altNames: [
          { type: 2, value: 'localhost' },
          { type: 7, ip: '127.0.0.1' },
          { type: 7, ip: '::1' },
          ...getLanIPs().map((ip) => ({ type: 7, ip })),
        ],
      },
    ],
  })
  return { cert: pems.cert, key: pems.private }
}

// https://vite.dev/config/
export default defineConfig(async () => ({
  plugins: [react()],
  server: {
    // Bind to 0.0.0.0 so the dev server is reachable from other devices on
    // the same Wi-Fi (e.g. testing the camera flow on an actual phone).
    host: true,
    // HTTPS is required for getUserMedia to work on a non-localhost origin —
    // browsers treat plain http://<lan-ip> as an insecure context and don't
    // expose the camera API there at all.
    https: await generateDevCert(),
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
}))
