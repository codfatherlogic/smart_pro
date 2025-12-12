<template>
  <ion-page>
    <ion-header>
      <ion-toolbar>
        <ion-title>{{ appName }}</ion-title>
        <ion-buttons slot="end">
          <ion-button @click="toggleDarkMode" class="theme-btn">
            <ion-icon :icon="isDarkMode ? sunnyOutline : moonOutline" />
          </ion-button>
          <ion-button @click="goToNotifications" class="notification-btn">
            <ion-icon :icon="notificationsOutline" />
            <span
              v-if="notificationCount > 0"
              class="notification-badge"
            >
              {{ notificationCount > 9 ? '9+' : notificationCount }}
            </span>
          </ion-button>
        </ion-buttons>
      </ion-toolbar>
    </ion-header>

    <ion-content :fullscreen="true">
      <ion-refresher slot="fixed" @ion-refresh="handleRefresh">
        <ion-refresher-content />
      </ion-refresher>

      <div class="p-4">
        <!-- Welcome Section -->
        <div class="mb-6">
          <h1 class="text-2xl font-bold text-gray-800">
            Welcome back!
          </h1>
          <p class="text-gray-500">
            Here's your overview
          </p>
        </div>

        <!-- Stats Cards -->
        <div class="grid grid-cols-2 gap-4 mb-6">
          <div class="app-card p-4">
            <div class="text-3xl font-bold text-primary-500">
              {{ stats.projects }}
            </div>
            <div class="text-sm text-gray-500">
              Active Projects
            </div>
          </div>
          <div class="app-card p-4">
            <div class="text-3xl font-bold text-orange-500">
              {{ stats.tasks }}
            </div>
            <div class="text-sm text-gray-500">
              Pending Tasks
            </div>
          </div>
        </div>

        <!-- Recent Projects -->
        <div class="app-card mb-6">
          <div class="app-card-header flex justify-between items-center">
            <span>Recent Projects</span>
            <ion-button
              fill="clear"
              size="small"
              @click="router.push('/smart-pro/projects')"
            >
              See All
            </ion-button>
          </div>
          <div
            v-if="loading"
            class="p-4"
          >
            <div class="skeleton h-16 mb-3" />
            <div class="skeleton h-16 mb-3" />
          </div>
          <div
            v-else-if="projects.length === 0"
            class="empty-state py-8"
          >
            <div class="empty-state-title">
              No projects yet
            </div>
            <div class="empty-state-description">
              Create your first project to get started
            </div>
          </div>
          <div v-else>
            <div
              v-for="project in projects.slice(0, 3)"
              :key="project.name"
              class="app-list-item"
              @click="goToProject(project.name)"
            >
              <div class="flex-1">
                <div class="font-medium text-gray-800">
                  {{ project.title || project.name }}
                </div>
                <div class="text-sm text-gray-500">
                  {{ formatDate(project.end_date) }}
                </div>
              </div>
              <span :class="['status-badge', getStatusClass(project.status)]">
                {{ project.status }}
              </span>
            </div>
          </div>
        </div>

        <!-- Connections Dashboard Link -->
        <div
          class="app-card mb-6 p-4 cursor-pointer"
          @click="router.push('/smart-pro/connections')"
        >
          <div class="flex items-center justify-between">
            <div class="flex items-center">
              <div class="w-10 h-10 rounded-full bg-purple-100 flex items-center justify-center mr-3">
                <ion-icon :icon="gitNetworkOutline" class="text-xl text-purple-600" />
              </div>
              <div>
                <div class="font-semibold text-gray-800">Connections Dashboard</div>
                <div class="text-sm text-gray-500">View all doctypes & relationships</div>
              </div>
            </div>
            <ion-icon :icon="chevronForwardOutline" class="text-gray-400" />
          </div>
        </div>

        <!-- Insights Dashboard (Full Access Users Only) -->
        <div
          v-if="hasFullAccess"
          class="app-card mb-6"
        >
          <div class="app-card-header flex items-center">
            <ion-icon :icon="analyticsOutline" class="text-lg text-blue-400 mr-2" />
            <span>Insights Dashboard</span>
          </div>
          <div class="p-4">
            <!-- Project Status Overview -->
            <div class="mb-4">
              <div class="text-sm font-medium text-gray-600 dark:text-gray-300 mb-2">Project Status</div>
              <div class="grid grid-cols-2 gap-2">
                <div class="insight-card insight-card-green">
                  <div class="text-xl font-bold">{{ insights.activeProjects }}</div>
                  <div class="text-xs opacity-80">Active</div>
                </div>
                <div class="insight-card insight-card-blue">
                  <div class="text-xl font-bold">{{ insights.planningProjects }}</div>
                  <div class="text-xs opacity-80">Planning</div>
                </div>
                <div class="insight-card insight-card-yellow">
                  <div class="text-xl font-bold">{{ insights.onHoldProjects }}</div>
                  <div class="text-xs opacity-80">On Hold</div>
                </div>
                <div class="insight-card insight-card-gray">
                  <div class="text-xl font-bold">{{ insights.completedProjects }}</div>
                  <div class="text-xs opacity-80">Completed</div>
                </div>
              </div>
            </div>

            <!-- Task Overview -->
            <div class="mb-4">
              <div class="text-sm font-medium text-gray-600 dark:text-gray-300 mb-2">Task Overview</div>
              <div class="grid grid-cols-3 gap-2">
                <div class="insight-card insight-card-blue">
                  <div class="text-xl font-bold">{{ insights.openTasks }}</div>
                  <div class="text-xs opacity-80">Open</div>
                </div>
                <div class="insight-card insight-card-orange">
                  <div class="text-xl font-bold">{{ insights.workingTasks }}</div>
                  <div class="text-xs opacity-80">Working</div>
                </div>
                <div class="insight-card insight-card-green">
                  <div class="text-xl font-bold">{{ insights.completedTasks }}</div>
                  <div class="text-xs opacity-80">Done</div>
                </div>
              </div>
            </div>

            <!-- Summary -->
            <div>
              <div class="text-sm font-medium text-gray-600 dark:text-gray-300 mb-2">Summary</div>
              <div class="space-y-2">
                <div class="summary-row">
                  <span class="text-sm text-gray-600 dark:text-gray-400">Total Projects</span>
                  <span class="font-semibold text-gray-800 dark:text-gray-200">{{ insights.totalProjects }}</span>
                </div>
                <div class="summary-row">
                  <span class="text-sm text-gray-600 dark:text-gray-400">Total Tasks</span>
                  <span class="font-semibold text-gray-800 dark:text-gray-200">{{ insights.totalTasks }}</span>
                </div>
                <div class="summary-row">
                  <span class="text-sm text-gray-600 dark:text-gray-400">Completion Rate</span>
                  <span class="font-semibold text-green-500">{{ insights.completionRate }}%</span>
                </div>
                <div class="summary-row summary-row-last">
                  <span class="text-sm text-gray-600 dark:text-gray-400">Overdue Tasks</span>
                  <span :class="['font-semibold', insights.overdueTasks > 0 ? 'text-red-500' : 'text-gray-800 dark:text-gray-200']">
                    {{ insights.overdueTasks }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- My Tasks -->
        <div class="app-card">
          <div class="app-card-header flex justify-between items-center">
            <span>My Tasks</span>
            <ion-button
              fill="clear"
              size="small"
              @click="router.push('/smart-pro/tasks')"
            >
              See All
            </ion-button>
          </div>
          <div
            v-if="loading"
            class="p-4"
          >
            <div class="skeleton h-16 mb-3" />
            <div class="skeleton h-16 mb-3" />
          </div>
          <div
            v-else-if="tasks.length === 0"
            class="empty-state py-8"
          >
            <div class="empty-state-title">
              No tasks assigned
            </div>
            <div class="empty-state-description">
              Tasks assigned to you will appear here
            </div>
          </div>
          <div v-else>
            <div
              v-for="task in tasks.slice(0, 3)"
              :key="task.name"
              class="app-list-item"
              @click="goToTask(task.name)"
            >
              <div class="flex-1">
                <div class="font-medium text-gray-800">
                  {{ task.title || task.name }}
                </div>
                <div class="text-sm text-gray-500">
                  Due: {{ formatDate(task.due_date) }}
                </div>
                <div class="progress-bar mt-2">
                  <div
                    class="progress-bar-fill"
                    :style="{ width: (task.progress || 0) + '%' }"
                  />
                </div>
              </div>
              <span :class="['status-badge', getStatusClass(task.status)]">
                {{ task.status }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </ion-content>
  </ion-page>
</template>

<script setup>
import { ref, onMounted, inject } from "vue"
import { onIonViewWillEnter } from "@ionic/vue"
import { useRouter } from "vue-router"
import {
  IonPage,
  IonHeader,
  IonToolbar,
  IonTitle,
  IonContent,
  IonRefresher,
  IonRefresherContent,
  IonButton,
  IonButtons,
  IonIcon,
} from "@ionic/vue"
import { gitNetworkOutline, chevronForwardOutline, notificationsOutline, moonOutline, sunnyOutline, analyticsOutline } from "ionicons/icons"
import { createResource, call } from "frappe-ui"
import { usePermissions } from "@/composables/usePermissions"

const router = useRouter()
const $dayjs = inject("$dayjs")
const { fetchPermissions, hasFullAccess } = usePermissions()

const loading = ref(true)
const projects = ref([])
const tasks = ref([])
const stats = ref({ projects: 0, tasks: 0 })
const insights = ref({
  totalProjects: 0,
  activeProjects: 0,
  planningProjects: 0,
  onHoldProjects: 0,
  completedProjects: 0,
  totalTasks: 0,
  openTasks: 0,
  workingTasks: 0,
  completedTasks: 0,
  overdueTasks: 0,
  completionRate: 0,
})
const notificationCount = ref(0)
const appName = ref("Smart Pro")
const isDarkMode = ref(false)

const projectsResource = createResource({
  url: "smart_pro.smart_pro.api.projects.get_user_projects",
  auto: false,
})

const tasksResource = createResource({
  url: "smart_pro.smart_pro.api.projects.get_user_tasks",
  auto: false,
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
    console.log("Home.vue - hasFullAccess:", hasFullAccess.value)

    // For full access users, get all data; otherwise get user's data
    if (hasFullAccess.value) {
      try {
        const [allProjects, allTasks] = await Promise.all([
          call("smart_pro.smart_pro.api.projects.get_all_projects"),
          call("smart_pro.smart_pro.api.projects.get_all_tasks"),
        ])
        projects.value = allProjects || []
        tasks.value = allTasks || []
        console.log("Home.vue - Loaded all projects:", projects.value.length)
      } catch (fullAccessError) {
        console.error("Error loading all data (falling back to user data):", fullAccessError)
        // Fallback to user-specific data if full access fails
        await Promise.all([projectsResource.fetch(), tasksResource.fetch()])
        projects.value = projectsResource.data || []
        tasks.value = tasksResource.data || []
      }
    } else {
      await Promise.all([projectsResource.fetch(), tasksResource.fetch()])
      projects.value = projectsResource.data || []
      tasks.value = tasksResource.data || []
      console.log("Home.vue - Loaded user projects:", projects.value.length)
    }
    stats.value = {
      projects: projects.value.filter((p) => p.status === "Active").length,
      tasks: tasks.value.filter((t) => t.status !== "Completed").length,
    }

    // Calculate insights for full access users
    if (hasFullAccess.value) {
      const today = $dayjs().format("YYYY-MM-DD")
      const completedTasksCount = tasks.value.filter((t) => t.status === "Completed").length
      const totalTasksCount = tasks.value.length

      insights.value = {
        totalProjects: projects.value.length,
        activeProjects: projects.value.filter((p) => p.status === "Active").length,
        planningProjects: projects.value.filter((p) => p.status === "Planning").length,
        onHoldProjects: projects.value.filter((p) => p.status === "On Hold").length,
        completedProjects: projects.value.filter((p) => p.status === "Completed").length,
        totalTasks: totalTasksCount,
        openTasks: tasks.value.filter((t) => t.status === "Open").length,
        workingTasks: tasks.value.filter((t) => t.status === "Working" || t.status === "Pending Review").length,
        completedTasks: completedTasksCount,
        overdueTasks: tasks.value.filter((t) => t.due_date && t.due_date < today && t.status !== "Completed").length,
        completionRate: totalTasksCount > 0 ? Math.round((completedTasksCount / totalTasksCount) * 100) : 0,
      }
    }

    lastLoadTime = now
  } catch (error) {
    console.error("Error loading data:", error)
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

function getStatusClass(status) {
  const map = {
    Active: "active",
    Planning: "planning",
    Completed: "completed",
    "On Hold": "on-hold",
    Cancelled: "cancelled",
    Open: "planning",
    Working: "on-hold",
  }
  return map[status] || ""
}

function goToProject(id) {
  router.push(`/smart-pro/project/${encodeURIComponent(id)}`)
}

function goToTask(id) {
  router.push(`/smart-pro/task/${encodeURIComponent(id)}`)
}

function goToNotifications() {
  router.push("/smart-pro/notifications")
}

async function loadNotificationCount() {
  try {
    const count = await call("frappe.client.get_count", {
      doctype: "Notification Log",
      filters: {
        for_user: ["like", "%"],
        read: 0
      }
    })
    notificationCount.value = count || 0
  } catch (err) {
    console.error("Error loading notification count:", err)
    notificationCount.value = 0
  }
}

async function loadAppSettings() {
  try {
    const settings = await call("smart_pro.smart_pro.api.projects.get_app_settings")
    if (settings && settings.app_name) {
      appName.value = settings.app_name
    }
  } catch (err) {
    console.error("Error loading app settings:", err)
  }
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
  loadAppSettings()
  loadData()
  loadNotificationCount()
})

// Reload data when navigating back to this tab
onIonViewWillEnter(() => {
  loadData()
  loadNotificationCount()
})
</script>

<style scoped>
.notification-btn {
  position: relative;
}

.notification-badge {
  position: absolute;
  top: 4px;
  right: 4px;
  min-width: 18px;
  height: 18px;
  padding: 0 4px;
  font-size: 10px;
  font-weight: 700;
  line-height: 18px;
  text-align: center;
  color: white;
  background-color: #ef4444;
  border-radius: 9px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
}

/* Insight Dashboard Cards */
.insight-card {
  border-radius: 0.5rem;
  padding: 0.75rem;
  text-align: center;
}

.insight-card-green {
  background-color: rgba(34, 197, 94, 0.15);
  color: #22c55e;
}

.insight-card-blue {
  background-color: rgba(59, 130, 246, 0.15);
  color: #3b82f6;
}

.insight-card-yellow {
  background-color: rgba(234, 179, 8, 0.15);
  color: #eab308;
}

.insight-card-orange {
  background-color: rgba(249, 115, 22, 0.15);
  color: #f97316;
}

.insight-card-gray {
  background-color: rgba(156, 163, 175, 0.15);
  color: #9ca3af;
}

/* Summary rows */
.summary-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 0;
  border-bottom: 1px solid rgba(156, 163, 175, 0.2);
}

.summary-row-last {
  border-bottom: none;
}

/* Dark mode specific overrides */
body.dark .insight-card-green {
  background-color: rgba(34, 197, 94, 0.2);
  color: #4ade80;
}

body.dark .insight-card-blue {
  background-color: rgba(59, 130, 246, 0.2);
  color: #60a5fa;
}

body.dark .insight-card-yellow {
  background-color: rgba(234, 179, 8, 0.2);
  color: #facc15;
}

body.dark .insight-card-orange {
  background-color: rgba(249, 115, 22, 0.2);
  color: #fb923c;
}

body.dark .insight-card-gray {
  background-color: rgba(156, 163, 175, 0.2);
  color: #d1d5db;
}
</style>
