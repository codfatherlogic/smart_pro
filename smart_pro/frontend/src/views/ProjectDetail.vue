<template>
  <ion-page>
    <ion-header>
      <ion-toolbar>
        <ion-buttons slot="start">
          <ion-back-button
            default-href="/smart-pro/projects"
            text=""
          />
        </ion-buttons>
        <ion-title>Project Details</ion-title>
      </ion-toolbar>
    </ion-header>

    <ion-content :fullscreen="true">
      <ion-refresher slot="fixed" @ion-refresh="handleRefresh">
        <ion-refresher-content />
      </ion-refresher>

      <!-- Loading State -->
      <div
        v-if="loading"
        class="p-4"
      >
        <div class="skeleton h-8 w-3/4 mb-4" />
        <div class="skeleton h-4 w-1/2 mb-6" />
        <div class="skeleton h-24 w-full mb-4" />
        <div class="skeleton h-32 w-full" />
      </div>

      <!-- Error State -->
      <div
        v-else-if="error"
        class="empty-state h-full"
      >
        <div class="empty-state-title">
          Error loading project
        </div>
        <div class="empty-state-description">
          {{ error }}
        </div>
        <ion-button
          class="mt-4"
          @click="loadData"
        >
          Retry
        </ion-button>
      </div>

      <!-- Project Details -->
      <div
        v-else-if="project"
        class="p-4"
      >
        <!-- Header -->
        <div class="mb-6">
          <div class="flex justify-between items-start mb-2">
            <h1 class="text-2xl font-bold text-gray-800">
              {{ project.title }}
            </h1>
            <span :class="['status-badge', getStatusClass(project.status)]">
              {{ project.status }}
            </span>
          </div>
          <p
            v-if="project.description"
            class="text-gray-600"
          >
            {{ stripHtml(project.description) }}
          </p>
        </div>

        <!-- Info Cards -->
        <div class="grid grid-cols-2 gap-4 mb-6">
          <div class="app-card p-4">
            <div class="text-xs text-gray-500 mb-1">
              Start Date
            </div>
            <div class="font-medium">
              {{ formatDate(project.start_date) }}
            </div>
          </div>
          <div class="app-card p-4">
            <div class="text-xs text-gray-500 mb-1">
              End Date
            </div>
            <div class="font-medium">
              {{ formatDate(project.end_date) }}
            </div>
          </div>
          <div
            v-if="project.project_manager"
            class="app-card p-4"
          >
            <div class="text-xs text-gray-500 mb-1">
              Manager
            </div>
            <div class="font-medium">
              {{ project.project_manager }}
            </div>
          </div>
          <div
            v-if="project.budget_amount"
            class="app-card p-4"
          >
            <div class="text-xs text-gray-500 mb-1">
              Budget
            </div>
            <div class="font-medium">
              {{ formatCurrency(project.budget_amount) }}
            </div>
          </div>
        </div>

        <!-- Tasks Section -->
        <div class="app-card mb-6">
          <div class="app-card-header flex justify-between items-center">
            <span>Tasks ({{ tasks.length }})</span>
          </div>
          <div
            v-if="tasks.length === 0"
            class="p-4 text-center text-gray-500"
          >
            No tasks for this project
          </div>
          <div v-else>
            <div
              v-for="task in tasks"
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
              </div>
              <span :class="['status-badge', getStatusClass(task.status)]">
                {{ task.status }}
              </span>
            </div>
          </div>
        </div>

        <!-- Team Section -->
        <div class="app-card">
          <div class="app-card-header flex justify-between items-center">
            <span>Team ({{ assignments.length }})</span>
            <!-- Add assignment button for full access users -->
            <ion-button
              v-if="hasFullAccess"
              fill="clear"
              size="small"
              @click="openAddAssignment"
            >
              <ion-icon :icon="addOutline" />
            </ion-button>
          </div>
          <div
            v-if="assignments.length === 0"
            class="p-4 text-center text-gray-500"
          >
            No team members assigned
          </div>
          <div v-else>
            <div
              v-for="member in assignments"
              :key="member.name"
              class="app-list-item"
            >
              <div class="flex items-center">
                <div
                  class="w-10 h-10 rounded-full bg-primary-100 flex items-center justify-center mr-3"
                >
                  <span class="text-sm font-medium text-primary-600">
                    {{ getInitials(member.employee_name) }}
                  </span>
                </div>
                <div>
                  <div class="font-medium text-gray-800">
                    {{ member.employee_name }}
                  </div>
                  <div class="text-sm text-gray-500">
                    {{ member.role }}
                  </div>
                </div>
              </div>
              <div class="text-sm text-gray-500">
                {{ member.allocation_percentage }}%
              </div>
            </div>
          </div>
        </div>
      </div>
    </ion-content>
  </ion-page>
</template>

<script setup>
import { ref, onMounted, inject } from "vue"
import { useRoute, useRouter } from "vue-router"
import {
  IonPage,
  IonHeader,
  IonToolbar,
  IonTitle,
  IonContent,
  IonButtons,
  IonBackButton,
  IonButton,
  IonIcon,
  IonRefresher,
  IonRefresherContent,
} from "@ionic/vue"
import { addOutline } from "ionicons/icons"
import { createResource } from "frappe-ui"
import { usePermissions } from "@/composables/usePermissions"

const route = useRoute()
const router = useRouter()
const $dayjs = inject("$dayjs")
const { fetchPermissions, hasFullAccess } = usePermissions()

const loading = ref(true)
const error = ref("")
const project = ref(null)
const tasks = ref([])
const assignments = ref([])

const projectResource = createResource({
  url: "smart_pro.smart_pro.api.projects.get_project_details",
  auto: false,
})

const tasksResource = createResource({
  url: "smart_pro.smart_pro.api.projects.get_project_tasks",
  auto: false,
})

const assignmentsResource = createResource({
  url: "smart_pro.smart_pro.api.projects.get_employee_assignments",
  auto: false,
})

async function loadData() {
  const projectId = route.params.id
  if (!projectId) {
    error.value = "Project not found"
    return
  }

  loading.value = true
  error.value = ""

  try {
    // Fetch permissions first
    await fetchPermissions()

    await Promise.all([
      projectResource.fetch({ project_name: projectId }),
      tasksResource.fetch({ project_name: projectId }),
      assignmentsResource.fetch({ project_name: projectId }),
    ])

    project.value = projectResource.data
    tasks.value = tasksResource.data || []
    assignments.value = assignmentsResource.data || []
  } catch (err) {
    console.error("Error loading project:", err)
    error.value = err.message || "Failed to load project"
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
    Open: "planning",
    Working: "on-hold",
  }
  return map[status] || ""
}

function stripHtml(html) {
  if (!html) return ""
  // Create a temporary element to parse HTML and extract text
  const tmp = document.createElement("div")
  tmp.innerHTML = html
  return tmp.textContent || tmp.innerText || ""
}

function getInitials(name) {
  if (!name) return "?"
  return name
    .split(" ")
    .map((n) => n[0])
    .join("")
    .toUpperCase()
    .slice(0, 2)
}

function goToTask(id) {
  router.push(`/smart-pro/task/${encodeURIComponent(id)}`)
}

function openAddAssignment() {
  // Navigate to mobile create assignment page with project pre-filled
  const projectName = route.params.id
  router.push(`/smart-pro/assignment/new?project=${encodeURIComponent(projectName)}`)
}

onMounted(() => {
  loadData()
})
</script>
