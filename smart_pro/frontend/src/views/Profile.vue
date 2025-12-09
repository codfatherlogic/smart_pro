<template>
  <ion-page>
    <ion-header>
      <ion-toolbar>
        <ion-buttons slot="start">
          <ion-back-button default-href="/smart-pro/home" text="" />
        </ion-buttons>
        <ion-title>Profile</ion-title>
      </ion-toolbar>
    </ion-header>

    <ion-content :fullscreen="true">
      <div class="p-4">
        <!-- User Info Card -->
        <div class="app-card p-6 mb-6 text-center">
          <div
            class="w-20 h-20 rounded-full bg-primary-100 flex items-center justify-center mx-auto mb-4"
          >
            <span class="text-3xl font-bold text-primary-600">
              {{ userInitials }}
            </span>
          </div>
          <h2 class="text-xl font-semibold text-gray-800">
            {{ userName }}
          </h2>
          <p class="text-gray-500">
            {{ userEmail }}
          </p>
        </div>

        <!-- Stats -->
        <div class="grid grid-cols-3 gap-4 mb-6">
          <div class="app-card p-4 text-center">
            <div class="text-2xl font-bold text-primary-500">
              {{ stats.projects }}
            </div>
            <div class="text-xs text-gray-500">
              Projects
            </div>
          </div>
          <div class="app-card p-4 text-center">
            <div class="text-2xl font-bold text-orange-500">
              {{ stats.tasks }}
            </div>
            <div class="text-xs text-gray-500">
              Tasks
            </div>
          </div>
          <div class="app-card p-4 text-center">
            <div class="text-2xl font-bold text-green-500">
              {{ stats.completed }}
            </div>
            <div class="text-xs text-gray-500">
              Done
            </div>
          </div>
        </div>

        <!-- Menu Items -->
        <div class="app-card">
          <ion-list lines="full">
            <ion-item
              button
              @click="openSettings"
            >
              <template #start>
                <ion-icon :icon="settingsOutline" />
              </template>
              <ion-label>Settings</ion-label>
              <template #end>
                <ion-icon :icon="chevronForwardOutline" />
              </template>
            </ion-item>

            <ion-item
              button
              @click="openHelp"
            >
              <template #start>
                <ion-icon :icon="helpCircleOutline" />
              </template>
              <ion-label>Help & Support</ion-label>
              <template #end>
                <ion-icon :icon="chevronForwardOutline" />
              </template>
            </ion-item>

            <ion-item
              button
              @click="openAbout"
            >
              <template #start>
                <ion-icon :icon="informationCircleOutline" />
              </template>
              <ion-label>About</ion-label>
              <template #end>
                <ion-icon :icon="chevronForwardOutline" />
              </template>
            </ion-item>

            <ion-item
              button
              class="text-red-500"
              @click="logout"
            >
              <ion-icon
                slot="start"
                :icon="logOutOutline"
                color="danger"
              />
              <ion-label color="danger">
                Logout
              </ion-label>
            </ion-item>
          </ion-list>
        </div>

        <!-- App Version -->
        <div class="text-center mt-6 text-sm text-gray-400">
          Smart Pro v1.0.0
        </div>
      </div>
    </ion-content>
  </ion-page>
</template>

<script setup>
import { ref, computed, onMounted } from "vue"
import { useRouter } from "vue-router"
import {
  IonPage,
  IonHeader,
  IonToolbar,
  IonTitle,
  IonContent,
  IonList,
  IonItem,
  IonLabel,
  IonIcon,
  IonButtons,
  IonBackButton,
  alertController,
  loadingController,
} from "@ionic/vue"
import {
  settingsOutline,
  helpCircleOutline,
  informationCircleOutline,
  logOutOutline,
  chevronForwardOutline,
} from "ionicons/icons"
import { createResource, call } from "frappe-ui"

const router = useRouter()

const userName = ref("")
const userEmail = ref("")
const stats = ref({ projects: 0, tasks: 0, completed: 0 })

const userInitials = computed(() => {
  if (!userName.value) return "?"
  return userName.value
    .split(" ")
    .map((n) => n[0])
    .join("")
    .toUpperCase()
    .slice(0, 2)
})

const userResource = createResource({
  url: "frappe.auth.get_logged_user",
  auto: false,
})

const projectsResource = createResource({
  url: "smart_pro.smart_pro.api.projects.get_user_projects",
  auto: false,
})

const tasksResource = createResource({
  url: "smart_pro.smart_pro.api.projects.get_user_tasks",
  auto: false,
})

async function loadUserData() {
  try {
    await userResource.fetch()
    userEmail.value = userResource.data || ""

    // Get full name
    if (userEmail.value) {
      const userDoc = await call("frappe.client.get_value", {
        doctype: "User",
        filters: { name: userEmail.value },
        fieldname: "full_name",
      })
      userName.value = userDoc?.full_name || userEmail.value
    }

    // Load stats
    await Promise.all([projectsResource.fetch(), tasksResource.fetch()])

    const projects = projectsResource.data || []
    const tasks = tasksResource.data || []

    stats.value = {
      projects: projects.length,
      tasks: tasks.length,
      completed: tasks.filter((t) => t.status === "Completed").length,
    }
  } catch (error) {
    console.error("Error loading user data:", error)
  }
}

async function openSettings() {
  const alert = await alertController.create({
    header: "Settings",
    message: "Settings will be available in a future update.",
    buttons: ["OK"],
  })
  await alert.present()
}

async function openHelp() {
  const alert = await alertController.create({
    header: "Help & Support",
    message: "For support, please contact your administrator.",
    buttons: ["OK"],
  })
  await alert.present()
}

async function openAbout() {
  const alert = await alertController.create({
    header: "About Smart Pro",
    message: "Smart Pro is a project management application built on Frappe Framework.",
    buttons: ["OK"],
  })
  await alert.present()
}

async function logout() {
  const alert = await alertController.create({
    header: "Logout",
    message: "Are you sure you want to logout?",
    buttons: [
      {
        text: "Cancel",
        role: "cancel",
      },
      {
        text: "Logout",
        role: "destructive",
        handler: async () => {
          const loading = await loadingController.create({
            message: "Logging out...",
          })
          await loading.present()

          try {
            // Call Frappe logout API
            await fetch("/api/method/logout", {
              method: "POST",
              headers: {
                "Content-Type": "application/json",
              },
            })
            // Clear any local storage
            localStorage.removeItem("user_id")
            sessionStorage.clear()
            // Redirect to login page
            window.location.href = "/smart-pro/login"
          } catch (error) {
            console.error("Logout error:", error)
            // Force redirect even if logout fails
            window.location.href = "/smart-pro/login"
          } finally {
            await loading.dismiss()
          }
        },
      },
    ],
  })
  await alert.present()
}

onMounted(() => {
  loadUserData()
})
</script>
