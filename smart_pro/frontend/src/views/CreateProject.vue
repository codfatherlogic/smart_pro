<template>
  <ion-page>
    <ion-header>
      <ion-toolbar>
        <template #start>
          <ion-buttons>
            <ion-back-button default-href="/smart-pro/projects" />
          </ion-buttons>
        </template>
        <ion-title>New Project</ion-title>
      </ion-toolbar>
    </ion-header>

    <ion-content :fullscreen="true">
      <div class="p-4">
        <form @submit.prevent="handleSubmit">
          <!-- Project Title -->
          <div class="mb-4">
            <ion-label class="block text-sm font-medium text-gray-700 mb-1">
              Project Title *
            </ion-label>
            <ion-input
              v-model="form.title"
              type="text"
              placeholder="Enter project title"
              fill="outline"
              required
            />
          </div>

          <!-- Description -->
          <div class="mb-4">
            <ion-label class="block text-sm font-medium text-gray-700 mb-1">
              Description
            </ion-label>
            <ion-textarea
              v-model="form.description"
              placeholder="Enter project description"
              fill="outline"
              :rows="3"
            />
          </div>

          <!-- Status -->
          <div class="mb-4">
            <ion-label class="block text-sm font-medium text-gray-700 mb-1">
              Status
            </ion-label>
            <ion-select
              v-model="form.status"
              fill="outline"
              interface="action-sheet"
            >
              <ion-select-option value="Planning">
                Planning
              </ion-select-option>
              <ion-select-option value="Active">
                Active
              </ion-select-option>
              <ion-select-option value="On Hold">
                On Hold
              </ion-select-option>
              <ion-select-option value="Completed">
                Completed
              </ion-select-option>
              <ion-select-option value="Cancelled">
                Cancelled
              </ion-select-option>
            </ion-select>
          </div>

          <!-- Start Date -->
          <div class="mb-4">
            <ion-label class="block text-sm font-medium text-gray-700 mb-1">
              Start Date
            </ion-label>
            <ion-input
              v-model="form.start_date"
              type="date"
              fill="outline"
            />
          </div>

          <!-- End Date -->
          <div class="mb-4">
            <ion-label class="block text-sm font-medium text-gray-700 mb-1">
              End Date
            </ion-label>
            <ion-input
              v-model="form.end_date"
              type="date"
              fill="outline"
            />
          </div>

          <!-- Budget -->
          <div class="mb-4">
            <ion-label class="block text-sm font-medium text-gray-700 mb-1">
              Budget Amount
            </ion-label>
            <ion-input
              v-model="form.budget_amount"
              type="number"
              placeholder="0.00"
              fill="outline"
            />
          </div>

          <!-- Submit Button -->
          <ion-button
            expand="block"
            type="submit"
            :disabled="saving || !form.title"
            class="mt-6"
          >
            <ion-spinner
              v-if="saving"
              name="crescent"
              class="mr-2"
            />
            {{ saving ? "Creating..." : "Create Project" }}
          </ion-button>
        </form>

        <div
          v-if="error"
          class="mt-4 p-3 bg-red-50 text-red-600 rounded-lg text-sm"
        >
          {{ error }}
        </div>
      </div>
    </ion-content>
  </ion-page>
</template>

<script setup>
import { ref, inject } from "vue"
import { useRouter } from "vue-router"
import {
  IonPage,
  IonHeader,
  IonToolbar,
  IonTitle,
  IonContent,
  IonButtons,
  IonBackButton,
  IonButton,
  IonInput,
  IonTextarea,
  IonLabel,
  IonSelect,
  IonSelectOption,
  IonSpinner,
  toastController,
} from "@ionic/vue"
import { call } from "frappe-ui"

const router = useRouter()
const $dayjs = inject("$dayjs")

const saving = ref(false)
const error = ref("")

const form = ref({
  title: "",
  description: "",
  status: "Planning",
  start_date: $dayjs().format("YYYY-MM-DD"),
  end_date: "",
  budget_amount: "",
})

async function handleSubmit() {
  if (!form.value.title) {
    error.value = "Project title is required"
    return
  }

  saving.value = true
  error.value = ""

  try {
    const result = await call("frappe.client.insert", {
      doc: {
        doctype: "Smart Project",
        title: form.value.title,
        description: form.value.description,
        status: form.value.status,
        start_date: form.value.start_date || null,
        end_date: form.value.end_date || null,
        budget_amount: form.value.budget_amount ? parseFloat(form.value.budget_amount) : 0,
      },
    })

    const toast = await toastController.create({
      message: "Project created successfully!",
      duration: 2000,
      color: "success",
    })
    await toast.present()

    // Navigate to the new project
    router.replace(`/smart-pro/project/${encodeURIComponent(result.name)}`)
  } catch (err) {
    console.error("Error creating project:", err)
    error.value = err.messages?.[0] || err.message || "Failed to create project"
  } finally {
    saving.value = false
  }
}
</script>
