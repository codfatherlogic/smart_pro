import path from "path"
import { fileURLToPath } from "url"
import fs from "fs"
import { defineConfig } from "vite"
import vue from "@vitejs/plugin-vue"
import { VitePWA } from "vite-plugin-pwa"
import Icons from "unplugin-icons/vite"

const __dirname = path.dirname(fileURLToPath(import.meta.url))

export default defineConfig({
  plugins: [
    vue(),
    Icons({
      compiler: "vue3",
      autoInstall: true,
    }),
    VitePWA({
      registerType: "autoUpdate",
      devOptions: {
        enabled: true,
      },
      workbox: {
        globPatterns: ["**/*.{js,css,html,ico,png,svg,woff,woff2}"],
        navigateFallback: "/assets/smart_pro/frontend/index.html",
        runtimeCaching: [
          {
            urlPattern: /^https:\/\/.*\/api\/.*/i,
            handler: "NetworkFirst",
            options: {
              cacheName: "api-cache",
              expiration: {
                maxEntries: 100,
                maxAgeSeconds: 60 * 60 * 24,
              },
            },
          },
        ],
      },
      manifest: {
        name: "Smart Pro",
        short_name: "SmartPro",
        description: "Project Management Mobile App",
        theme_color: "#0089FF",
        background_color: "#F4F5F6",
        display: "standalone",
        orientation: "portrait",
        scope: "/smart-pro",
        start_url: "/smart-pro",
        icons: [
          {
            src: "/assets/smart_pro/frontend/icons/icon-192x192.png",
            sizes: "192x192",
            type: "image/png",
          },
          {
            src: "/assets/smart_pro/frontend/icons/icon-512x512.png",
            sizes: "512x512",
            type: "image/png",
          },
          {
            src: "/assets/smart_pro/frontend/icons/icon-512x512.png",
            sizes: "512x512",
            type: "image/png",
            purpose: "maskable",
          },
        ],
      },
    }),
  ],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "src"),
    },
  },
  build: {
    outDir: "../public/frontend",
    emptyOutDir: true,
    target: "es2015",
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          "frappe-ui": ["frappe-ui"],
        },
      },
    },
  },
  optimizeDeps: {
    include: ["feather-icons", "showdown"],
  },
  server: {
    port: 8081,
    proxy: getProxyOptions(),
  },
})

function getProxyOptions() {
  const commonSiteConfig = getCommonSiteConfig()
  const webserverPort = commonSiteConfig?.webserver_port || 8000

  return {
    "^/(app|login|api|assets|files|private)": {
      target: `http://127.0.0.1:${webserverPort}`,
      ws: true,
      router: function (req) {
        const siteName = req.headers.host?.split(":")[0]
        return `http://${siteName}:${webserverPort}`
      },
    },
  }
}

function getCommonSiteConfig() {
  try {
    const benchPath = path.resolve(__dirname, "../../../..")
    const configPath = path.join(benchPath, "sites/common_site_config.json")

    if (fs.existsSync(configPath)) {
      const configContent = fs.readFileSync(configPath, "utf8")
      return JSON.parse(configContent)
    }
  } catch (e) {
    // Ignore errors
  }
  return {}
}
