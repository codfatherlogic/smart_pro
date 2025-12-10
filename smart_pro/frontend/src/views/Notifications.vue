<template>
  <ion-page>
    <ion-header>
      <ion-toolbar>
        <ion-buttons slot="start">
          <ion-back-button default-href="/smart-pro/home" text="" />
        </ion-buttons>
        <ion-title>Notifications</ion-title>
        <ion-buttons slot="end">
          <ion-button
            v-if="notifications.length > 0"
            @click="markAllAsRead"
            :disabled="markingAll"
          >
            <ion-icon :icon="checkmarkDoneOutline" />
          </ion-button>
        </ion-buttons>
      </ion-toolbar>
    </ion-header>

    <ion-content :fullscreen="true">
      <ion-refresher slot="fixed" @ion-refresh="handleRefresh">
        <ion-refresher-content />
      </ion-refresher>

      <!-- Loading State -->
      <div
        v-if="loading"
        class="p-4"
      >
        <div
          v-for="i in 5"
          :key="i"
          class="app-card mb-4 p-4"
        >
          <div class="skeleton h-4 w-3/4 mb-2" />
          <div class="skeleton h-3 w-1/2" />
        </div>
      </div>

      <!-- Empty State -->
      <div
        v-else-if="notifications.length === 0"
        class="empty-state h-full"
      >
        <ion-icon
          :icon="notificationsOffOutline"
          class="empty-state-icon"
        />
        <div class="empty-state-title">
          No notifications
        </div>
        <div class="empty-state-description">
          You're all caught up!
        </div>
      </div>

      <!-- Notifications List -->
      <div
        v-else
        class="p-4"
      >
        <div
          v-for="notification in notifications"
          :key="notification.name"
          class="notification-card"
          :class="{ unread: !notification.read }"
          @click="handleNotificationClick(notification)"
        >
          <div class="notification-icon" :class="getNotificationTypeClass(notification.type)">
            <ion-icon :icon="getNotificationIcon(notification.type)" />
          </div>
          <div class="notification-content">
            <div class="notification-subject">
              {{ notification.subject }}
            </div>
            <div class="notification-message" v-if="notification.email_content">
              {{ stripHtml(notification.email_content).substring(0, 100) }}...
            </div>
            <div class="notification-time">
              {{ formatTime(notification.creation) }}
            </div>
          </div>
          <div class="notification-actions">
            <span
              v-if="!notification.read"
              class="unread-dot"
            />
          </div>
        </div>
      </div>
    </ion-content>
  </ion-page>
</template>

<script setup>
import { ref, onMounted, inject } from "vue"
import { onIonViewWillEnter } from "@ionic/vue"
import { useRouter } from "vue-router"
import {
  IonPage,
  IonHeader,
  IonToolbar,
  IonTitle,
  IonContent,
  IonRefresher,
  IonRefresherContent,
  IonIcon,
  IonButton,
  IonButtons,
  IonBackButton,
  toastController,
} from "@ionic/vue"
import {
  notificationsOffOutline,
  checkmarkDoneOutline,
  alertCircleOutline,
  informationCircleOutline,
  checkmarkCircleOutline,
  warningOutline,
  calendarOutline,
  documentTextOutline,
  personOutline,
} from "ionicons/icons"
import { call } from "frappe-ui"

const router = useRouter()
const $dayjs = inject("$dayjs")

const loading = ref(true)
const notifications = ref([])
const markingAll = ref(false)

async function loadData() {
  loading.value = true
  try {
    // Fetch from Smart Pro Notification (custom notifications)
    const smartProNotifications = await call("frappe.client.get_list", {
      doctype: "Smart Pro Notification",
      fields: ["name", "title", "body", "data", "status", "created_at"],
      filters: {},
      order_by: "created_at desc",
      limit_page_length: 50
    })

    // Transform Smart Pro Notifications to common format
    const transformedNotifications = (smartProNotifications || []).map(n => {
      let parsedData = {}
      try {
        parsedData = n.data ? JSON.parse(n.data) : {}
      } catch (e) {
        console.error("Error parsing notification data:", e)
      }
      return {
        name: n.name,
        subject: n.title,
        email_content: n.body,
        type: parsedData.type || "Info",
        document_type: parsedData.doctype,
        document_name: parsedData.name,
        read: n.status === "read" ? 1 : 0,
        creation: n.created_at,
        source: "smart_pro"
      }
    })

    // Also fetch from Frappe Notification Log
    let frappeNotifications = []
    try {
      const frappeResult = await call("frappe.client.get_list", {
        doctype: "Notification Log",
        fields: ["name", "subject", "email_content", "type", "document_type", "document_name", "read", "creation"],
        filters: {},
        order_by: "creation desc",
        limit_page_length: 50
      })
      frappeNotifications = (frappeResult || []).map(n => ({
        ...n,
        source: "frappe"
      }))
    } catch (e) {
      console.log("Frappe Notification Log not accessible:", e)
    }

    // Merge and sort by creation date
    const allNotifications = [...transformedNotifications, ...frappeNotifications]
    allNotifications.sort((a, b) => new Date(b.creation) - new Date(a.creation))

    notifications.value = allNotifications.slice(0, 50)
  } catch (err) {
    console.error("Error loading notifications:", err)
  } finally {
    loading.value = false
  }
}

function handleRefresh(event) {
  loadData().finally(() => {
    event.target.complete()
  })
}

async function handleNotificationClick(notification) {
  // Mark as read using custom API
  if (!notification.read) {
    try {
      await call("smart_pro.smart_pro.api.projects.mark_notification_as_read", {
        notification_name: notification.name,
        source: notification.source || "smart_pro"
      })
      notification.read = 1
    } catch (err) {
      console.error("Error marking notification as read:", err)
    }
  }

  // Navigate to related document if possible
  if (notification.document_type && notification.document_name) {
    const docTypeRouteMap = {
      "Smart Project": `/smart-pro/project/${encodeURIComponent(notification.document_name)}`,
      "Smart Task": `/smart-pro/task/${encodeURIComponent(notification.document_name)}`,
      "Employee Date Request": `/smart-pro/date-requests`,
    }

    const route = docTypeRouteMap[notification.document_type]
    if (route) {
      router.push(route)
    }
  }
}

async function markAllAsRead() {
  markingAll.value = true
  try {
    // Use custom API to mark all as read
    await call("smart_pro.smart_pro.api.projects.mark_all_notifications_as_read")

    // Update local state
    notifications.value.forEach(n => {
      n.read = 1
    })

    const toast = await toastController.create({
      message: "All notifications marked as read",
      duration: 2000,
      color: "success",
    })
    await toast.present()
  } catch (err) {
    console.error("Error marking all as read:", err)
    const toast = await toastController.create({
      message: "Failed to mark notifications as read",
      duration: 2000,
      color: "danger",
    })
    await toast.present()
  } finally {
    markingAll.value = false
  }
}

function formatTime(dateStr) {
  if (!dateStr) return ""
  return $dayjs(dateStr).fromNow()
}

function stripHtml(html) {
  if (!html) return ""
  return html.replace(/<[^>]*>/g, "").replace(/&nbsp;/g, " ").trim()
}

function getNotificationIcon(type) {
  const iconMap = {
    Alert: alertCircleOutline,
    Warning: warningOutline,
    Success: checkmarkCircleOutline,
    Info: informationCircleOutline,
    Assignment: personOutline,
    Mention: personOutline,
    Share: documentTextOutline,
    Event: calendarOutline,
  }
  return iconMap[type] || informationCircleOutline
}

function getNotificationTypeClass(type) {
  const classMap = {
    Alert: "alert",
    Warning: "warning",
    Success: "success",
    Info: "info",
    Assignment: "assignment",
    Mention: "mention",
    Share: "share",
    Event: "event",
  }
  return classMap[type] || "info"
}

onMounted(() => {
  loadData()
})

onIonViewWillEnter(() => {
  loadData()
})
</script>

<style scoped>
.notification-card {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 1rem;
  background: var(--ion-card-background, white);
  border-radius: 0.75rem;
  margin-bottom: 0.75rem;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
  transition: all 0.2s ease;
  cursor: pointer;
}

.notification-card:hover {
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.notification-card.unread {
  background: linear-gradient(135deg, var(--ion-color-primary-tint, #eff6ff) 0%, var(--ion-card-background, #fff) 100%);
  border-left: 3px solid var(--ion-color-primary);
}

/* Dark mode support */
body.dark .notification-card {
  background: var(--ion-card-background, #1e1e1e);
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.3);
}

body.dark .notification-card.unread {
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.2) 0%, var(--ion-card-background, #1e1e1e) 100%);
}

body.dark .notification-subject {
  color: #f1f5f9;
}

body.dark .notification-message {
  color: #94a3b8;
}

body.dark .notification-time {
  color: #64748b;
}

.notification-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  flex-shrink: 0;
}

.notification-icon.alert { background: #fecaca; color: #dc2626; }
.notification-icon.warning { background: #fed7aa; color: #ea580c; }
.notification-icon.success { background: #d1fae5; color: #059669; }
.notification-icon.info { background: #dbeafe; color: #2563eb; }
.notification-icon.assignment { background: #e9d5ff; color: #9333ea; }
.notification-icon.mention { background: #fce7f3; color: #db2777; }
.notification-icon.share { background: #ccfbf1; color: #0d9488; }
.notification-icon.event { background: #fef3c7; color: #d97706; }

.notification-content {
  flex: 1;
  min-width: 0;
}

.notification-subject {
  font-weight: 600;
  color: var(--ion-text-color, #1e293b);
  font-size: 0.9375rem;
  margin-bottom: 0.25rem;
}

.notification-message {
  font-size: 0.8125rem;
  color: var(--ion-color-medium, #64748b);
  margin-bottom: 0.5rem;
  line-height: 1.4;
}

.notification-time {
  font-size: 0.75rem;
  color: var(--ion-color-medium-shade, #94a3b8);
}

.notification-actions {
  display: flex;
  align-items: center;
}

.unread-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: var(--ion-color-primary);
}

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

.app-card {
  background-color: var(--ion-card-background, white);
  border-radius: 0.75rem;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
}

body.dark .app-card {
  background-color: var(--ion-card-background, #1e1e1e);
}

.skeleton {
  background-color: var(--ion-color-light, #e5e7eb);
  border-radius: 0.25rem;
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

body.dark .skeleton {
  background-color: #374151;
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
