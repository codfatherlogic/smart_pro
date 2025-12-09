<template>
  <!-- Android/Chrome Install Dialog -->
  <ion-modal :is-open="showInstallDialog" @did-dismiss="dismissDialog">
    <ion-header>
      <ion-toolbar>
        <ion-title>Install App</ion-title>
        <ion-buttons slot="end">
          <ion-button @click="dismissDialog">
            <ion-icon :icon="closeOutline" />
          </ion-button>
        </ion-buttons>
      </ion-toolbar>
    </ion-header>
    <ion-content class="ion-padding">
      <div class="install-prompt-content">
        <div class="install-icon-wrapper">
          <ion-icon :icon="downloadOutline" class="install-icon" />
        </div>
        <h2 class="install-title">Install {{ appName }}</h2>
        <p class="install-description">
          Get the app on your device for easy access & a better experience!
        </p>
        <div class="install-actions">
          <ion-button expand="block" @click="installApp">
            Install
          </ion-button>
          <ion-button expand="block" fill="clear" color="medium" @click="dismissDialog">
            Not Now
          </ion-button>
        </div>
      </div>
    </ion-content>
  </ion-modal>

  <!-- iOS Install Instructions Popover -->
  <ion-modal :is-open="showIOSPopover" @did-dismiss="dismissIOSPopover" :initial-breakpoint="0.4" :breakpoints="[0, 0.4]">
    <ion-content class="ion-padding">
      <div class="ios-install-content">
        <div class="install-icon-wrapper">
          <ion-icon :icon="shareOutline" class="install-icon ios-share" />
        </div>
        <h2 class="install-title">Install {{ appName }}</h2>
        <p class="install-description">
          To install this app on your iPhone/iPad:
        </p>
        <div class="ios-steps">
          <div class="ios-step">
            <span class="step-number">1</span>
            <span>Tap the <ion-icon :icon="shareOutline" class="inline-icon" /> Share button in Safari</span>
          </div>
          <div class="ios-step">
            <span class="step-number">2</span>
            <span>Scroll down and tap "Add to Home Screen"</span>
          </div>
          <div class="ios-step">
            <span class="step-number">3</span>
            <span>Tap "Add" to install</span>
          </div>
        </div>
        <ion-button expand="block" fill="clear" color="medium" @click="dismissIOSPopover" class="mt-4">
          Got it
        </ion-button>
      </div>
    </ion-content>
  </ion-modal>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from "vue"
import {
  IonModal,
  IonHeader,
  IonToolbar,
  IonTitle,
  IonButtons,
  IonButton,
  IonContent,
  IonIcon,
} from "@ionic/vue"
import { closeOutline, downloadOutline, shareOutline } from "ionicons/icons"
import { call } from "frappe-ui"

const appName = ref("Smart Pro")
const showInstallDialog = ref(false)
const showIOSPopover = ref(false)
let deferredPrompt = null

// Check if running in standalone mode (already installed)
function isStandalone() {
  return (
    window.matchMedia("(display-mode: standalone)").matches ||
    window.navigator.standalone === true
  )
}

// Check if iOS
function isIOS() {
  return /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream
}

// Check if Safari on iOS
function isIOSSafari() {
  const ua = navigator.userAgent
  return isIOS() && /Safari/.test(ua) && !/CriOS|FxiOS/.test(ua)
}

// Check if should show install prompt
function shouldShowPrompt() {
  // Don't show if already installed
  if (isStandalone()) return false

  // Check if user has dismissed the prompt before
  const dismissed = localStorage.getItem("smart-pro-install-dismissed")
  if (dismissed) {
    const dismissedTime = parseInt(dismissed, 10)
    // Show again after 7 days
    if (Date.now() - dismissedTime < 7 * 24 * 60 * 60 * 1000) {
      return false
    }
  }

  return true
}

function handleBeforeInstallPrompt(event) {
  // Prevent the default browser prompt
  event.preventDefault()

  // Store the event for later use
  deferredPrompt = event

  // Show our custom install dialog after a short delay
  if (shouldShowPrompt()) {
    setTimeout(() => {
      showInstallDialog.value = true
    }, 2000)
  }
}

async function installApp() {
  if (!deferredPrompt) return

  // Show the browser's install prompt
  deferredPrompt.prompt()

  // Wait for the user's response
  const { outcome } = await deferredPrompt.userChoice

  // Clear the deferred prompt
  deferredPrompt = null

  // Close our dialog
  showInstallDialog.value = false

  if (outcome === "accepted") {
    console.log("PWA installed successfully")
  }
}

function dismissDialog() {
  showInstallDialog.value = false
  localStorage.setItem("smart-pro-install-dismissed", Date.now().toString())
}

function dismissIOSPopover() {
  showIOSPopover.value = false
  localStorage.setItem("smart-pro-install-dismissed", Date.now().toString())
}

function showIOSInstallInstructions() {
  if (shouldShowPrompt() && isIOSSafari()) {
    setTimeout(() => {
      showIOSPopover.value = true
    }, 3000)
  }
}

async function loadAppName() {
  try {
    const settings = await call("smart_pro.smart_pro.api.projects.get_app_settings")
    if (settings && settings.app_name) {
      appName.value = settings.app_name
    }
  } catch (err) {
    console.error("Error loading app name:", err)
  }
}

onMounted(() => {
  loadAppName()

  // Listen for the beforeinstallprompt event (Android/Chrome)
  window.addEventListener("beforeinstallprompt", handleBeforeInstallPrompt)

  // For iOS Safari, show manual instructions
  if (isIOSSafari() && !isStandalone()) {
    showIOSInstallInstructions()
  }
})

onBeforeUnmount(() => {
  window.removeEventListener("beforeinstallprompt", handleBeforeInstallPrompt)
})
</script>

<style scoped>
.install-prompt-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 2rem 1rem;
}

.install-icon-wrapper {
  width: 80px;
  height: 80px;
  border-radius: 20px;
  background: linear-gradient(135deg, var(--ion-color-primary), var(--ion-color-primary-shade));
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 1.5rem;
  box-shadow: 0 8px 24px rgba(0, 137, 255, 0.3);
}

.install-icon {
  font-size: 2.5rem;
  color: white;
}

.install-icon.ios-share {
  font-size: 2rem;
}

.install-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--ion-text-color);
  margin: 0 0 0.75rem 0;
}

.install-description {
  font-size: 1rem;
  color: var(--ion-color-medium);
  margin: 0 0 2rem 0;
  max-width: 280px;
}

.install-actions {
  width: 100%;
  max-width: 300px;
}

.install-actions ion-button {
  margin-bottom: 0.5rem;
}

.ios-install-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 1rem;
}

.ios-steps {
  width: 100%;
  text-align: left;
  margin-top: 1rem;
}

.ios-step {
  display: flex;
  align-items: center;
  padding: 0.75rem 0;
  border-bottom: 1px solid var(--ion-color-light-shade);
  font-size: 0.95rem;
  color: var(--ion-text-color);
}

.ios-step:last-child {
  border-bottom: none;
}

.step-number {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background-color: var(--ion-color-primary);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 0.875rem;
  margin-right: 1rem;
  flex-shrink: 0;
}

.inline-icon {
  font-size: 1.1rem;
  vertical-align: middle;
  color: var(--ion-color-primary);
}
</style>
