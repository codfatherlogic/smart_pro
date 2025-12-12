import { ref, computed } from "vue"
import { call } from "frappe-ui"

// Shared state across all component instances (singleton pattern)
const permissions = ref({
  has_full_access: false,
  is_project_manager: false,
  managed_projects: [],
})
const loading = ref(false)
const error = ref(null)
const fetched = ref(false)

/**
 * Composable for managing user permissions
 * - has_full_access: Can view all data (read-only mode)
 * - is_project_manager: Can approve timesheets for their projects
 * - managed_projects: List of project IDs managed by the user
 */
export function usePermissions() {
  async function fetchPermissions() {
    // Don't fetch again if already fetched
    if (fetched.value) {
      return permissions.value
    }

    loading.value = true
    error.value = null
    try {
      const result = await call("smart_pro.smart_pro.api.projects.get_user_permissions")
      if (result?.success) {
        permissions.value = {
          has_full_access: result.has_full_access || false,
          is_project_manager: result.is_project_manager || false,
          managed_projects: result.managed_projects || [],
        }
      }
      fetched.value = true
      console.log("User permissions fetched:", permissions.value)
      return permissions.value
    } catch (err) {
      error.value = err
      console.error("Failed to fetch user permissions:", err)
      return permissions.value
    } finally {
      loading.value = false
    }
  }

  // Computed properties for easy access
  const hasFullAccess = computed(() => permissions.value.has_full_access)
  const isProjectManager = computed(() => permissions.value.is_project_manager)
  const managedProjects = computed(() => permissions.value.managed_projects)

  // Check if user can approve timesheet for a specific project
  function canApproveTimesheetForProject(projectName) {
    if (permissions.value.has_full_access) return true
    if (!permissions.value.is_project_manager) return false
    return permissions.value.managed_projects.includes(projectName)
  }

  // Check if user is in read-only mode (has full access but not the owner)
  function isReadOnlyForItem(ownerOrAssignee) {
    // If user has full access, they can see everything but in read-only mode
    // unless they are the owner/assignee
    return permissions.value.has_full_access
  }

  // Clear permissions (useful for logout)
  function clearPermissions() {
    permissions.value = {
      has_full_access: false,
      is_project_manager: false,
      managed_projects: [],
    }
    fetched.value = false
  }

  return {
    permissions,
    loading,
    error,
    fetchPermissions,
    hasFullAccess,
    isProjectManager,
    managedProjects,
    canApproveTimesheetForProject,
    isReadOnlyForItem,
    clearPermissions,
  }
}
