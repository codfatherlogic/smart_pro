<template>
  <ion-page>
    <ion-tabs>
      <ion-router-outlet />
      <ion-tab-bar slot="bottom">
        <!-- Home tab - always visible -->
        <ion-tab-button tab="home" href="/smart-pro/home">
          <ion-icon :icon="homeOutline" />
          <ion-label>Home</ion-label>
        </ion-tab-button>

        <!-- Tasks tab - visible to all -->
        <ion-tab-button tab="tasks" href="/smart-pro/tasks">
          <ion-icon :icon="checkmarkCircleOutline" />
          <ion-label>Tasks</ion-label>
        </ion-tab-button>

        <!-- Date Requests tab - visible to all -->
        <ion-tab-button tab="date-requests" href="/smart-pro/date-requests">
          <ion-icon :icon="calendarOutline" />
          <ion-label>Requests</ion-label>
        </ion-tab-button>

        <!-- Time Sheet tab - visible to all -->
        <ion-tab-button tab="timesheet" href="/smart-pro/timesheet">
          <ion-icon :icon="timeOutline" />
          <ion-label>Time Sheet</ion-label>
        </ion-tab-button>

        <!-- Profile tab - always visible -->
        <ion-tab-button tab="profile" href="/smart-pro/profile">
          <ion-icon :icon="personOutline" />
          <ion-label>Profile</ion-label>
        </ion-tab-button>
      </ion-tab-bar>
    </ion-tabs>
  </ion-page>
</template>

<script setup>
import {
  IonPage,
  IonTabs,
  IonTabBar,
  IonTabButton,
  IonIcon,
  IonLabel,
  IonRouterOutlet,
} from "@ionic/vue"
import {
  homeOutline,
  checkmarkCircleOutline,
  timeOutline,
  personOutline,
  calendarOutline,
} from "ionicons/icons"
</script>

<style scoped>
ion-tab-bar {
  --background: var(--ion-toolbar-background);
  --border: 1px solid var(--ion-color-light-shade);
  padding-bottom: env(safe-area-inset-bottom);
}

ion-tab-button {
  --color: var(--ion-color-medium);
  --color-selected: var(--ion-color-primary);
}
</style>
