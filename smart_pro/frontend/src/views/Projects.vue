<template>
  <ion-page>
    <ion-header>
      <ion-toolbar>
        <ion-buttons slot="start">
          <ion-back-button default-href="/smart-pro/home" text="" />
        </ion-buttons>
        <ion-title>Projects</ion-title>
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
import { ref, computed, onMounted, inject, watch } from "vue"
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
import { createResource, call } from "frappe-ui"
import { usePermissions } from "@/composables/usePermissions"

const router = useRouter()
const $dayjs = inject("$dayjs")
const { fetchPermissions, hasFullAccess } = usePermissions()

const loading = ref(true)
const searchQuery = ref("")
const statusFilter = ref("active")
const projects = ref([])
const completedProjects = ref([])
let completedLoaded = false

const projectsResource = createResource({
  url: "smart_pro.smart_pro.api.projects.get_user_projects",
  auto: false,
})

// Separate resource for completed projects (only loaded when needed)
const completedProjectsResource = createResource({
  url: "smart_pro.smart_pro.api.projects.get_user_projects",
  auto: false,
})

const filteredProjects = computed(() => {
  // For completed filter, use completedProjects; otherwise use regular projects
  let result = statusFilter.value === "completed" ? completedProjects.value : projects.value

  // Apply status filter (except for completed which is already filtered)
  if (statusFilter.value !== "all" && statusFilter.value !== "completed") {
    const statusMap = {
      "active": "Active",
      "planning": "Planning",
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
    // Fetch permissions first
    await fetchPermissions()

    // For full access users, get all projects; otherwise get user's projects
    if (hasFullAccess.value) {
      const result = await call("smart_pro.smart_pro.api.projects.get_all_projects")
      projects.value = (result || []).filter(p => p.status !== "Completed")
    } else {
      // Load active projects (excludes completed by default)
      await projectsResource.fetch()
      projects.value = projectsResource.data || []
    }
    lastLoadTime = now
  } catch (error) {
    console.error("Error loading projects:", error)
  } finally {
    loading.value = false
  }
}

// Load completed projects only when user clicks on Completed tab
async function loadCompletedProjects() {
  if (completedLoaded) return

  loading.value = true
  try {
    // For full access users, get all completed projects
    if (hasFullAccess.value) {
      const result = await call("smart_pro.smart_pro.api.projects.get_all_projects")
      completedProjects.value = (result || []).filter(p => p.status === "Completed")
    } else {
      await completedProjectsResource.fetch({ include_completed: "true" })
      const allProjects = completedProjectsResource.data || []
      // Filter to only show completed projects
      completedProjects.value = allProjects.filter(p => p.status === "Completed")
    }
    completedLoaded = true
  } catch (error) {
    console.error("Error loading completed projects:", error)
  } finally {
    loading.value = false
  }
}

// Watch for filter changes to load completed projects when needed
watch(statusFilter, (newValue) => {
  if (newValue === "completed" && !completedLoaded) {
    loadCompletedProjects()
  }
})

function handleRefresh(event) {
  // Reset completed cache on refresh
  completedLoaded = false
  completedProjects.value = []

  loadData(true).finally(() => {
    // If on completed tab, reload completed projects too
    if (statusFilter.value === "completed") {
      loadCompletedProjects().finally(() => {
        event.target.complete()
      })
    } else {
      event.target.complete()
    }
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
