import { createApp } from "vue"
import { IonicVue } from "@ionic/vue"
import { setConfig, frappeRequest, resourcesPlugin } from "frappe-ui"
import App from "./App.vue"
import router from "./router"

// Ionic CSS
import "@ionic/vue/css/core.css"
import "@ionic/vue/css/normalize.css"
import "@ionic/vue/css/structure.css"
import "@ionic/vue/css/typography.css"
import "@ionic/vue/css/padding.css"
import "@ionic/vue/css/float-elements.css"
import "@ionic/vue/css/text-alignment.css"
import "@ionic/vue/css/text-transformation.css"
import "@ionic/vue/css/flex-utils.css"
import "@ionic/vue/css/display.css"

// App CSS
import "./theme/variables.css"
import "./main.css"

// Configure Frappe UI
setConfig("resourceFetcher", frappeRequest)

// Ensure requests to our API send cookies and CSRF header by default.
// This helps avoid CSRFTokenError when the library's internal fetch
// doesn't include credentials in some environments.
;(function patchFetch() {
  if (!window.fetch) return
  const originalFetch = window.fetch.bind(window)
  window.fetch = async function (input, init = {}) {
    try {
      const url = typeof input === "string" ? input : input.url

      // Only modify requests that target our backend API
      if (url && (url.startsWith("/api/") || url.startsWith("/api/method/"))) {
        init = init || {}
        // include credentials so cookies (session) are sent
        if (!init.credentials) init.credentials = "include"

        init.headers = init.headers || {}

        // preserve existing headers if they are a Headers instance
        if (init.headers instanceof Headers) {
          // add CSRF token header if available and this is not a GET
          const method = (init.method || 'GET').toUpperCase()
          if (method !== 'GET' && window.csrf_token && window.csrf_token !== "{{ csrf_token }}") {
            init.headers.set("X-Frappe-CSRF-Token", window.csrf_token)
          }
          if (!init.headers.has("X-Requested-With")) {
            init.headers.set("X-Requested-With", "XMLHttpRequest")
          }
        } else {
          // plain object
          const method = (init.method || 'GET').toUpperCase()
          if (method !== 'GET' && window.csrf_token && window.csrf_token !== "{{ csrf_token }}") {
            init.headers["X-Frappe-CSRF-Token"] = window.csrf_token
          }
          if (!init.headers["X-Requested-With"]) {
            init.headers["X-Requested-With"] = "XMLHttpRequest"
          }
        }
      }

      return await originalFetch(input, init)
    } catch (e) {
      return originalFetch(input, init)
    }
  }
})()

// Create Vue app
const app = createApp(App)

// Use plugins
app.use(IonicVue, {
  mode: "ios", // Use iOS style for consistent look
})
app.use(resourcesPlugin)
app.use(router)

// Provide global utilities
import dayjs from "dayjs"
import relativeTime from "dayjs/plugin/relativeTime"
import isToday from "dayjs/plugin/isToday"
import isTomorrow from "dayjs/plugin/isTomorrow"
dayjs.extend(relativeTime)
dayjs.extend(isToday)
dayjs.extend(isTomorrow)

app.provide("$dayjs", dayjs)

// Mount app after router is ready
router.isReady().then(() => {
  app.mount("#app")
})

// Register service worker for PWA
if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => {
    navigator.serviceWorker.register("/assets/smart_pro/frontend/sw.js").catch((error) => {
      console.log("Service worker registration failed:", error)
    })
  })
}
