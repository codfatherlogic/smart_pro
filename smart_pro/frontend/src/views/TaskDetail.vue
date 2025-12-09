<template>
  <ion-page>
    <ion-header>
      <ion-toolbar>
        <ion-buttons slot="start">
          <ion-back-button default-href="/smart-pro/tasks" text="" />
        </ion-buttons>
        <ion-title>Task Details</ion-title>
        <ion-buttons slot="end">
          <ion-button @click="openActions">
            <ion-icon :icon="ellipsisVertical" />
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

      <!-- Loading State -->
      <div
        v-if="loading"
        class="p-4"
      >
        <div class="skeleton h-8 w-3/4 mb-4" />
        <div class="skeleton h-4 w-1/2 mb-6" />
        <div class="skeleton h-24 w-full mb-4" />
      </div>

      <!-- Error State -->
      <div
        v-else-if="error"
        class="empty-state h-full"
      >
        <div class="empty-state-title">
          Error loading task
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

      <!-- Task Details -->
      <div
        v-else-if="task"
        class="p-4"
      >
        <!-- Header -->
        <div class="mb-6">
          <div class="flex justify-between items-start mb-2">
            <h1 class="text-2xl font-bold text-gray-800 flex-1 pr-2">
              {{ task.title }}
            </h1>
            <span :class="['status-badge', getStatusClass(task.status)]">
              {{ task.status }}
            </span>
          </div>
          <p
            v-if="task.description"
            class="text-gray-600"
          >
            {{ task.description }}
          </p>
        </div>

        <!-- Progress -->
        <div class="app-card p-4 mb-6">
          <div class="flex justify-between items-center mb-2">
            <span class="font-medium">Progress</span>
            <span class="text-primary-600 font-bold">{{ task.progress || 0 }}%</span>
          </div>
          <div class="progress-bar h-3">
            <div
              class="progress-bar-fill"
              :style="{ width: (task.progress || 0) + '%' }"
            />
          </div>
          <ion-button
            expand="block"
            fill="outline"
            class="mt-4"
            @click="updateProgress"
          >
            Update Progress
          </ion-button>
        </div>

        <!-- Project Scope Card -->
        <div v-if="task.project_scope" class="app-card p-4 mb-6">
          <div class="text-xs text-gray-500 mb-2 uppercase font-semibold">
            Project Scope
          </div>
          <div class="text-gray-700 prose prose-sm max-w-none" v-html="task.project_scope" />
        </div>

        <!-- Info Cards -->
        <div class="grid grid-cols-2 gap-4 mb-6">
          <div class="app-card p-4">
            <div class="text-xs text-gray-500 mb-1">
              Project
            </div>
            <div
              class="font-medium text-primary-600"
              @click="goToProject"
            >
              {{ task.project || "-" }}
            </div>
          </div>
          <div class="app-card p-4">
            <div class="text-xs text-gray-500 mb-1">
              Due Date
            </div>
            <div
              class="font-medium"
              :class="{ 'text-red-600': isOverdue }"
            >
              {{ formatDate(task.due_date) }}
            </div>
          </div>
          <div class="app-card p-4">
            <div class="text-xs text-gray-500 mb-1">
              Priority
            </div>
            <div :class="['font-medium', getPriorityClass(task.priority)]">
              {{ task.priority || "Normal" }}
            </div>
          </div>
          <div class="app-card p-4">
            <div class="text-xs text-gray-500 mb-1">
              Assigned To
            </div>
            <div class="font-medium">
              {{ task.assigned_to || "-" }}
            </div>
          </div>
        </div>

        <!-- Actions -->
        <div class="space-y-3">
          <ion-button
            v-if="task.status !== 'Completed'"
            expand="block"
            @click="markComplete"
          >
            Mark as Complete
          </ion-button>
          <ion-button
            v-if="task.status === 'Open'"
            expand="block"
            fill="outline"
            @click="startWorking"
          >
            Start Working
          </ion-button>
        </div>
      </div>
    </ion-content>
  </ion-page>
</template>

<script setup>
import { ref, computed, onMounted, inject } from "vue"
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
  actionSheetController,
  alertController,
  loadingController,
  toastController,
} from "@ionic/vue"
import { ellipsisVertical } from "ionicons/icons"
import { call } from "frappe-ui"

const route = useRoute()
const router = useRouter()
const $dayjs = inject("$dayjs")

const loading = ref(true)
const error = ref("")
const task = ref(null)

const isOverdue = computed(() => {
  if (!task.value?.due_date) return false
  return $dayjs(task.value.due_date).isBefore($dayjs(), "day")
})

async function loadData() {
  const taskId = route.params.id
  if (!taskId) {
    error.value = "Task not found"
    return
  }

  loading.value = true
  error.value = ""

  try {
    const result = await call("frappe.client.get", {
      doctype: "Smart Task",
      name: taskId,
    })
    task.value = result
  } catch (err) {
    console.error("Error loading task:", err)
    error.value = err.message || "Failed to load task"
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

function goToProject() {
  if (task.value?.project) {
    router.push(`/smart-pro/project/${encodeURIComponent(task.value.project)}`)
  }
}

async function updateProgress() {
  const alert = await alertController.create({
    header: "Update Progress",
    inputs: [
      {
        name: "progress",
        type: "number",
        placeholder: "Enter progress (0-100)",
        min: 0,
        max: 100,
        value: task.value?.progress || 0,
      },
    ],
    buttons: [
      { text: "Cancel", role: "cancel" },
      {
        text: "Update",
        handler: async (data) => {
          const progress = Math.min(100, Math.max(0, parseInt(data.progress) || 0))
          await saveTask({ progress })
        },
      },
    ],
  })
  await alert.present()
}

async function startWorking() {
  await saveTask({ status: "Working" })
}

async function markComplete() {
  const alert = await alertController.create({
    header: "Mark Complete",
    message: "Are you sure you want to mark this task as complete?",
    buttons: [
      { text: "Cancel", role: "cancel" },
      {
        text: "Complete",
        handler: async () => {
          await saveTask({ status: "Completed", progress: 100 })
        },
      },
    ],
  })
  await alert.present()
}

async function saveTask(updates) {
  const loader = await loadingController.create({ message: "Saving..." })
  await loader.present()

  try {
    await call("frappe.client.set_value", {
      doctype: "Smart Task",
      name: task.value.name,
      fieldname: updates,
    })

    // Update local state
    Object.assign(task.value, updates)

    const toast = await toastController.create({
      message: "Task updated successfully",
      duration: 2000,
      color: "success",
    })
    await toast.present()
  } catch (err) {
    console.error("Error saving task:", err)
    const toast = await toastController.create({
      message: "Failed to update task",
      duration: 2000,
      color: "danger",
    })
    await toast.present()
  } finally {
    await loader.dismiss()
  }
}

async function openActions() {
  const actionSheet = await actionSheetController.create({
    header: "Actions",
    buttons: [
      {
        text: "Open in Desktop",
        handler: () => {
          window.open(`/app/smart-task/${task.value.name}`, "_blank")
        },
      },
      {
        text: "Cancel",
        role: "cancel",
      },
    ],
  })
  await actionSheet.present()
}

onMounted(() => {
  loadData()
})
</script>
