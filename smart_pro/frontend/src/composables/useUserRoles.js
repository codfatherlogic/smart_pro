import { ref, computed } from "vue"
import { call } from "frappe-ui"

// Shared state across all component instances
const roles = ref([])
const loading = ref(false)
const error = ref(null)
const fetched = ref(false)

/**
 * Composable for managing user roles and role-based UI
 */
export function useUserRoles() {
  async function fetchRoles() {
    // Don't fetch again if already fetched
    if (fetched.value && roles.value.length > 0) {
      return
    }

    loading.value = true
    error.value = null
    try {
      const result = await call("smart_pro.smart_pro.api.projects.get_user_roles")
      roles.value = result?.roles || []
      fetched.value = true
      console.log("User roles fetched:", roles.value)
    } catch (err) {
      error.value = err
      console.error("Failed to fetch user roles:", err)
    } finally {
      loading.value = false
    }
  }

  const isTeamLead = computed(() => {
    const result = roles.value.includes("Projects Manager") ||
           roles.value.includes("Project Manager") ||
           roles.value.includes("HR Manager") ||
           roles.value.includes("HR-Manager") ||
           roles.value.includes("System Manager")
    return result
  })

  const isEmployee = computed(() => {
    return roles.value.includes("Employee")
  })

  const hasRole = (roleName) => {
    return roles.value.includes(roleName)
  }

  // Clear roles (useful for logout)
  function clearRoles() {
    roles.value = []
    fetched.value = false
  }

  return {
    roles,
    loading,
    error,
    fetchRoles,
    isTeamLead,
    isEmployee,
    hasRole,
    clearRoles,
  }
}