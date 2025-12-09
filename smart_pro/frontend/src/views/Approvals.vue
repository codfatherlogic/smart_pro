<template>
  <ion-page>
    <ion-header>
      <ion-toolbar>
        <ion-buttons slot="start">
          <ion-back-button default-href="/smart-pro/home" text="" />
        </ion-buttons>
        <ion-title>Approvals</ion-title>
        <ion-buttons slot="end">
          <ion-button @click="refreshData">
            <ion-icon :icon="refreshOutline" />
          </ion-button>
        </ion-buttons>
      </ion-toolbar>
      <ion-toolbar>
        <ion-segment v-model="approvalType">
          <ion-segment-button value="date_requests">
            <ion-label>Date Requests</ion-label>
          </ion-segment-button>
          <ion-segment-button value="timesheets">
            <ion-label>Time Sheets</ion-label>
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
          v-for="i in 3"
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
        v-else-if="approvalType === 'date_requests' && dateRequests.length === 0"
        class="empty-state h-full"
      >
        <ion-icon
          :icon="checkmarkDoneOutline"
          class="empty-state-icon"
        />
        <div class="empty-state-title">
          No pending date requests
        </div>
        <div class="empty-state-description">
          All date requests have been approved or rejected
        </div>
      </div>

      <div
        v-else-if="approvalType === 'timesheets' && timeSheets.length === 0"
        class="empty-state h-full"
      >
        <ion-icon
          :icon="timeOutline"
          class="empty-state-icon"
        />
        <div class="empty-state-title">
          No pending time sheets
        </div>
        <div class="empty-state-description">
          All time sheets have been approved or rejected
        </div>
      </div>

      <!-- Date Requests List -->
      <div
        v-else-if="approvalType === 'date_requests'"
        class="p-4"
      >
        <div
          v-for="request in dateRequests"
          :key="request.name"
          class="app-card mb-4 p-4"
        >
          <div class="flex justify-between items-start mb-2">
            <div>
              <h3 class="font-semibold text-gray-800">
                {{ request.employee_name }}
              </h3>
              <div class="text-sm text-gray-500">
                {{ request.request_type }}
              </div>
            </div>
            <span class="status-badge pending">
              Pending
            </span>
          </div>

          <div class="text-sm text-gray-600 mb-3">
            <div class="flex items-center mb-1">
              <ion-icon
                :icon="calendarOutline"
                class="mr-2"
              />
              {{ formatDate(request.from_date) }} - {{ formatDate(request.to_date) }}
            </div>
            <div
              v-if="request.project_title"
              class="mt-1 text-blue-600"
            >
              <strong>Project:</strong> {{ request.project_title }}
            </div>
            <div
              v-if="request.reason"
              class="mt-2 line-clamp-3"
            >
              <strong>Reason:</strong> {{ stripHtml(request.reason) }}
            </div>
            <div
              v-if="request.auto_create_tasks"
              class="mt-2 text-xs text-green-600"
            >
              Tasks will be auto-created on approval
            </div>
          </div>

          <div class="flex space-x-2">
            <ion-button
              expand="block"
              color="success"
              size="small"
              :disabled="processingRequest === request.name"
              @click="approveRequest(request.name)"
            >
              <ion-spinner
                v-if="processingRequest === request.name"
                name="crescent"
                class="mr-2"
              />
              Approve
            </ion-button>
            <ion-button
              expand="block"
              color="danger"
              size="small"
              :disabled="processingRequest === request.name"
              @click="rejectRequest(request.name)"
            >
              <ion-spinner
                v-if="processingRequest === request.name"
                name="crescent"
                class="mr-2"
              />
              Reject
            </ion-button>
            <ion-button
              expand="block"
              color="medium"
              size="small"
              @click="viewDetails(request)"
            >
              Details
            </ion-button>
          </div>
        </div>
      </div>

      <!-- Time Sheets List -->
      <div
        v-else
        class="p-4"
      >
        <div
          v-for="timesheet in timeSheets"
          :key="timesheet.name"
          class="app-card mb-4 p-4"
        >
          <div class="flex justify-between items-start mb-2">
            <div>
              <h3 class="font-semibold text-gray-800">
                {{ timesheet.employee || 'Employee' }}
              </h3>
              <div class="text-sm text-gray-500">
                {{ timesheet.task || 'General Work' }}
              </div>
            </div>
            <span :class="['status-badge', getTimesheetStatusClass(timesheet.status)]">
              {{ timesheet.status }}
            </span>
          </div>

          <div class="text-sm text-gray-600 mb-3">
            <div class="flex items-center mb-1">
              <ion-icon
                :icon="calendarOutline"
                class="mr-2"
              />
              {{ formatDate(timesheet.date) }}
            </div>
            <div class="flex items-center">
              <ion-icon
                :icon="timeOutline"
                class="mr-2"
              />
              {{ timesheet.hours_worked }} hours
            </div>
            <div
              v-if="timesheet.project"
              class="mt-1"
            >
              <strong>Project:</strong> {{ timesheet.project }}
            </div>
          </div>

          <div class="flex space-x-2">
            <ion-button
              v-if="timesheet.status === 'Submitted'"
              expand="block"
              color="success"
              size="small"
              :disabled="processingTimesheet === timesheet.name"
              @click="approveTimesheet(timesheet.name)"
            >
              <ion-spinner
                v-if="processingTimesheet === timesheet.name"
                name="crescent"
                class="mr-2"
              />
              Approve
            </ion-button>
            <ion-button
              v-if="timesheet.status === 'Submitted'"
              expand="block"
              color="danger"
              size="small"
              :disabled="processingTimesheet === timesheet.name"
              @click="rejectTimesheet(timesheet.name)"
            >
              <ion-spinner
                v-if="processingTimesheet === timesheet.name"
                name="crescent"
                class="mr-2"
              />
              Reject
            </ion-button>
            <ion-button
              expand="block"
              color="medium"
              size="small"
              @click="viewTimesheetDetails(timesheet)"
            >
              Details
            </ion-button>
          </div>
        </div>
      </div>
    </ion-content>
  </ion-page>
</template>

<script setup>
import { ref, onMounted, watch } from "vue"
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
  IonSegment,
  IonSegmentButton,
  IonLabel,
  IonSpinner,
  toastController,
} from "@ionic/vue"
import {
  refreshOutline,
  calendarOutline,
  timeOutline,
  checkmarkDoneOutline,
} from "ionicons/icons"
import { call } from "frappe-ui"

const loading = ref(true)
const approvalType = ref("date_requests")
const dateRequests = ref([])
const timeSheets = ref([])
const processingRequest = ref("")
const processingTimesheet = ref("")

async function loadDateRequests() {
  try {
    const result = await call("smart_pro.smart_pro.api.projects.get_pending_approvals")
    dateRequests.value = result?.date_requests || []
  } catch (err) {
    console.error("Error loading date requests:", err)
  }
}

async function loadTimeSheets() {
  try {
    const result = await call("smart_pro.smart_pro.api.projects.get_team_time_sheets")
    // Filter for pending time sheets (status = "Submitted")
    timeSheets.value = (result || []).filter(ts => ts.status === "Submitted")
  } catch (err) {
    console.error("Error loading time sheets:", err)
  }
}

async function loadData() {
  loading.value = true
  await Promise.all([loadDateRequests(), loadTimeSheets()])
  loading.value = false
}

async function approveRequest(requestId) {
  processingRequest.value = requestId
  try {
    await call("smart_pro.smart_pro.api.projects.approve_date_request", {
      request_id: requestId,
      status: "Approved",
    })

    const toast = await toastController.create({
      message: "Request approved successfully!",
      duration: 2000,
      color: "success",
    })
    await toast.present()

    // Remove from list
    dateRequests.value = dateRequests.value.filter(req => req.name !== requestId)
  } catch (err) {
    console.error("Error approving request:", err)
    const toast = await toastController.create({
      message: err.messages?.[0] || "Failed to approve request",
      duration: 3000,
      color: "danger",
    })
    await toast.present()
  } finally {
    processingRequest.value = ""
  }
}

async function rejectRequest(requestId) {
  processingRequest.value = requestId
  try {
    await call("smart_pro.smart_pro.api.projects.approve_date_request", {
      request_id: requestId,
      status: "Rejected",
    })

    const toast = await toastController.create({
      message: "Request rejected successfully!",
      duration: 2000,
      color: "warning",
    })
    await toast.present()

    // Remove from list
    dateRequests.value = dateRequests.value.filter(req => req.name !== requestId)
  } catch (err) {
    console.error("Error rejecting request:", err)
    const toast = await toastController.create({
      message: err.messages?.[0] || "Failed to reject request",
      duration: 3000,
      color: "danger",
    })
    await toast.present()
  } finally {
    processingRequest.value = ""
  }
}

async function approveTimesheet(timesheetId) {
  processingTimesheet.value = timesheetId
  try {
    await call("frappe.client.set_value", {
      doctype: "Smart Time Sheet",
      name: timesheetId,
      fieldname: {
        status: "Approved",
      },
    })

    const toast = await toastController.create({
      message: "Time sheet approved successfully!",
      duration: 2000,
      color: "success",
    })
    await toast.present()

    // Remove from list
    timeSheets.value = timeSheets.value.filter(ts => ts.name !== timesheetId)
  } catch (err) {
    console.error("Error approving time sheet:", err)
    const toast = await toastController.create({
      message: err.messages?.[0] || "Failed to approve time sheet",
      duration: 3000,
      color: "danger",
    })
    await toast.present()
  } finally {
    processingTimesheet.value = ""
  }
}

async function rejectTimesheet(timesheetId) {
  processingTimesheet.value = timesheetId
  try {
    await call("frappe.client.set_value", {
      doctype: "Smart Time Sheet",
      name: timesheetId,
      fieldname: {
        status: "Rejected",
      },
    })

    const toast = await toastController.create({
      message: "Time sheet rejected successfully!",
      duration: 2000,
      color: "warning",
    })
    await toast.present()

    // Remove from list
    timeSheets.value = timeSheets.value.filter(ts => ts.name !== timesheetId)
  } catch (err) {
    console.error("Error rejecting time sheet:", err)
    const toast = await toastController.create({
      message: err.messages?.[0] || "Failed to reject time sheet",
      duration: 3000,
      color: "danger",
    })
    await toast.present()
  } finally {
    processingTimesheet.value = ""
  }
}

function viewDetails(request) {
  // For now, just show an alert
  alert(`Request Details:\nEmployee: ${request.employee_name}\nType: ${request.request_type}\nDates: ${formatDate(request.from_date)} to ${formatDate(request.to_date)}\nReason: ${request.reason || 'None'}`)
}

function viewTimesheetDetails(timesheet) {
  alert(`Time Sheet Details:\nEmployee: ${timesheet.employee}\nDate: ${formatDate(timesheet.date)}\nHours: ${timesheet.hours_worked}\nTask: ${timesheet.task || 'None'}\nProject: ${timesheet.project || 'None'}`)
}

function formatDate(dateStr) {
  if (!dateStr) return "-"
  const date = new Date(dateStr)
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

function stripHtml(html) {
  if (!html) return ""
  return html.replace(/<[^>]*>/g, "")
}

function getTimesheetStatusClass(status) {
  const map = {
    Draft: "planning",
    Submitted: "pending",
    Approved: "completed",
    Rejected: "cancelled",
  }
  return map[status] || ""
}

function handleRefresh(event) {
  loadData().finally(() => {
    event.target.complete()
  })
}

function refreshData() {
  loadData()
}

watch(approvalType, () => {
  // Optional: Load data when switching tabs
})

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

.status-badge.pending {
  background-color: #fef3c7;
  color: #92400e;
}

.status-badge.planning {
  background-color: #e0f2fe;
  color: #0369a1;
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