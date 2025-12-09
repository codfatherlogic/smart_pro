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
