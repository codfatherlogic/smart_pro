<template>
  <ion-page>
    <ion-header>
      <ion-toolbar>
        <ion-buttons slot="start">
          <ion-back-button default-href="/smart-pro/home" text="" />
        </ion-buttons>
        <ion-title>Projects</ion-title>
        <ion-buttons slot="end">
          <ion-button @click="createProject">
            <ion-icon :icon="addOutline" />
          </ion-button>
        </ion-buttons>
      </ion-toolbar>
      <ion-toolbar>
        <ion-searchbar
          v-model="searchQuery"
          placeholder="Search projects..."
          :debounce="300"
        />
      </ion-toolbar>
    </ion-header>

    <ion-content :fullscreen="true">
      <ion-refresher
        slot="fixed"
        @ion-refresh="handleRefresh"
      >
        <ion-refresher-content />
      </ion-refresher>

      <!-- Loading State -->
      <div
        v-if="loading"
        class="p-4"
      >
        <div
          v-for="i in 5"
          :key="i"
          class="app-card mb-4 p-4"
        >
          <div class="skeleton h-5 w-3/4 mb-2" />
          <div class="skeleton h-4 w-1/2 mb-2" />
          <div class="skeleton h-3 w-full" />
        </div>
      </div>

      <!-- Empty State -->
      <div
        v-else-if="filteredProjects.length === 0"
        class="empty-state h-full"
      >
        <ion-icon
          :icon="folderOutline"
          class="empty-state-icon"
        />
        <div class="empty-state-title">
          No projects found
        </div>
        <div class="empty-state-description">
          {{ searchQuery ? "Try a different search term" : "Create your first project" }}
        </div>
        <ion-button
          v-if="!searchQuery"
          class="mt-4"
          @click="createProject"
        >
          Create Project
        </ion-button>
      </div>

      <!-- Projects List -->
      <div
        v-else
        class="p-4"
      >
        <div
          v-for="project in filteredProjects"
          :key="project.name"
          class="app-card mb-4 p-4"
          @click="goToProject(project.name)"
        >
          <div class="flex justify-between items-start mb-2">
            <h3 class="font-semibold text-gray-800">
              {{ project.title || project.name }}
            </h3>
            <span :class="['status-badge', getStatusClass(project.status)]">
              {{ project.status }}
            </span>
          </div>
          <div class="text-sm text-gray-500 mb-3">
            {{ formatDate(project.start_date) }} - {{ formatDate(project.end_date) }}
          </div>
          <div
            v-if="project.budget_amount"
            class="text-sm text-gray-600"
          >
            Budget: {{ formatCurrency(project.budget_amount) }}
          </div>
        </div>
      </div>

      <!-- FAB -->
      <ion-fab
        slot="fixed"
        vertical="bottom"
        horizontal="end"
      >
        <ion-fab-button @click="createProject">
          <ion-icon :icon="addOutline" />
        </ion-fab-button>
      </ion-fab>
    </ion-content>
  </ion-page>
</template>

<script setup>
import { ref, computed, onMounted, inject } from "vue"
import { useRouter } from "vue-router"
import {
  IonPage,
  IonHeader,
  IonToolbar,
  IonTitle,
  IonContent,
  IonSearchbar,
  IonRefresher,
  IonRefresherContent,
  IonButton,
  IonButtons,
  IonBackButton,
  IonIcon,
  IonFab,
  IonFabButton,
} from "@ionic/vue"
import { addOutline, folderOutline } from "ionicons/icons"
import { createResource } from "frappe-ui"

const router = useRouter()
const $dayjs = inject("$dayjs")

const loading = ref(true)
const searchQuery = ref("")
const projects = ref([])

const projectsResource = createResource({
  url: "smart_pro.smart_pro.api.projects.get_user_projects",
  auto: false,
})

const filteredProjects = computed(() => {
  if (!searchQuery.value) return projects.value
  const query = searchQuery.value.toLowerCase()
  return projects.value.filter(
    (p) =>
      (p.title || p.name).toLowerCase().includes(query) ||
      (p.status || "").toLowerCase().includes(query)
  )
})

async function loadData() {
  loading.value = true
  try {
    await projectsResource.fetch()
    projects.value = projectsResource.data || []
  } catch (error) {
    console.error("Error loading projects:", error)
  } finally {
    loading.value = false
  }
}

function handleRefresh(event) {
  loadData().finally(() => {
    event.target.complete()
  })
}

function formatDate(dateStr) {
  if (!dateStr) return "-"
  return $dayjs(dateStr).format("MMM D, YYYY")
}

function formatCurrency(amount) {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
  }).format(amount)
}

function getStatusClass(status) {
  const map = {
    Active: "active",
    Planning: "planning",
    Completed: "completed",
    "On Hold": "on-hold",
    Cancelled: "cancelled",
  }
  return map[status] || ""
}

function goToProject(id) {
  router.push(`/smart-pro/project/${encodeURIComponent(id)}`)
}

function createProject() {
  router.push("/smart-pro/project/new")
}

onMounted(() => {
  loadData()
})
</script>
