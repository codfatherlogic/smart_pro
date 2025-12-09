<template>
  <ion-page>
    <ion-header>
      <ion-toolbar>
        <ion-buttons slot="start">
          <ion-back-button default-href="/smart-pro/home" text="" />
        </ion-buttons>
        <ion-title>Timesheet</ion-title>
        <ion-buttons slot="end">
          <ion-button @click="openAddModal">
            <ion-icon :icon="addOutline" />
          </ion-button>
        </ion-buttons>
      </ion-toolbar>
      <ion-toolbar>
        <ion-segment v-model="filter" scrollable>
          <ion-segment-button value="all">
            <ion-label>All</ion-label>
          </ion-segment-button>
          <ion-segment-button value="draft">
            <ion-label>Draft</ion-label>
          </ion-segment-button>
          <ion-segment-button value="submitted">
            <ion-label>Submitted</ion-label>
          </ion-segment-button>
          <ion-segment-button value="approved">
            <ion-label>Approved</ion-label>
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

      <!-- Today's Summary Card -->
      <div class="p-4 pb-0">
        <div class="app-card p-4 bg-gradient-to-r from-blue-500 to-blue-600 text-white">
          <div class="text-sm opacity-90 mb-1">Today's Summary</div>
          <div class="flex justify-between items-end">
            <div>
              <span class="text-3xl font-bold">{{ todaySummary.total_hours || 0 }}</span>
              <span class="text-lg ml-1">hours</span>
            </div>
            <div class="text-right">
              <div class="text-sm opacity-90">{{ todaySummary.tasks_worked || 0 }} tasks</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="p-4">
        <div v-for="i in 3" :key="i" class="app-card mb-4 p-4">
          <div class="skeleton h-5 w-3/4 mb-2" />
          <div class="skeleton h-4 w-1/2 mb-2" />
          <div class="skeleton h-3 w-full" />
        </div>
      </div>

      <!-- Empty State -->
      <div v-else-if="filteredTimeSheets.length === 0" class="empty-state h-full">
        <ion-icon :icon="timeOutline" class="empty-state-icon" />
        <div class="empty-state-title">No timesheet entries</div>
        <div class="empty-state-description">
          {{ filter === "draft" ? "No draft timesheets" : filter === "submitted" ? "No submitted timesheets" : filter === "approved" ? "No approved timesheets" : "Log your work hours from your assigned tasks" }}
        </div>
        <ion-button class="mt-4" @click="openAddModal">
          Log Hours
        </ion-button>
      </div>

      <!-- Time Sheets List -->
      <div v-else class="p-4">
        <div v-for="entry in filteredTimeSheets" :key="entry.name" class="app-card mb-4 p-4">
          <div class="flex justify-between items-start mb-2">
            <h3 class="font-semibold text-gray-800">
              {{ entry.task_title || entry.task || "General Work" }}
            </h3>
            <span :class="['status-badge', getStatusClass(entry.status)]">
              {{ entry.status }}
            </span>
          </div>
          <div class="text-sm text-gray-500 mb-2">
            <ion-icon :icon="calendarOutline" class="mr-1" />
            {{ formatDate(entry.date) }}
          </div>
          <div class="flex items-center justify-between text-sm">
            <span class="text-gray-600">
              <ion-icon :icon="timeOutline" class="mr-1" />
              {{ entry.hours_worked }} hours
            </span>
            <span class="px-2 py-1 bg-gray-100 rounded text-xs text-gray-600">
              {{ entry.activity_type }}
            </span>
          </div>
          <div v-if="entry.project" class="mt-2 text-sm text-blue-600">
            <ion-icon :icon="folderOutline" class="mr-1" />
            {{ entry.project }}
          </div>
          <div v-if="entry.description" class="mt-2 text-sm text-gray-600 line-clamp-2">
            {{ stripHtml(entry.description) }}
          </div>

          <!-- Submit Button for Draft entries -->
          <div v-if="entry.status === 'Draft'" class="mt-3 pt-3 border-t border-gray-100">
            <ion-button
              size="small"
              expand="block"
              @click="submitTimesheet(entry.name)"
              :disabled="submittingId === entry.name"
            >
              <ion-spinner v-if="submittingId === entry.name" name="crescent" class="mr-2" />
              {{ submittingId === entry.name ? 'Submitting...' : 'Submit for Approval' }}
            </ion-button>
          </div>
        </div>
      </div>
    </ion-content>

    <!-- Add Time Sheet Modal -->
    <ion-modal :is-open="showAddModal" @did-dismiss="showAddModal = false">
      <ion-header>
        <ion-toolbar>
          <ion-title>Log Hours</ion-title>
          <ion-buttons slot="end">
            <ion-button @click="showAddModal = false">Close</ion-button>
          </ion-buttons>
        </ion-toolbar>
      </ion-header>
      <ion-content class="ion-padding">
        <form @submit.prevent="submitTimeSheet">
          <!-- Task Selection -->
          <div class="mb-4">
            <ion-label class="block text-sm font-medium text-gray-700 mb-1">
              Task *
            </ion-label>
            <ion-select
              v-model="newEntry.task"
              placeholder="Select a task"
              interface="action-sheet"
              fill="outline"
            >
              <ion-select-option v-for="task in myTasks" :key="task.name" :value="task.name">
                {{ task.title }}
              </ion-select-option>
            </ion-select>
          </div>

          <!-- Date -->
          <div class="mb-4">
            <ion-label class="block text-sm font-medium text-gray-700 mb-1">
              Date *
            </ion-label>
            <ion-input
              v-model="newEntry.date"
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
              v-model="newEntry.hours_worked"
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
              v-model="newEntry.activity_type"
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
              v-model="newEntry.description"
              placeholder="What did you work on today?"
              fill="outline"
              :rows="3"
              required
            />
          </div>

          <!-- Notes -->
          <div class="mb-4">
            <ion-label class="block text-sm font-medium text-gray-700 mb-1">
              Additional Notes
            </ion-label>
            <ion-textarea
              v-model="newEntry.notes"
              placeholder="Any additional notes..."
              fill="outline"
              :rows="2"
            />
          </div>

          <!-- Submit Button -->
          <ion-button
            expand="block"
            type="submit"
            :disabled="submitting"
            class="mt-6"
          >
            <ion-spinner v-if="submitting" name="crescent" class="mr-2" />
            {{ submitting ? "Saving..." : "Save Timesheet" }}
          </ion-button>

          <div v-if="error" class="mt-4 p-3 bg-red-50 text-red-600 rounded-lg text-sm">
            {{ error }}
          </div>
        </form>
      </ion-content>
    </ion-modal>
  </ion-page>
</template>

<script setup>
import { ref, computed, onMounted, inject } from "vue"
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
  IonModal,
  IonInput,
  IonTextarea,
  IonLabel,
  IonSpinner,
  IonSelect,
  IonSelectOption,
  IonSegment,
  IonSegmentButton,
  toastController,
} from "@ionic/vue"
import { addOutline, timeOutline, calendarOutline, folderOutline } from "ionicons/icons"
import { call } from "frappe-ui"

const $dayjs = inject("$dayjs")

const loading = ref(true)
const showAddModal = ref(false)
const submitting = ref(false)
const submittingId = ref(null)
const error = ref("")
const filter = ref("all")
const timeSheets = ref([])
const myTasks = ref([])
const todaySummary = ref({ total_hours: 0, tasks_worked: 0, timesheets: [] })

const filteredTimeSheets = computed(() => {
  if (filter.value === "all") return timeSheets.value
  if (filter.value === "draft") {
    return timeSheets.value.filter((t) => t.status === "Draft")
  }
  if (filter.value === "submitted") {
    return timeSheets.value.filter((t) => t.status === "Submitted")
  }
  if (filter.value === "approved") {
    return timeSheets.value.filter((t) => t.status === "Approved")
  }
  return timeSheets.value
})

const newEntry = ref({
  task: "",
  date: "",
  hours_worked: "",
  activity_type: "Development",
  description: "",
  notes: "",
})

async function loadData() {
  loading.value = true
  try {
    const [timesheetsResult, tasksResult, summaryResult] = await Promise.all([
      call("smart_pro.smart_pro.api.projects.get_my_timesheets"),
      call("smart_pro.smart_pro.api.projects.get_user_tasks"),
      call("smart_pro.smart_pro.api.projects.get_today_summary"),
    ])
    timeSheets.value = timesheetsResult || []
    myTasks.value = (tasksResult || []).filter(t => t.status !== "Completed")
    todaySummary.value = summaryResult || { total_hours: 0, tasks_worked: 0 }
  } catch (err) {
    console.error("Error loading data:", err)
    error.value = err.messages?.[0] || err.message || "Failed to load data"
  } finally {
    loading.value = false
  }
}

function openAddModal() {
  newEntry.value = {
    task: "",
    date: $dayjs().format("YYYY-MM-DD"),
    hours_worked: "",
    activity_type: "Development",
    description: "",
    notes: "",
  }
  error.value = ""
  showAddModal.value = true
}

async function submitTimeSheet() {
  if (!newEntry.value.task || !newEntry.value.date || !newEntry.value.hours_worked || !newEntry.value.description) {
    error.value = "Task, date, hours, and description are required"
    return
  }

  submitting.value = true
  error.value = ""

  try {
    await call("smart_pro.smart_pro.api.projects.create_timesheet", {
      task: newEntry.value.task,
      date: newEntry.value.date,
      hours_worked: parseFloat(newEntry.value.hours_worked),
      description: newEntry.value.description,
      activity_type: newEntry.value.activity_type,
      notes: newEntry.value.notes || null,
    })

    const toast = await toastController.create({
      message: "Timesheet saved successfully!",
      duration: 2000,
      color: "success",
    })
    await toast.present()

    showAddModal.value = false
    await loadData()
  } catch (err) {
    console.error("Error saving timesheet:", err)
    error.value = err.messages?.[0] || err.message || "Failed to save timesheet"
  } finally {
    submitting.value = false
  }
}

async function submitTimesheet(timesheetName) {
  submittingId.value = timesheetName
  try {
    await call("smart_pro.smart_pro.api.projects.submit_timesheet", {
      timesheet_name: timesheetName,
    })

    const toast = await toastController.create({
      message: "Timesheet submitted for approval!",
      duration: 2000,
      color: "success",
    })
    await toast.present()

    await loadData()
  } catch (err) {
    console.error("Error submitting timesheet:", err)
    const toast = await toastController.create({
      message: err.messages?.[0] || "Failed to submit timesheet",
      duration: 3000,
      color: "danger",
    })
    await toast.present()
  } finally {
    submittingId.value = null
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

function stripHtml(html) {
  if (!html) return ""
  return html.replace(/<[^>]*>/g, "")
}

function getStatusClass(status) {
  const map = {
    Draft: "planning",
    Submitted: "on-hold",
    Approved: "completed",
    Rejected: "cancelled",
  }
  return map[status] || ""
}

onMounted(() => {
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

.skeleton {
  background-color: #e5e7eb;
  border-radius: 0.25rem;
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}
</style>
