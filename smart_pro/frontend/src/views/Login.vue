<template>
  <ion-page>
    <ion-content
      :fullscreen="true"
      class="ion-padding login-content"
    >
      <div class="flex flex-col items-center justify-center min-h-full">
        <!-- Logo -->
        <div class="mb-8 text-center">
          <div
            class="w-20 h-20 rounded-2xl bg-primary-500 flex items-center justify-center mx-auto mb-4 logo-container"
          >
            <span class="text-3xl font-bold text-white">SP</span>
          </div>
          <h1 class="text-2xl font-bold title-text">
            Smart Pro
          </h1>
          <p class="subtitle-text">
            Project Management
          </p>
        </div>

        <!-- Login Form -->
        <div class="w-full max-w-sm">
          <div class="login-card p-6">
            <form @submit.prevent="handleLogin">
              <div class="mb-4">
                <ion-input
                  v-model="email"
                  type="email"
                  placeholder="Email"
                  fill="outline"
                  :disabled="loading"
                  class="login-input"
                  required
                />
              </div>

              <div class="mb-6">
                <ion-input
                  v-model="password"
                  type="password"
                  placeholder="Password"
                  fill="outline"
                  :disabled="loading"
                  class="login-input"
                  required
                />
              </div>

              <ion-button
                expand="block"
                type="submit"
                :disabled="loading || !email || !password"
                class="login-button"
              >
                <ion-spinner
                  v-if="loading"
                  name="crescent"
                  class="mr-2"
                />
                {{ loading ? "Signing in..." : "Sign In" }}
              </ion-button>
            </form>

            <div
              v-if="error"
              class="mt-4 p-3 error-message rounded-lg text-sm"
            >
              {{ error }}
            </div>

            <!-- Social Login Divider -->
            <div
              v-if="socialProviders.length > 0"
              class="divider-container my-6"
            >
              <div class="divider-line" />
              <span class="divider-text">or continue with</span>
              <div class="divider-line" />
            </div>

            <!-- Social Login Buttons -->
            <div
              v-if="socialProviders.length > 0"
              class="social-login-container"
            >
              <button
                v-for="provider in socialProviders"
                :key="provider.name"
                type="button"
                class="social-login-btn"
                :style="{ '--provider-color': provider.color }"
                @click="handleSocialLogin(provider)"
                :disabled="loading"
              >
                <ion-icon :icon="getProviderIcon(provider.icon)" />
                <span>{{ provider.label }}</span>
              </button>
            </div>

            <!-- Loading social providers -->
            <div
              v-if="loadingProviders"
              class="text-center py-4"
            >
              <ion-spinner name="dots" class="social-spinner" />
            </div>
          </div>

          <div class="text-center mt-6 text-sm">
            <a
              href="/login#forgot"
              class="forgot-link"
            >Forgot Password?</a>
          </div>

          <!-- Theme Toggle -->
          <div class="text-center mt-4">
            <ion-button
              fill="clear"
              size="small"
              @click="toggleDarkMode"
              class="theme-toggle-btn"
            >
              <ion-icon :icon="isDarkMode ? sunnyOutline : moonOutline" slot="start" />
              {{ isDarkMode ? 'Light Mode' : 'Dark Mode' }}
            </ion-button>
          </div>
        </div>
      </div>
    </ion-content>
  </ion-page>
</template>

<script setup>
import { ref, onMounted } from "vue"
import { useRouter } from "vue-router"
import { IonPage, IonContent, IonInput, IonButton, IonSpinner, IonIcon } from "@ionic/vue"
import {
  logoGoogle,
  logoGithub,
  logoFacebook,
  logoMicrosoft,
  globeOutline,
  moonOutline,
  sunnyOutline
} from "ionicons/icons"
import { call } from "frappe-ui"

const router = useRouter()

const email = ref("")
const password = ref("")
const loading = ref(false)
const error = ref("")
const socialProviders = ref([])
const loadingProviders = ref(true)
const isDarkMode = ref(false)

// Icon mapping for social providers
const iconMap = {
  "logo-google": logoGoogle,
  "logo-github": logoGithub,
  "logo-facebook": logoFacebook,
  "logo-microsoft": logoMicrosoft,
  "globe-outline": globeOutline
}

function getProviderIcon(iconName) {
  return iconMap[iconName] || globeOutline
}

async function loadSocialProviders() {
  loadingProviders.value = true
  try {
    // Pass the redirect URL so OAuth returns to our app after login
    const redirectTo = window.location.origin + "/smart-pro/home"
    const result = await call("smart_pro.smart_pro.api.projects.get_social_login_providers", {
      redirect_to: redirectTo
    })
    if (result && result.success) {
      socialProviders.value = result.providers || []
    }
  } catch (err) {
    console.error("Error loading social providers:", err)
  } finally {
    loadingProviders.value = false
  }
}

async function handleLogin() {
  if (!email.value || !password.value) return

  loading.value = true
  error.value = ""

  try {
    await call("login", {
      usr: email.value,
      pwd: password.value,
    })

    // Redirect to home on success
    router.push("/smart-pro/home")
  } catch (err) {
    console.error("Login error:", err)
    error.value = err.messages?.[0] || "Invalid email or password"
  } finally {
    loading.value = false
  }
}

function handleSocialLogin(provider) {
  // Redirect to the OAuth authorize URL (already contains all necessary parameters)
  window.location.href = provider.url
}

function initDarkMode() {
  // Check localStorage for user preference
  const savedTheme = localStorage.getItem("smart-pro-theme")
  if (savedTheme === "dark") {
    isDarkMode.value = true
    document.body.classList.add("dark")
    document.body.classList.remove("light")
  } else if (savedTheme === "light") {
    isDarkMode.value = false
    document.body.classList.add("light")
    document.body.classList.remove("dark")
  } else {
    // Check system preference
    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches
    isDarkMode.value = prefersDark
    if (prefersDark) {
      document.body.classList.add("dark")
    }
  }
}

function toggleDarkMode() {
  isDarkMode.value = !isDarkMode.value
  if (isDarkMode.value) {
    document.body.classList.add("dark")
    document.body.classList.remove("light")
    localStorage.setItem("smart-pro-theme", "dark")
  } else {
    document.body.classList.remove("dark")
    document.body.classList.add("light")
    localStorage.setItem("smart-pro-theme", "light")
  }
}

onMounted(() => {
  initDarkMode()
  loadSocialProviders()
})
</script>

<style scoped>
/* Light mode (default) */
.login-content {
  --background: linear-gradient(180deg, #f8fafc 0%, #e2e8f0 100%);
}

.title-text {
  color: #1e293b;
}

.subtitle-text {
  color: #64748b;
}

.login-card {
  background: white;
  border-radius: 1rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.login-input {
  --background: #f8fafc;
  --border-color: #e2e8f0;
  --color: #1e293b;
  --placeholder-color: #94a3b8;
}

.login-button {
  --background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  --box-shadow: 0 4px 14px rgba(59, 130, 246, 0.4);
  font-weight: 600;
}

.error-message {
  background-color: #fef2f2;
  color: #dc2626;
}

.forgot-link {
  color: #3b82f6;
  text-decoration: none;
}

.forgot-link:hover {
  text-decoration: underline;
}

.logo-container {
  box-shadow: 0 8px 24px rgba(59, 130, 246, 0.3);
}

/* Divider */
.divider-container {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.divider-line {
  flex: 1;
  height: 1px;
  background: #e2e8f0;
}

.divider-text {
  color: #94a3b8;
  font-size: 0.875rem;
  white-space: nowrap;
}

/* Social Login Buttons */
.social-login-container {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.social-login-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  padding: 0.875rem 1rem;
  border: 1px solid #e2e8f0;
  border-radius: 0.75rem;
  background: white;
  color: #374151;
  font-size: 0.9375rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.social-login-btn:hover {
  background: #f8fafc;
  border-color: var(--provider-color);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.social-login-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.social-login-btn ion-icon {
  font-size: 1.25rem;
  color: var(--provider-color);
}

.social-spinner {
  color: #64748b;
}

.theme-toggle-btn {
  --color: #64748b;
  font-size: 0.875rem;
}

/* Dark mode styles */
body.dark .login-content {
  --background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
}

body.dark .title-text {
  color: #f1f5f9;
}

body.dark .subtitle-text {
  color: #94a3b8;
}

body.dark .login-card {
  background: #1e293b;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

body.dark .login-input {
  --background: #0f172a;
  --border-color: #334155;
  --color: #f1f5f9;
  --placeholder-color: #64748b;
}

body.dark .error-message {
  background-color: rgba(220, 38, 38, 0.2);
  color: #fca5a5;
}

body.dark .divider-line {
  background: #334155;
}

body.dark .divider-text {
  color: #64748b;
}

body.dark .social-login-btn {
  background: #0f172a;
  border-color: #334155;
  color: #e2e8f0;
}

body.dark .social-login-btn:hover {
  background: #1e293b;
  border-color: var(--provider-color);
}

body.dark .social-spinner {
  color: #94a3b8;
}

body.dark .forgot-link {
  color: #60a5fa;
}

body.dark .theme-toggle-btn {
  --color: #94a3b8;
}

body.dark .logo-container {
  box-shadow: 0 8px 24px rgba(59, 130, 246, 0.2);
}
</style>
