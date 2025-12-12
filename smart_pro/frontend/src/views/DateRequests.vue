<template>
  <ion-page>
    <ion-header>
      <ion-toolbar>
        <ion-buttons slot="start">
          <ion-back-button default-href="/smart-pro/home" text="" />
        </ion-buttons>
        <ion-title>Date Requests</ion-title>
      </ion-toolbar>
      <ion-toolbar>
        <ion-segment v-model="filter" scrollable>
          <ion-segment-button value="all">
            <ion-label>All</ion-label>
          </ion-segment-button>
          <ion-segment-button value="pending">
            <ion-label>Pending</ion-label>
          </ion-segment-button>
          <ion-segment-button value="approved">
            <ion-label>Approved</ion-label>
          </ion-segment-button>
          <ion-segment-button value="rejected">
            <ion-label>Rejected</ion-label>
          </ion-segment-button>
        </ion-segment>
      </ion-toolbar>
    </ion-header>

    <ion-content :fullscreen="true">
      <ion-refresher slot="fixed" @ion-refresh="handleRefresh">
        <ion-refresher-content />
      </ion-refresher>

      <!-- Loading State -->
      <div v-if="loading" class="p-4">
        <div v-for="i in 3" :key="i" class="app-card mb-4 p-4">
          <div class="skeleton h-5 w-3/4 mb-2" />
          <div class="skeleton h-4 w-1/2 mb-2" />
          <div class="skeleton h-3 w-full" />
        </div>
      </div>

      <!-- Empty State -->
      <div v-else-if="filteredRequests.length === 0" class="empty-state h-full">
        <ion-icon :icon="calendarOutline" class="empty-state-icon" />
        <div class="empty-state-title">No date requests</div>
        <div class="empty-state-description">
          {{ filter === "pending" ? "No pending requests" : filter === "approved" ? "No approved requests" : filter === "rejected" ? "No rejected requests" : "Your date requests will appear here" }}
        </div>
      </div>

      <!-- Date Requests List -->
      <div v-else class="p-4">
        <div v-for="request in filteredRequests" :key="request.name" class="app-card mb-4 p-4">
          <div class="flex justify-between items-start mb-2">
            <div>
              <span class="text-xs text-gray-500 uppercase">{{ request.request_type }}</span>
              <h3 class="font-semibold text-gray-800">
                {{ request.project_title || request.project || 'General Request' }}
              </h3>
            </div>
            <span :class="['status-badge', getStatusClass(request.status)]">
              {{ request.status }}
            </span>
          </div>

          <div class="flex items-center text-sm text-gray-600 mb-2">
            <ion-icon :icon="calendarOutline" class="mr-1" />
            {{ formatDate(request.from_date) }} - {{ formatDate(request.to_date) }}
            <span class="ml-2 text-blue-600">({{ request.total_days }} days)</span>
          </div>

          <div v-if="request.reason" class="text-sm text-gray-600 mb-2 line-clamp-2">
            {{ stripHtml(request.reason) }}
          </div>

          <!-- Project Scope (Expandable) -->
          <div v-if="request.project_scope" class="mb-2 bg-blue-50 rounded text-sm overflow-hidden">
            <div
              class="flex items-center justify-between p-2 cursor-pointer"
              @click="toggleScope(request.name)"
            >
              <div class="text-xs text-blue-600 font-semibold">Project Scope:</div>
              <ion-icon
                :icon="expandedScopes[request.name] ? chevronUpOutline : chevronDownOutline"
                class="text-blue-600"
              />
            </div>
            <div
              class="scope-content px-2 pb-2"
              :class="{ 'expanded': expandedScopes[request.name] }"
            >
              <div class="text-gray-700 whitespace-pre-wrap" v-html="request.project_scope" />
            </div>
          </div>

          <div v-if="request.approver" class="text-xs text-gray-500">
            <ion-icon :icon="personOutline" class="mr-1" />
            Approver: {{ request.approver }}
          </div>

          <div v-if="request.comments && request.status !== 'Pending Approval'" class="mt-2 p-2 bg-gray-50 rounded text-sm">
            <span class="font-medium">Comments:</span> {{ stripHtml(request.comments) }}
          </div>

          <!-- Auto Create Tasks indicator -->
          <div v-if="request.auto_create_tasks && request.request_type === 'Project Date Update'" class="mt-2 text-xs text-green-600">
            <ion-icon :icon="checkmarkCircleOutline" class="mr-1" />
            Tasks will be auto-created on approval
          </div>

          <!-- Action Buttons for Pending Requests -->
          <div v-if="request.status === 'Pending Approval'" class="mt-3 pt-3 border-t border-gray-100">
            <div class="flex flex-wrap gap-2">
              <!-- Edit Dates Button -->
              <ion-button size="small" fill="outline" color="primary" @click="openEditModal(request)">
                <ion-icon :icon="createOutline" slot="start" />
                Edit Dates
              </ion-button>
              <!-- Approve Button -->
              <ion-button size="small" fill="solid" color="success" @click="approveRequest(request)">
                <ion-icon :icon="checkmarkOutline" slot="start" />
                Approve
              </ion-button>
              <!-- Reject Button -->
              <ion-button size="small" fill="outline" color="danger" @click="rejectRequest(request)">
                <ion-icon :icon="closeOutline" slot="start" />
                Reject
              </ion-button>
            </div>
          </div>
        </div>
      </div>
    </ion-content>

    <!-- Edit Date Request Modal -->
    <ion-modal :is-open="showEditModal" @did-dismiss="showEditModal = false">
      <ion-header>
        <ion-toolbar>
          <ion-title>Edit Dates</ion-title>
          <ion-buttons slot="end">
            <ion-button @click="showEditModal = false">Close</ion-button>
          </ion-buttons>
        </ion-toolbar>
      </ion-header>
      <ion-content class="ion-padding">
        <form @submit.prevent="updateRequest">
          <!-- From Date -->
          <div class="mb-4">
            <ion-label class="block text-sm font-medium text-gray-700 mb-1">
              From Date *
            </ion-label>
            <ion-input
              v-model="editRequest.from_date"
              type="date"
              fill="outline"
              required
            />
          </div>

          <!-- To Date -->
          <div class="mb-4">
            <ion-label class="block text-sm font-medium text-gray-700 mb-1">
              To Date *
            </ion-label>
            <ion-input
              v-model="editRequest.to_date"
              type="date"
              fill="outline"
              required
            />
          </div>

          <!-- Calculated Days -->
          <div v-if="editCalculatedDays > 0" class="mb-4 p-3 bg-blue-50 rounded-lg">
            <span class="text-blue-800 font-medium">Total: {{ editCalculatedDays }} days</span>
          </div>

          <!-- Reason/Description -->
          <div class="mb-4">
            <ion-label class="block text-sm font-medium text-gray-700 mb-1">
              Reason / Work Description
            </ion-label>
            <ion-textarea
              v-model="editRequest.reason"
              placeholder="Update reason if needed..."
              fill="outline"
              :rows="4"
            />
          </div>

          <!-- Update Button -->
          <ion-button
            expand="block"
            type="submit"
            :disabled="updating"
            class="mt-6"
          >
            <ion-spinner v-if="updating" name="crescent" class="mr-2" />
            {{ updating ? "Updating..." : "Update Request" }}
          </ion-button>

          <div v-if="editError" class="mt-4 p-3 bg-red-50 text-red-600 rounded-lg text-sm">
            {{ editError }}
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
  IonSegment,
  IonSegmentButton,
  toastController,
  onIonViewWillEnter,
} from "@ionic/vue"
import { calendarOutline, personOutline, checkmarkCircleOutline, createOutline, checkmarkOutline, closeOutline, chevronDownOutline, chevronUpOutline } from "ionicons/icons"
import { call } from "frappe-ui"
import { usePermissions } from "@/composables/usePermissions"

const $dayjs = inject("$dayjs")
const { fetchPermissions, hasFullAccess } = usePermissions()

const loading = ref(true)
const showEditModal = ref(false)
const updating = ref(false)
const editError = ref("")
const filter = ref("pending")
const dateRequests = ref([])
const currentUser = ref("")
const expandedScopes = ref({})

function toggleScope(requestName) {
  expandedScopes.value[requestName] = !expandedScopes.value[requestName]
}

const filteredRequests = computed(() => {
  if (filter.value === "all") return dateRequests.value
  if (filter.value === "pending") {
    return dateRequests.value.filter((r) => r.status === "Pending Approval")
  }
  if (filter.value === "approved") {
    return dateRequests.value.filter((r) => r.status === "Approved")
  }
  if (filter.value === "rejected") {
    return dateRequests.value.filter((r) => r.status === "Rejected")
  }
  return dateRequests.value
})

const editRequest = ref({
  name: "",
  from_date: "",
  to_date: "",
  reason: "",
})

const editCalculatedDays = computed(() => {
  if (!editRequest.value.from_date || !editRequest.value.to_date) return 0
  const from = $dayjs(editRequest.value.from_date)
  const to = $dayjs(editRequest.value.to_date)
  if (to.isBefore(from)) return 0
  return to.diff(from, "day") + 1
})

// Cache timestamp to avoid unnecessary reloads
let lastLoadTime = 0
const CACHE_TTL = 30000 // 30 seconds

async function loadData(forceRefresh = false) {
  const now = Date.now()

  // Skip reload if data is fresh (unless forced)
  if (!forceRefresh && lastLoadTime && (now - lastLoadTime) < CACHE_TTL && dateRequests.value.length > 0) {
    return
  }

  loading.value = dateRequests.value.length === 0 // Only show loading on first load
  try {
    // Fetch permissions first
    await fetchPermissions()

    // For full access users, get all date requests; otherwise get user's requests
    let requestsResult
    if (hasFullAccess.value) {
      requestsResult = await call("smart_pro.smart_pro.api.projects.get_all_date_requests")
    } else {
      requestsResult = await call("smart_pro.smart_pro.api.projects.get_my_date_requests")
    }

    const userResult = await call("frappe.auth.get_logged_user")
    dateRequests.value = requestsResult || []
    currentUser.value = userResult || ""
    lastLoadTime = now
  } catch (err) {
    console.error("Error loading data:", err)
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

function stripHtml(html) {
  if (!html) return ""
  return html.replace(/<[^>]*>/g, "")
}

function getStatusClass(status) {
  const map = {
    Draft: "planning",
    "Pending Approval": "on-hold",
    Approved: "completed",
    Rejected: "cancelled",
    Cancelled: "cancelled",
  }
  return map[status] || ""
}

function openEditModal(request) {
  editRequest.value = {
    name: request.name,
    from_date: request.from_date,
    to_date: request.to_date,
    reason: stripHtml(request.reason || ""),
  }
  editError.value = ""
  showEditModal.value = true
}

async function updateRequest() {
  if (!editRequest.value.from_date || !editRequest.value.to_date) {
    editError.value = "From date and to date are required"
    return
  }

  const from = $dayjs(editRequest.value.from_date)
  const to = $dayjs(editRequest.value.to_date)
  if (to.isBefore(from)) {
    editError.value = "To date cannot be before from date"
    return
  }

  updating.value = true
  editError.value = ""

  try {
    await call("smart_pro.smart_pro.api.projects.update_date_request", {
      request_id: editRequest.value.name,
      from_date: editRequest.value.from_date,
      to_date: editRequest.value.to_date,
      reason: editRequest.value.reason || null,
    })

    const toast = await toastController.create({
      message: "Date request updated successfully!",
      duration: 2000,
      color: "success",
    })
    await toast.present()

    showEditModal.value = false
    await loadData()
  } catch (err) {
    console.error("Error updating request:", err)
    editError.value = err.messages?.[0] || err.message || "Failed to update request"
  } finally {
    updating.value = false
  }
}

async function approveRequest(request) {
  try {
    await call("smart_pro.smart_pro.api.projects.approve_date_request", {
      request_id: request.name,
      status: "Approved",
    })

    const toast = await toastController.create({
      message: "Request approved successfully!",
      duration: 2000,
      color: "success",
    })
    await toast.present()

    await loadData()
  } catch (err) {
    console.error("Error approving request:", err)
    const toast = await toastController.create({
      message: err.messages?.[0] || err.message || "Failed to approve request",
      duration: 3000,
      color: "danger",
    })
    await toast.present()
  }
}

async function rejectRequest(request) {
  try {
    await call("smart_pro.smart_pro.api.projects.approve_date_request", {
      request_id: request.name,
      status: "Rejected",
    })

    const toast = await toastController.create({
      message: "Request rejected",
      duration: 2000,
      color: "warning",
    })
    await toast.present()

    await loadData()
  } catch (err) {
    console.error("Error rejecting request:", err)
    const toast = await toastController.create({
      message: err.messages?.[0] || err.message || "Failed to reject request",
      duration: 3000,
      color: "danger",
    })
    await toast.present()
  }
}

onMounted(() => {
  loadData()
})

// Reload data when navigating back to this tab
onIonViewWillEnter(() => {
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

.line-clamp-3 {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* Expandable Scope Styles */
.scope-content {
  max-height: 60px;
  overflow: hidden;
  transition: max-height 0.3s ease-out;
}

.scope-content.expanded {
  max-height: 1000px;
  transition: max-height 0.5s ease-in;
}

.scope-content:not(.expanded) > div {
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
