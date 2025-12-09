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

// Navigation guard for authentication
router.beforeEach(async (to, from, next) => {
  const publicPages = ["/smart-pro/login"]
  const authRequired = !publicPages.includes(to.path)

  // Check if user is logged in
  try {
    const response = await fetch("/api/method/frappe.auth.get_logged_user")
    const data = await response.json()

    if (authRequired && (!data.message || data.message === "Guest")) {
      return next("/smart-pro/login")
    }

    if (to.path === "/smart-pro/login" && data.message && data.message !== "Guest") {
      return next("/smart-pro/home")
    }
  } catch (error) {
    if (authRequired) {
      return next("/smart-pro/login")
    }
  }

  next()
})

export default router
