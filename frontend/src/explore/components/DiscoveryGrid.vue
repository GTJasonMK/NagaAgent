<script setup lang="ts">
import type { TravelDiscovery } from '@/travel/types'
import DiscoveryCard from './DiscoveryCard.vue'

defineProps<{
  discoveries: TravelDiscovery[]
  clickable?: boolean
}>()
</script>

<template>
  <div v-if="discoveries.length" class="discovery-grid">
    <DiscoveryCard
      v-for="(d, i) in discoveries"
      :key="i"
      :discovery="d"
      :clickable="clickable"
    />
  </div>

  <!-- Empty state -->
  <div v-else class="empty-state">
    <svg class="w-8 h-8 text-white/10 mb-2" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
      <circle cx="12" cy="12" r="10" />
      <path d="M2 12h20" />
      <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" />
    </svg>
    <span class="text-white/15 text-xs">暂无发现</span>
  </div>
</template>

<style scoped>
.discovery-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 10px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 32px 16px;
}
</style>
