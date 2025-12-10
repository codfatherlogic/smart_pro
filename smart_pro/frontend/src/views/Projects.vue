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
      <ion-toolbar>
        <ion-segment v-model="statusFilter" scrollable>
          <ion-segment-button value="all">
            <ion-label>All</ion-label>
          </ion-segment-button>
          <ion-segment-button value="active">
            <ion-label>Active</ion-label>
          </ion-segment-button>
          <ion-segment-button value="planning">
            <ion-label>Planning</ion-label>
          </ion-segment-button>
          <ion-segment-button value="completed">
            <ion-label>Completed</ion-label>
          </ion-segment-button>
          <ion-segment-button value="on-hold">
            <ion-label>On Hold</ion-label>
          </ion-segment-button>
        </ion-segment>
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
          {{ getEmptyMessage }}
        </div>
        <ion-button
          v-if="!searchQuery && statusFilter === 'all'"
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
  IonButtons,
  IonBackButton,
  IonIcon,
  IonSegment,
  IonSegmentButton,
  IonLabel,
  onIonViewWillEnter,
} from "@ionic/vue"
import { folderOutline } from "ionicons/icons"
import { createResource } from "frappe-ui"

const router = useRouter()
const $dayjs = inject("$dayjs")

const loading = ref(true)
const searchQuery = ref("")
const statusFilter = ref("all")
const projects = ref([])

const projectsResource = createResource({
  url: "smart_pro.smart_pro.api.projects.get_user_projects",
  auto: false,
})

const filteredProjects = computed(() => {
  let result = projects.value

  // Apply status filter
  if (statusFilter.value !== "all") {
    const statusMap = {
      "active": "Active",
      "planning": "Planning",
      "completed": "Completed",
      "on-hold": "On Hold",
      "cancelled": "Cancelled"
    }
    const targetStatus = statusMap[statusFilter.value]
    result = result.filter(p => p.status === targetStatus)
  }

  // Apply search filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(
      (p) =>
        (p.title || p.name).toLowerCase().includes(query) ||
        (p.status || "").toLowerCase().includes(query)
    )
  }

  return result
})

const getEmptyMessage = computed(() => {
  if (searchQuery.value) {
    return "Try a different search term"
  }
  if (statusFilter.value !== "all") {
    const filterLabels = {
      "active": "active",
      "planning": "planning",
      "completed": "completed",
      "on-hold": "on hold",
      "cancelled": "cancelled"
    }
    return `No ${filterLabels[statusFilter.value]} projects`
  }
  return "Create your first project"
})

// Cache timestamp to avoid unnecessary reloads
let lastLoadTime = 0
const CACHE_TTL = 30000 // 30 seconds

async function loadData(forceRefresh = false) {
  const now = Date.now()

  // Skip reload if data is fresh (unless forced)
  if (!forceRefresh && lastLoadTime && (now - lastLoadTime) < CACHE_TTL && projects.value.length > 0) {
    return
  }

  loading.value = projects.value.length === 0 // Only show loading on first load
  try {
    await projectsResource.fetch()
    projects.value = projectsResource.data || []
    lastLoadTime = now
  } catch (error) {
    console.error("Error loading projects:", error)
  } finally {
    loading.value = false
  }
}

function handleRefresh(event) {
  loadData(true).finally(() => {
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

onMounted(() => {
  loadData()
})

// Reload data when navigating back to this tab
onIonViewWillEnter(() => {
  loadData()
})
</script>
