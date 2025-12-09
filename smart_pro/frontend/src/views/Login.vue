<template>
  <ion-page>
    <ion-content
      :fullscreen="true"
      class="ion-padding"
    >
      <div class="flex flex-col items-center justify-center min-h-full">
        <!-- Logo -->
        <div class="mb-8 text-center">
          <div
            class="w-20 h-20 rounded-2xl bg-primary-500 flex items-center justify-center mx-auto mb-4"
          >
            <span class="text-3xl font-bold text-white">SP</span>
          </div>
          <h1 class="text-2xl font-bold text-gray-800">
            Smart Pro
          </h1>
          <p class="text-gray-500">
            Project Management
          </p>
        </div>

        <!-- Login Form -->
        <div class="w-full max-w-sm">
          <div class="app-card p-6">
            <form @submit.prevent="handleLogin">
              <div class="mb-4">
                <ion-input
                  v-model="email"
                  type="email"
                  placeholder="Email"
                  fill="outline"
                  :disabled="loading"
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
                  required
                />
              </div>

              <ion-button
                expand="block"
                type="submit"
                :disabled="loading || !email || !password"
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
              class="mt-4 p-3 bg-red-50 text-red-600 rounded-lg text-sm"
            >
              {{ error }}
            </div>
          </div>

          <div class="text-center mt-6 text-sm text-gray-500">
            <a
              href="/login#forgot"
              class="text-primary-500"
            >Forgot Password?</a>
          </div>
        </div>
      </div>
    </ion-content>
  </ion-page>
</template>

<script setup>
import { ref } from "vue"
import { useRouter } from "vue-router"
import { IonPage, IonContent, IonInput, IonButton, IonSpinner } from "@ionic/vue"
import { call } from "frappe-ui"

const router = useRouter()

const email = ref("")
const password = ref("")
const loading = ref(false)
const error = ref("")

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
</script>

<style scoped>
ion-content {
  --background: linear-gradient(180deg, #f8fafc 0%, #e2e8f0 100%);
}
</style>
