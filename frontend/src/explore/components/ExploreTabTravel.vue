<script setup lang="ts">
import { useTravel } from '@/travel/composables/useTravel'
import TravelConfigForm from '@/travel/components/TravelConfigForm.vue'
import TravelRunningPanel from '@/travel/components/TravelRunningPanel.vue'
import TravelResultPanel from '@/travel/components/TravelResultPanel.vue'
import TravelHistoryList from '@/travel/components/TravelHistoryList.vue'
import DiscoveryGrid from './DiscoveryGrid.vue'

const {
  travelSession, isRunning, isCompleted, historyList, loading,
  timeProgress, creditProgress, startTravel, stopTravel, viewSession,
} = useTravel()
</script>

<template>
  <div class="flex flex-col gap-4 p-1">
    <!-- Running state -->
    <div v-if="isRunning && travelSession" class="card">
      <TravelRunningPanel
        :session="travelSession"
        :time-progress="timeProgress"
        :credit-progress="creditProgress"
        @stop="stopTravel"
      />
    </div>

    <!-- Completed state -->
    <div v-else-if="isCompleted && travelSession" class="card">
      <TravelResultPanel
        :session="travelSession"
        @new-travel="travelSession = null"
      />
    </div>

    <!-- Default: config form -->
    <div v-else class="card">
      <TravelConfigForm :loading="loading" @start="startTravel" />
    </div>

    <!-- Discoveries section (when session has discoveries) -->
    <template v-if="travelSession?.discoveries?.length && !isCompleted">
      <div class="section-label">发现</div>
      <DiscoveryGrid :discoveries="travelSession.discoveries" />
    </template>

    <!-- History -->
    <div class="card">
      <TravelHistoryList :sessions="historyList" @select="viewSession" />
    </div>
  </div>
</template>

<style scoped>
.card {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 8px;
  padding: 16px;
}

.section-label {
  color: rgba(255, 255, 255, 0.3);
  font-size: 11px;
  letter-spacing: 0.1em;
  margin-bottom: -8px;
}

/* Override PrimeVue ProgressBar to gold */
.card :deep(.p-progressbar) {
  background: rgba(255, 255, 255, 0.06);
}
.card :deep(.p-progressbar-value) {
  background: #d4af37;
}

/* Override PrimeVue Button to gold */
.card :deep(.p-button-outlined) {
  border-color: rgba(212, 175, 55, 0.4);
  color: #d4af37;
}
.card :deep(.p-button-outlined:hover) {
  background: rgba(212, 175, 55, 0.08);
  border-color: rgba(212, 175, 55, 0.6);
  color: #d4af37;
}
.card :deep(.p-button-danger.p-button-outlined) {
  border-color: rgba(239, 68, 68, 0.4);
  color: #ef4444;
}
.card :deep(.p-button-danger.p-button-outlined:hover) {
  background: rgba(239, 68, 68, 0.08);
}
</style>
