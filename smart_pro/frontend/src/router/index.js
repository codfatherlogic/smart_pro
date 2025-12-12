import { createRouter, createWebHistory } from "@ionic/vue-router"

const routes = [
  {
    path: "/",
    redirect: "/smart-pro",
  },
  {
    path: "/smart-pro",
    component: () => import("@/views/TabsLayout.vue"),
    children: [
      {
        path: "",
        redirect: "/smart-pro/home",
      },
      {
        path: "home",
        name: "Home",
        component: () => import("@/views/Home.vue"),
      },
      {
        path: "projects",
        name: "Projects",
        component: () => import("@/views/Projects.vue"),
      },
      {
        path: "tasks",
        name: "Tasks",
        component: () => import("@/views/Tasks.vue"),
      },
      {
        path: "timesheet",
        name: "TimeSheet",
        component: () => import("@/views/TimeSheet.vue"),
      },
      {
        path: "date-requests",
        name: "DateRequests",
        component: () => import("@/views/DateRequests.vue"),
      },
      {
        path: "approvals",
        name: "Approvals",
        component: () => import("@/views/Approvals.vue"),
      },
      {
        path: "connections",
        name: "Connections",
        component: () => import("@/views/Connections.vue"),
      },
      {
        path: "notifications",
        name: "Notifications",
        component: () => import("@/views/Notifications.vue"),
      },
      {
        path: "profile",
        name: "Profile",
        component: () => import("@/views/Profile.vue"),
      },
    ],
  },
  {
    path: "/smart-pro/project/new",
    name: "CreateProject",
    component: () => import("@/views/CreateProject.vue"),
  },
  {
    path: "/smart-pro/assignment/new",
    name: "CreateAssignment",
    component: () => import("@/views/CreateAssignment.vue"),
  },
  {
    path: "/smart-pro/project/:id",
    name: "ProjectDetail",
    component: () => import("@/views/ProjectDetail.vue"),
  },
  {
    path: "/smart-pro/task/:id",
    name: "TaskDetail",
    component: () => import("@/views/TaskDetail.vue"),
  },
  {
    path: "/smart-pro/login",
    name: "Login",
    component: () => import("@/views/Login.vue"),
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// Cache authentication state for performance
let authCache = {
  user: null,
  timestamp: 0,
  TTL: 60000, // 1 minute cache
}

async function getAuthUser(forceRefresh = false) {
  const now = Date.now()

  // Return cached value if valid and not forcing refresh
  if (!forceRefresh && authCache.user !== null && (now - authCache.timestamp) < authCache.TTL) {
    return authCache.user
  }

  try {
    const response = await fetch("/api/method/frappe.auth.get_logged_user")
    const data = await response.json()
    authCache.user = data.message || "Guest"
    authCache.timestamp = now
    return authCache.user
  } catch (error) {
    return "Guest"
  }
}

// Clear auth cache on logout
export function clearAuthCache() {
  authCache.user = null
  authCache.timestamp = 0
}

// Navigation guard for authentication
router.beforeEach(async (to, from, next) => {
  const publicPages = ["/smart-pro/login"]
  const authRequired = !publicPages.includes(to.path)

  // Only force refresh on initial load or coming from login
  const forceRefresh = from.name === undefined || from.path === "/smart-pro/login"
  const user = await getAuthUser(forceRefresh)

  if (authRequired && (!user || user === "Guest")) {
    return next("/smart-pro/login")
  }

  if (to.path === "/smart-pro/login" && user && user !== "Guest") {
    return next("/smart-pro/home")
  }

  next()
})

export default router
