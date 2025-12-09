<template>
  <ion-page>
    <ion-header>
      <ion-toolbar>
        <ion-buttons slot="start">
          <ion-back-button default-href="/smart-pro/home" text="" />
        </ion-buttons>
        <ion-title>Connections Dashboard</ion-title>
        <ion-buttons slot="end">
          <ion-button @click="refreshData">
            <ion-icon :icon="refreshOutline" />
          </ion-button>
        </ion-buttons>
      </ion-toolbar>
    </ion-header>

    <ion-content :fullscreen="true">
      <template #fixed>
        <ion-refresher @ion-refresh="handleRefresh">
          <ion-refresher-content />
        </ion-refresher>
      </template>

      <div class="p-4">
        <!-- Workflow Overview -->
        <div class="app-card mb-4 p-4 bg-gradient-to-r from-blue-500 to-blue-600 text-white">
          <h2 class="text-lg font-bold mb-2">Smart Pro Workflow</h2>
          <div class="text-sm opacity-90">
            Project → Assignment → Date Request → Task → Timesheet
          </div>
        </div>

        <!-- Loading State -->
        <div v-if="loading" class="space-y-4">
          <div v-for="i in 6" :key="i" class="app-card p-4">
            <div class="skeleton h-6 w-1/2 mb-2" />
            <div class="skeleton h-4 w-3/4" />
          </div>
        </div>

        <!-- DocType Cards -->
        <div v-else class="space-y-4">
          <!-- Smart Projects -->
          <div class="app-card p-4">
            <div class="flex items-center justify-between">
              <div class="flex items-center">
                <div class="w-12 h-12 rounded-full bg-blue-100 flex items-center justify-center mr-3">
                  <ion-icon :icon="folderOutline" class="text-2xl text-blue-600" />
                </div>
                <div>
                  <h3 class="font-semibold text-gray-800">Smart Projects</h3>
                  <p class="text-sm text-gray-500">Main project container</p>
                </div>
              </div>
              <div class="text-right">
                <div class="text-2xl font-bold text-blue-600">{{ counts.projects }}</div>
                <div class="text-xs text-gray-500">Total</div>
              </div>
            </div>
            <div class="mt-3 pt-3 border-t border-gray-100">
              <div class="flex justify-between text-sm">
                <span class="text-green-600">{{ counts.activeProjects }} Active</span>
                <span class="text-blue-600">{{ counts.planningProjects }} Planning</span>
                <span class="text-gray-500">{{ counts.completedProjects }} Done</span>
              </div>
            </div>
          </div>

          <!-- Employee Project Assignments -->
          <div class="app-card p-4">
            <div class="flex items-center justify-between">
              <div class="flex items-center">
                <div class="w-12 h-12 rounded-full bg-purple-100 flex items-center justify-center mr-3">
                  <ion-icon :icon="peopleOutline" class="text-2xl text-purple-600" />
                </div>
                <div>
                  <h3 class="font-semibold text-gray-800">Project Assignments</h3>
                  <p class="text-sm text-gray-500">Employee to project mapping</p>
                </div>
              </div>
              <div class="text-right">
                <div class="text-2xl font-bold text-purple-600">{{ counts.assignments }}</div>
                <div class="text-xs text-gray-500">Total</div>
              </div>
            </div>
            <div class="mt-3 pt-3 border-t border-gray-100 text-sm text-gray-600">
              <ion-icon :icon="arrowForwardOutline" class="mr-1" />
              Auto-creates Date Request on assignment
            </div>
          </div>

          <!-- Employee Date Requests -->
          <div class="app-card p-4">
            <div class="flex items-center justify-between">
              <div class="flex items-center">
                <div class="w-12 h-12 rounded-full bg-orange-100 flex items-center justify-center mr-3">
                  <ion-icon :icon="calendarOutline" class="text-2xl text-orange-600" />
                </div>
                <div>
                  <h3 class="font-semibold text-gray-800">Date Requests</h3>
                  <p class="text-sm text-gray-500">Leave, WFH, Project dates</p>
                </div>
              </div>
              <div class="text-right">
                <div class="text-2xl font-bold text-orange-600">{{ counts.dateRequests }}</div>
                <div class="text-xs text-gray-500">Total</div>
              </div>
            </div>
            <div class="mt-3 pt-3 border-t border-gray-100">
              <div class="flex justify-between text-sm">
                <span class="text-yellow-600">{{ counts.pendingRequests }} Pending</span>
                <span class="text-green-600">{{ counts.approvedRequests }} Approved</span>
                <span class="text-red-600">{{ counts.rejectedRequests }} Rejected</span>
              </div>
            </div>
          </div>

          <!-- Smart Tasks -->
          <div class="app-card p-4">
            <div class="flex items-center justify-between">
              <div class="flex items-center">
                <div class="w-12 h-12 rounded-full bg-green-100 flex items-center justify-center mr-3">
                  <ion-icon :icon="checkmarkCircleOutline" class="text-2xl text-green-600" />
                </div>
                <div>
                  <h3 class="font-semibold text-gray-800">Smart Tasks</h3>
                  <p class="text-sm text-gray-500">Work items & assignments</p>
                </div>
              </div>
              <div class="text-right">
                <div class="text-2xl font-bold text-green-600">{{ counts.tasks }}</div>
                <div class="text-xs text-gray-500">Total</div>
              </div>
            </div>
            <div class="mt-3 pt-3 border-t border-gray-100">
              <div class="flex justify-between text-sm">
                <span class="text-blue-600">{{ counts.openTasks }} Open</span>
                <span class="text-yellow-600">{{ counts.workingTasks }} Working</span>
                <span class="text-green-600">{{ counts.completedTasks }} Done</span>
              </div>
            </div>
          </div>

          <!-- Smart Time Sheets -->
          <div class="app-card p-4">
            <div class="flex items-center justify-between">
              <div class="flex items-center">
                <div class="w-12 h-12 rounded-full bg-teal-100 flex items-center justify-center mr-3">
                  <ion-icon :icon="timeOutline" class="text-2xl text-teal-600" />
                </div>
                <div>
                  <h3 class="font-semibold text-gray-800">Time Sheets</h3>
                  <p class="text-sm text-gray-500">Work hour logging</p>
                </div>
              </div>
              <div class="text-right">
                <div class="text-2xl font-bold text-teal-600">{{ counts.timesheets }}</div>
                <div class="text-xs text-gray-500">Total</div>
              </div>
            </div>
            <div class="mt-3 pt-3 border-t border-gray-100">
              <div class="flex justify-between text-sm">
                <span class="text-blue-600">{{ counts.draftTimesheets }} Draft</span>
                <span class="text-yellow-600">{{ counts.submittedTimesheets }} Submitted</span>
                <span class="text-green-600">{{ counts.approvedTimesheets }} Approved</span>
              </div>
            </div>
          </div>

          <!-- Notifications -->
          <div class="app-card p-4">
            <div class="flex items-center justify-between">
              <div class="flex items-center">
                <div class="w-12 h-12 rounded-full bg-red-100 flex items-center justify-center mr-3">
                  <ion-icon :icon="notificationsOutline" class="text-2xl text-red-600" />
                </div>
                <div>
                  <h3 class="font-semibold text-gray-800">Notifications</h3>
                  <p class="text-sm text-gray-500">System alerts & updates</p>
                </div>
              </div>
              <div class="text-right">
                <div class="text-2xl font-bold text-red-600">{{ counts.notifications }}</div>
                <div class="text-xs text-gray-500">Total</div>
              </div>
            </div>
          </div>
        </div>

        <!-- Workflow Diagram -->
        <div class="app-card mt-6 p-4">
          <h3 class="font-semibold text-gray-800 mb-4">Document Flow</h3>
          <div class="workflow-diagram">
            <div class="workflow-step">
              <div class="workflow-icon bg-blue-100 text-blue-600">
                <ion-icon :icon="folderOutline" />
              </div>
              <div class="workflow-label">Project</div>
            </div>
            <div class="workflow-arrow">
              <ion-icon :icon="arrowForwardOutline" />
            </div>
            <div class="workflow-step">
              <div class="workflow-icon bg-purple-100 text-purple-600">
                <ion-icon :icon="peopleOutline" />
              </div>
              <div class="workflow-label">Assignment</div>
            </div>
            <div class="workflow-arrow">
              <ion-icon :icon="arrowForwardOutline" />
            </div>
            <div class="workflow-step">
              <div class="workflow-icon bg-orange-100 text-orange-600">
                <ion-icon :icon="calendarOutline" />
              </div>
              <div class="workflow-label">Date Request</div>
            </div>
            <div class="workflow-arrow">
              <ion-icon :icon="arrowForwardOutline" />
            </div>
            <div class="workflow-step">
              <div class="workflow-icon bg-green-100 text-green-600">
                <ion-icon :icon="checkmarkCircleOutline" />
              </div>
              <div class="workflow-label">Task</div>
            </div>
            <div class="workflow-arrow">
              <ion-icon :icon="arrowForwardOutline" />
            </div>
            <div class="workflow-step">
              <div class="workflow-icon bg-teal-100 text-teal-600">
                <ion-icon :icon="timeOutline" />
              </div>
              <div class="workflow-label">Timesheet</div>
            </div>
          </div>
        </div>

        <!-- Quick Actions -->
        <div class="app-card mt-4 p-4">
          <h3 class="font-semibold text-gray-800 mb-4">Quick Actions</h3>
          <div class="grid grid-cols-2 gap-3">
            <ion-button expand="block" color="primary" @click="router.push('/smart-pro/projects')">
              <ion-icon :icon="folderOutline" slot="start" />
              View Projects
            </ion-button>
            <ion-button expand="block" color="secondary" @click="router.push('/smart-pro/date-requests')">
              <ion-icon :icon="calendarOutline" slot="start" />
              Date Request
            </ion-button>
            <ion-button expand="block" color="success" @click="router.push('/smart-pro/tasks')">
              <ion-icon :icon="checkmarkCircleOutline" slot="start" />
              View Tasks
            </ion-button>
            <ion-button expand="block" color="tertiary" @click="router.push('/smart-pro/timesheet')">
              <ion-icon :icon="timeOutline" slot="start" />
              Log Hours
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
import {
  IonPage,
  IonHeader,
  IonToolbar,
  IonTitle,
  IonContent,
  IonButton,
  IonButtons,
  IonBackButton,
  IonIcon,
  IonRefresher,
  IonRefresherContent,
} from "@ionic/vue"
import {
  refreshOutline,
  folderOutline,
  peopleOutline,
  calendarOutline,
  checkmarkCircleOutline,
  timeOutline,
  notificationsOutline,
  arrowForwardOutline,
} from "ionicons/icons"
import { call } from "frappe-ui"

const router = useRouter()

const loading = ref(true)
const counts = ref({
  projects: 0,
  activeProjects: 0,
  planningProjects: 0,
  completedProjects: 0,
  assignments: 0,
  dateRequests: 0,
  pendingRequests: 0,
  approvedRequests: 0,
  rejectedRequests: 0,
  tasks: 0,
  openTasks: 0,
  workingTasks: 0,
  completedTasks: 0,
  timesheets: 0,
  draftTimesheets: 0,
  submittedTimesheets: 0,
  approvedTimesheets: 0,
  notifications: 0,
})

async function loadData() {
  loading.value = true
  try {
    const result = await call("smart_pro.smart_pro.api.projects.get_connections_dashboard")
    if (result) {
      counts.value = result
    }
  } catch (err) {
    console.error("Error loading connections data:", err)
    // Load with fallback if API doesn't exist
    await loadFallbackData()
  } finally {
    loading.value = false
  }
}

async function loadFallbackData() {
  try {
    // Fetch counts using frappe.client.get_count
    const [projects, assignments, dateRequests, tasks, timesheets] = await Promise.all([
      call("frappe.client.get_count", { doctype: "Smart Project" }),
      call("frappe.client.get_count", { doctype: "Employee Project Assignment" }),
      call("frappe.client.get_count", { doctype: "Employee Date Request" }),
      call("frappe.client.get_count", { doctype: "Smart Task" }),
      call("frappe.client.get_count", { doctype: "Smart Time Sheet" }),
    ])

    counts.value.projects = projects || 0
    counts.value.assignments = assignments || 0
    counts.value.dateRequests = dateRequests || 0
    counts.value.tasks = tasks || 0
    counts.value.timesheets = timesheets || 0
  } catch (err) {
    console.error("Error loading fallback data:", err)
  }
}

function handleRefresh(event) {
  loadData().finally(() => {
    event.target.complete()
  })
}

function refreshData() {
  loadData()
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.app-card {
  background-color: white;
  border-radius: 0.75rem;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
  transition: box-shadow 0.2s;
}

.app-card:hover {
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

.skeleton {
  background-color: #e5e7eb;
  border-radius: 0.25rem;
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.workflow-diagram {
  display: flex;
  align-items: center;
  justify-content: space-between;
  overflow-x: auto;
  padding: 1rem 0;
}

.workflow-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 60px;
}

.workflow-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
}

.workflow-label {
  margin-top: 0.5rem;
  font-size: 0.7rem;
  text-align: center;
  color: #6b7280;
  white-space: nowrap;
}

.workflow-arrow {
  color: #9ca3af;
  font-size: 1rem;
  padding: 0 0.25rem;
}
</style>
