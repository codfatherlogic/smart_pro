<template>
  <ion-page>
    <ion-header>
      <ion-toolbar>
        <ion-buttons slot="start">
          <ion-back-button default-href="/smart-pro/home" text="" />
        </ion-buttons>
        <ion-title>My Tasks</ion-title>
      </ion-toolbar>
      <ion-toolbar>
        <ion-segment v-model="filter" scrollable>
          <ion-segment-button value="all">
            <ion-label>All</ion-label>
          </ion-segment-button>
          <ion-segment-button value="open">
            <ion-label>Open</ion-label>
          </ion-segment-button>
          <ion-segment-button value="working">
            <ion-label>Working</ion-label>
          </ion-segment-button>
          <ion-segment-button value="done">
            <ion-label>Done</ion-label>
          </ion-segment-button>
        </ion-segment>
      </ion-toolbar>
    </ion-header>

    <ion-content :fullscreen="true">
      <template #fixed>
        <ion-refresher @ion-refresh="handleRefresh">
          <ion-refresher-content />
        </ion-refresher>
      </template>

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
          <div class="skeleton h-2 w-full" />
        </div>
      </div>

      <!-- Empty State -->
      <div
        v-else-if="filteredTasks.length === 0"
        class="empty-state h-full"
      >
        <ion-icon
          :icon="checkmarkCircleOutline"
          class="empty-state-icon"
        />
        <div class="empty-state-title">
          No tasks
        </div>
        <div class="empty-state-description">
          {{ filter === "done" ? "No completed tasks yet" : filter === "open" ? "No open tasks" : filter === "working" ? "No tasks in progress" : "No tasks assigned to you" }}
        </div>
      </div>

      <!-- Tasks List -->
      <div
        v-else
        class="p-4"
      >
        <div
          v-for="task in filteredTasks"
          :key="task.name"
          class="app-card mb-4 p-4"
        >
          <div class="flex justify-between items-start mb-2">
            <h3
              class="font-semibold text-gray-800 flex-1 pr-2"
              @click="goToTask(task.name)"
            >
              {{ task.title || task.name }}
            </h3>
            <span :class="['status-badge', getStatusClass(task.status)]">
              {{ task.status }}
            </span>
          </div>

          <div class="text-sm text-gray-500 mb-2">
            <span v-if="task.project">Project: {{ task.project }}</span>
          </div>

          <div class="flex items-center justify-between text-sm">
            <span class="text-gray-500">Due: {{ formatDate(task.due_date) }}</span>
            <span
              v-if="task.priority"
              :class="['text-xs font-medium', getPriorityClass(task.priority)]"
            >
              {{ task.priority }}
            </span>
          </div>

          <div class="mt-3">
            <div class="flex justify-between text-xs text-gray-500 mb-1">
              <span>Progress</span>
              <span>{{ task.progress || 0 }}%</span>
            </div>
            <div
              class="progress-bar"
              @click.stop="openProgressModal(task)"
            >
              <div
                class="progress-bar-fill"
                :style="{ width: (task.progress || 0) + '%' }"
              />
            </div>
            <div class="text-xs text-gray-500 mt-1 text-center">
              Tap progress bar to update
            </div>
          </div>

          <!-- Log Hours Button (hidden for completed tasks) -->
          <div
            v-if="task.status !== 'Completed'"
            class="mt-3 pt-3 border-t border-gray-100"
          >
            <ion-button
              size="small"
              expand="block"
              fill="outline"
              @click.stop="openLogHoursModal(task)"
            >
              <ion-icon :icon="timeOutline" slot="start" />
              Log Hours
            </ion-button>
          </div>
        </div>
      </div>
    </ion-content>

    <!-- Progress Update Modal -->
    <ion-modal
      :is-open="showProgressModal"
      @did-dismiss="showProgressModal = false"
    >
      <ion-header>
        <ion-toolbar>
          <ion-title>Update Progress</ion-title>
          <ion-buttons slot="end">
            <ion-button @click="showProgressModal = false">
              Close
            </ion-button>
          </ion-buttons>
        </ion-toolbar>
      </ion-header>
      <ion-content class="ion-padding">
        <div
          v-if="selectedTask"
          class="mb-4"
        >
          <h3 class="font-semibold text-lg mb-2">
            {{ selectedTask.title || selectedTask.name }}
          </h3>
          <div class="text-sm text-gray-500">
            Current progress: {{ selectedTask.progress || 0 }}%
          </div>
        </div>

        <div class="mb-6">
          <ion-label class="block text-sm font-medium text-gray-700 mb-2">
            Set Progress (0-100%)
          </ion-label>
          <div class="flex items-center space-x-4">
            <ion-range
              v-model="progressValue"
              :min="0"
              :max="100"
              :step="5"
              color="primary"
              class="flex-1"
            >
              <template #start>
                <ion-label>0%</ion-label>
              </template>
              <template #end>
                <ion-label>100%</ion-label>
              </template>
            </ion-range>
            <div class="text-lg font-semibold w-16 text-center">
              {{ progressValue }}%
            </div>
          </div>
        </div>

        <div class="mb-4">
          <ion-label class="block text-sm font-medium text-gray-700 mb-2">
            Status
          </ion-label>
          <ion-select
            v-model="statusValue"
            fill="outline"
            interface="action-sheet"
          >
            <ion-select-option value="Open">
              Open
            </ion-select-option>
            <ion-select-option value="Working">
              Working
            </ion-select-option>
            <ion-select-option value="Pending Review">
              Pending Review
            </ion-select-option>
            <ion-select-option value="Completed">
              Completed
            </ion-select-option>
          </ion-select>
        </div>

        <ion-button
          expand="block"
          :disabled="updating"
          class="mt-6"
          @click="updateProgress"
        >
          <ion-spinner
            v-if="updating"
            name="crescent"
            class="mr-2"
          />
          {{ updating ? "Updating..." : "Update Task" }}
        </ion-button>

        <div
          v-if="error"
          class="mt-4 p-3 bg-red-50 text-red-600 rounded-lg text-sm"
        >
          {{ error }}
        </div>
      </ion-content>
    </ion-modal>

    <!-- Log Hours Modal -->
    <ion-modal
      :is-open="showLogHoursModal"
      @did-dismiss="showLogHoursModal = false"
    >
      <ion-header>
        <ion-toolbar>
          <ion-title>Log Hours</ion-title>
          <ion-buttons slot="end">
            <ion-button @click="showLogHoursModal = false">
              Close
            </ion-button>
          </ion-buttons>
        </ion-toolbar>
      </ion-header>
      <ion-content class="ion-padding">
        <div
          v-if="selectedTaskForLog"
          class="mb-4"
        >
          <h3 class="font-semibold text-lg mb-2">
            {{ selectedTaskForLog.title || selectedTaskForLog.name }}
          </h3>
          <div class="text-sm text-gray-500">
            {{ selectedTaskForLog.project }}
          </div>
        </div>

        <form @submit.prevent="submitLogHours">
          <!-- Date -->
          <div class="mb-4">
            <ion-label class="block text-sm font-medium text-gray-700 mb-1">
              Date *
            </ion-label>
            <ion-input
              v-model="logEntry.date"
              type="date"
              fill="outline"
              required
            />
          </div>

          <!-- Hours Worked -->
          <div class="mb-4">
            <ion-label class="block text-sm font-medium text-gray-700 mb-1">
              Hours Worked *
            </ion-label>
            <ion-input
              v-model="logEntry.hours_worked"
              type="number"
              min="0.5"
              max="24"
              step="0.5"
              placeholder="e.g., 8"
              fill="outline"
              required
            />
          </div>

          <!-- Activity Type -->
          <div class="mb-4">
            <ion-label class="block text-sm font-medium text-gray-700 mb-1">
              Activity Type
            </ion-label>
            <ion-select
              v-model="logEntry.activity_type"
              interface="action-sheet"
              fill="outline"
            >
              <ion-select-option value="Development">Development</ion-select-option>
              <ion-select-option value="Design">Design</ion-select-option>
              <ion-select-option value="Testing">Testing</ion-select-option>
              <ion-select-option value="Documentation">Documentation</ion-select-option>
              <ion-select-option value="Meeting">Meeting</ion-select-option>
              <ion-select-option value="Research">Research</ion-select-option>
              <ion-select-option value="Bug Fix">Bug Fix</ion-select-option>
              <ion-select-option value="Code Review">Code Review</ion-select-option>
              <ion-select-option value="Deployment">Deployment</ion-select-option>
              <ion-select-option value="Other">Other</ion-select-option>
            </ion-select>
          </div>

          <!-- Description -->
          <div class="mb-4">
            <ion-label class="block text-sm font-medium text-gray-700 mb-1">
              Work Description *
            </ion-label>
            <ion-textarea
              v-model="logEntry.description"
              placeholder="What did you work on?"
              fill="outline"
              :rows="3"
              required
            />
          </div>

          <!-- Submit Button -->
          <ion-button
            expand="block"
            type="submit"
            :disabled="loggingHours"
            class="mt-6"
          >
            <ion-spinner
              v-if="loggingHours"
              name="crescent"
              class="mr-2"
            />
            {{ loggingHours ? "Saving..." : "Save Timesheet" }}
          </ion-button>

          <div
            v-if="logError"
            class="mt-4 p-3 bg-red-50 text-red-600 rounded-lg text-sm"
          >
            {{ logError }}
          </div>
        </form>
      </ion-content>
    </ion-modal>
  </ion-page>
</template>

<script setup>
import { ref, computed, inject, onMounted } from "vue"
import { onIonViewWillEnter } from "@ionic/vue"
import { useRouter } from "vue-router"
import {
  IonPage,
  IonHeader,
  IonToolbar,
  IonTitle,
  IonContent,
  IonSegment,
  IonSegmentButton,
  IonLabel,
  IonRefresher,
  IonRefresherContent,
  IonIcon,
  IonModal,
  IonButton,
  IonButtons,
  IonBackButton,
  IonRange,
  IonSelect,
  IonSelectOption,
  IonSpinner,
  IonInput,
  IonTextarea,
  toastController,
} from "@ionic/vue"
import { checkmarkCircleOutline, timeOutline } from "ionicons/icons"
import { createResource, call } from "frappe-ui"

const router = useRouter()
const $dayjs = inject("$dayjs")

const loading = ref(true)
const filter = ref("all")
const tasks = ref([])
const showProgressModal = ref(false)
const selectedTask = ref(null)
const progressValue = ref(0)
const statusValue = ref("Open")
const updating = ref(false)
const error = ref("")

// Log Hours state
const showLogHoursModal = ref(false)
const selectedTaskForLog = ref(null)
const loggingHours = ref(false)
const logError = ref("")
const logEntry = ref({
  date: "",
  hours_worked: "",
  activity_type: "Development",
  description: "",
})

const filteredTasks = computed(() => {
  if (filter.value === "all") return tasks.value
  if (filter.value === "open") {
    return tasks.value.filter((t) => t.status === "Open")
  }
  if (filter.value === "working") {
    return tasks.value.filter((t) => t.status === "Working" || t.status === "Pending Review")
  }
  if (filter.value === "done") {
    return tasks.value.filter((t) => t.status === "Completed")
  }
  return tasks.value
})

// Use createResource like Home.vue does - this pattern works correctly
const tasksResource = createResource({
  url: "smart_pro.smart_pro.api.projects.get_user_tasks",
  auto: false,
})

async function loadData() {
  loading.value = true
  error.value = ""
  try {
    await tasksResource.fetch()
    tasks.value = tasksResource.data || []
    console.log("Tasks loaded via createResource:", tasks.value.length, "tasks")
  } catch (err) {
    console.error("Error loading tasks:", err)
    error.value = err.messages?.[0] || err.message || "Failed to load tasks"
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
  const date = $dayjs(dateStr)
  if (date.isToday()) return "Today"
  if (date.isTomorrow()) return "Tomorrow"
  return date.format("MMM D")
}

function getStatusClass(status) {
  const map = {
    Open: "planning",
    Working: "on-hold",
    "Pending Review": "on-hold",
    Completed: "completed",
    Cancelled: "cancelled",
  }
  return map[status] || ""
}

function getPriorityClass(priority) {
  const map = {
    Low: "text-green-600",
    Medium: "text-blue-600",
    High: "text-orange-600",
    Critical: "text-red-600",
  }
  return map[priority] || "text-gray-600"
}

function goToTask(id) {
  router.push(`/smart-pro/task/${encodeURIComponent(id)}`)
}

function openProgressModal(task) {
  selectedTask.value = task
  progressValue.value = task.progress || 0
  statusValue.value = task.status || "Open"
  showProgressModal.value = true
}

async function updateProgress() {
  if (!selectedTask.value) return

  updating.value = true
  error.value = ""

  try {
    await call("frappe.client.set_value", {
      doctype: "Smart Task",
      name: selectedTask.value.name,
      fieldname: {
        progress: progressValue.value,
        status: statusValue.value,
      },
    })

    const toast = await toastController.create({
      message: "Task updated successfully!",
      duration: 2000,
      color: "success",
    })
    await toast.present()

    // Update local data
    const taskIndex = tasks.value.findIndex(t => t.name === selectedTask.value.name)
    if (taskIndex !== -1) {
      tasks.value[taskIndex].progress = progressValue.value
      tasks.value[taskIndex].status = statusValue.value
    }

    showProgressModal.value = false
    selectedTask.value = null
  } catch (err) {
    console.error("Error updating task:", err)
    error.value = err.messages?.[0] || err.message || "Failed to update task"
  } finally {
    updating.value = false
  }
}

function openLogHoursModal(task) {
  selectedTaskForLog.value = task
  logEntry.value = {
    date: $dayjs().format("YYYY-MM-DD"),
    hours_worked: "",
    activity_type: "Development",
    description: "",
  }
  logError.value = ""
  showLogHoursModal.value = true
}

async function submitLogHours() {
  if (!selectedTaskForLog.value) return

  if (!logEntry.value.date || !logEntry.value.hours_worked || !logEntry.value.description) {
    logError.value = "Date, hours, and description are required"
    return
  }

  loggingHours.value = true
  logError.value = ""

  try {
    await call("smart_pro.smart_pro.api.projects.create_timesheet", {
      task: selectedTaskForLog.value.name,
      date: logEntry.value.date,
      hours_worked: parseFloat(logEntry.value.hours_worked),
      description: logEntry.value.description,
      activity_type: logEntry.value.activity_type,
      notes: null,
    })

    const toast = await toastController.create({
      message: "Timesheet saved successfully!",
      duration: 2000,
      color: "success",
    })
    await toast.present()

    showLogHoursModal.value = false
    selectedTaskForLog.value = null
  } catch (err) {
    console.error("Error saving timesheet:", err)
    logError.value = err.messages?.[0] || err.message || "Failed to save timesheet"
  } finally {
    loggingHours.value = false
  }
}

// Use both onMounted (for initial load) and onIonViewWillEnter (for tab navigation)
onMounted(() => {
  console.log("Tasks component mounted - loading data")
  loadData()
})

// Also reload when navigating back to this tab
onIonViewWillEnter(() => {
  console.log("Tasks view entering - reloading data")
  loadData()
})
</script>


<style scoped>
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  text-align: center;
}

.empty-state-icon {
  font-size: 4rem;
  color: var(--ion-color-medium);
  margin-bottom: 1rem;
}

.empty-state-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--ion-color-dark);
  margin-bottom: 0.5rem;
}

.empty-state-description {
  color: var(--ion-color-medium);
  max-width: 20rem;
}

.status-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
}

.status-badge.planning {
  background-color: #e0f2fe;
  color: #0369a1;
}

.status-badge.on-hold {
  background-color: #fef3c7;
  color: #92400e;
}

.status-badge.completed {
  background-color: #d1fae5;
  color: #065f46;
}

.status-badge.cancelled {
  background-color: #fee2e2;
  color: #991b1b;
}

.progress-bar {
  height: 0.75rem;
  background-color: #e5e7eb;
  border-radius: 0.375rem;
  overflow: hidden;
  cursor: pointer;
  transition: background-color 0.2s;
}

.progress-bar:hover {
  background-color: #d1d5db;
}

.progress-bar-fill {
  height: 100%;
  background-color: #3b82f6;
  border-radius: 0.375rem;
  transition: width 0.3s ease;
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

.app-card {
  background-color: white;
  border-radius: 0.75rem;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
  transition: box-shadow 0.2s;
}

.app-card:hover {
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}
</style>
