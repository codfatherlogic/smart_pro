<template>
  <ion-page>
    <ion-header>
      <ion-toolbar>
        <ion-buttons slot="start">
          <ion-back-button
            :default-href="backUrl"
            text=""
          />
        </ion-buttons>
        <ion-title>New Assignment</ion-title>
      </ion-toolbar>
    </ion-header>

    <ion-content :fullscreen="true">
      <div class="p-4">
        <!-- Loading employees/roles -->
        <div v-if="loadingOptions" class="text-center py-8">
          <ion-spinner name="crescent" />
          <p class="text-gray-500 mt-2">Loading...</p>
        </div>

        <form v-else @submit.prevent="handleSubmit">
          <!-- Project (read-only if pre-filled) -->
          <div class="mb-4">
            <ion-label class="block text-sm font-medium text-gray-700 mb-1">
              Project *
            </ion-label>
            <ion-input
              v-if="projectName"
              :value="projectTitle || projectName"
              type="text"
              fill="outline"
              readonly
              disabled
            />
            <ion-select
              v-else
              v-model="form.project"
              fill="outline"
              interface="action-sheet"
              placeholder="Select Project"
            >
              <ion-select-option
                v-for="project in projects"
                :key="project.name"
                :value="project.name"
              >
                {{ project.title || project.name }}
              </ion-select-option>
            </ion-select>
          </div>

          <!-- Employee -->
          <div class="mb-4">
            <ion-label class="block text-sm font-medium text-gray-700 mb-1">
              Employee *
            </ion-label>
            <ion-select
              v-model="form.employee"
              fill="outline"
              interface="action-sheet"
              placeholder="Select Employee"
              @ionChange="onEmployeeChange"
            >
              <ion-select-option
                v-for="emp in employees"
                :key="emp.name"
                :value="emp.name"
              >
                {{ emp.employee_name }}
              </ion-select-option>
            </ion-select>
          </div>

          <!-- Role -->
          <div class="mb-4">
            <ion-label class="block text-sm font-medium text-gray-700 mb-1">
              Role *
            </ion-label>
            <ion-select
              v-model="form.role"
              fill="outline"
              interface="action-sheet"
              placeholder="Select Role"
            >
              <ion-select-option
                v-for="role in roles"
                :key="role.name"
                :value="role.name"
              >
                {{ role.name }}
              </ion-select-option>
            </ion-select>
          </div>

          <!-- Allocation Percentage -->
          <div class="mb-4">
            <ion-label class="block text-sm font-medium text-gray-700 mb-1">
              Allocation Percentage
            </ion-label>
            <ion-input
              v-model="form.allocation_percentage"
              type="number"
              placeholder="100"
              fill="outline"
              min="0"
              max="100"
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
              <ion-select-option value="Active">Active</ion-select-option>
              <ion-select-option value="On Hold">On Hold</ion-select-option>
              <ion-select-option value="Completed">Completed</ion-select-option>
              <ion-select-option value="Cancelled">Cancelled</ion-select-option>
            </ion-select>
          </div>

          <!-- Start Date -->
          <div class="mb-4">
            <ion-label class="block text-sm font-medium text-gray-700 mb-1">
              Start Date *
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

          <!-- Approver -->
          <div class="mb-4">
            <ion-label class="block text-sm font-medium text-gray-700 mb-1">
              Approver
            </ion-label>
            <ion-input
              v-model="form.approver"
              type="text"
              placeholder="Email of approver (optional)"
              fill="outline"
              readonly
            />
            <p class="text-xs text-gray-500 mt-1">
              Auto-filled from employee's user ID
            </p>
          </div>

          <!-- Project Scope -->
          <div class="mb-4">
            <ion-label class="block text-sm font-medium text-gray-700 mb-1">
              Project Scope
            </ion-label>
            <ion-textarea
              v-model="form.project_scope"
              placeholder="Detailed description of the project scope and deliverables for this assignment"
              fill="outline"
              :rows="4"
              :auto-grow="true"
            />
          </div>

          <!-- Submit Button -->
          <ion-button
            expand="block"
            type="submit"
            :disabled="saving || !isFormValid"
            class="mt-6"
          >
            <ion-spinner
              v-if="saving"
              name="crescent"
              class="mr-2"
            />
            {{ saving ? "Creating..." : "Create Assignment" }}
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
  IonInput,
  IonTextarea,
  IonLabel,
  IonSelect,
  IonSelectOption,
  IonSpinner,
  toastController,
} from "@ionic/vue"
import { call } from "frappe-ui"

const route = useRoute()
const router = useRouter()
const $dayjs = inject("$dayjs")

const projectName = route.query.project || ""
const projectTitle = ref("")
const backUrl = computed(() =>
  projectName ? `/smart-pro/project/${encodeURIComponent(projectName)}` : "/smart-pro/projects"
)

const saving = ref(false)
const loadingOptions = ref(true)
const error = ref("")

const employees = ref([])
const roles = ref([])
const projects = ref([])

const form = ref({
  project: projectName,
  employee: "",
  role: "",
  allocation_percentage: "100",
  status: "Active",
  start_date: $dayjs().format("YYYY-MM-DD"),
  end_date: "",
  approver: "",
  project_scope: "",
})

const isFormValid = computed(() => {
  return form.value.project && form.value.employee && form.value.role && form.value.start_date
})

async function loadOptions() {
  loadingOptions.value = true
  try {
    // Load employees, roles, and projects in parallel
    const [employeesResult, rolesResult, projectsResult] = await Promise.all([
      call("frappe.client.get_list", {
        doctype: "Employee",
        filters: { status: "Active" },
        fields: ["name", "employee_name", "user_id"],
        limit_page_length: 0,
        order_by: "employee_name asc",
      }),
      call("frappe.client.get_list", {
        doctype: "Smart Role",
        fields: ["name"],
        limit_page_length: 0,
        order_by: "name asc",
      }),
      call("frappe.client.get_list", {
        doctype: "Smart Project",
        filters: { status: ["!=", "Cancelled"] },
        fields: ["name", "title"],
        limit_page_length: 0,
        order_by: "title asc",
      }),
    ])

    employees.value = employeesResult || []
    roles.value = rolesResult || []
    projects.value = projectsResult || []

    // If project is pre-filled, get its title
    if (projectName) {
      const project = projects.value.find(p => p.name === projectName)
      if (project) {
        projectTitle.value = project.title
      }
    }
  } catch (err) {
    console.error("Error loading options:", err)
    error.value = "Failed to load form options"
  } finally {
    loadingOptions.value = false
  }
}

function onEmployeeChange() {
  // Auto-fill approver with employee's user_id
  const selectedEmployee = employees.value.find(e => e.name === form.value.employee)
  if (selectedEmployee && selectedEmployee.user_id) {
    form.value.approver = selectedEmployee.user_id
  } else {
    form.value.approver = ""
  }
}

async function handleSubmit() {
  if (!isFormValid.value) {
    error.value = "Please fill in all required fields"
    return
  }

  saving.value = true
  error.value = ""

  try {
    // Get employee name for the record
    const selectedEmployee = employees.value.find(e => e.name === form.value.employee)

    const result = await call("frappe.client.insert", {
      doc: {
        doctype: "Employee Project Assignment",
        project: form.value.project,
        employee: form.value.employee,
        employee_name: selectedEmployee?.employee_name || "",
        role: form.value.role,
        allocation_percentage: parseFloat(form.value.allocation_percentage) || 100,
        status: form.value.status,
        start_date: form.value.start_date,
        end_date: form.value.end_date || null,
        approver: form.value.approver || null,
        project_scope: form.value.project_scope || null,
      },
    })

    const toast = await toastController.create({
      message: "Assignment created successfully!",
      duration: 2000,
      color: "success",
    })
    await toast.present()

    // Navigate back to project detail
    if (projectName) {
      router.replace(`/smart-pro/project/${encodeURIComponent(projectName)}`)
    } else {
      router.replace("/smart-pro/projects")
    }
  } catch (err) {
    console.error("Error creating assignment:", err)
    error.value = err.messages?.[0] || err.message || "Failed to create assignment"
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  loadOptions()
})
</script>
