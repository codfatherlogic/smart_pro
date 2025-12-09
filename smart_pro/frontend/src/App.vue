<template>
  <ion-app>
    <ion-router-outlet />
    <InstallPrompt />
  </ion-app>
</template>

<script setup>
import { IonApp, IonRouterOutlet } from "@ionic/vue"
import InstallPrompt from "@/components/InstallPrompt.vue"
</script>
