<script setup lang="ts">
import ScrollPanel from 'primevue/scrollpanel'
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useForumProfile } from '@/forum/useAgentProfile'
import coreApi from '@/api/core'
import ExploreTabTravel from './components/ExploreTabTravel.vue'
import ExploreTabNetwork from './components/ExploreTabNetwork.vue'

const route = useRoute()
const router = useRouter()

const tab = ref<'travel' | 'network'>(
  route.query.tab === 'network' ? 'network' : 'travel',
)

// Status indicators
const travelRunning = ref(false)
const { profile, load: loadProfile } = useForumProfile()
const forumEnabled = computed(() => profile.value?.forumEnabled ?? false)

onMounted(async () => {
  // One-shot check for travel status badge
  try {
    const res = await coreApi.getTravelStatus()
    travelRunning.value = res.active
  } catch {
    // ignore
  }
  loadProfile()
})

function setTab(t: 'travel' | 'network') {
  tab.value = t
  router.replace({ query: t === 'travel' ? {} : { tab: 'network' } })
}
</script>

<template>
  <div class="explore-root">
    <!-- Back button -->
    <button class="back-btn" @click="router.push('/')">
      <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M19 12H5" /><polyline points="12 19 5 12 12 5" />
      </svg>
    </button>

    <!-- Main panel -->
    <div class="explore-panel">
      <!-- Header -->
      <div class="explore-header">
        <h1 class="panel-title">探索</h1>

        <div class="tab-bar">
          <button
            class="tab-item"
            :class="{ active: tab === 'travel' }"
            @click="setTab('travel')"
          >
            <span
              v-if="travelRunning"
              class="pulse-dot green"
            />
            旅行探索
          </button>
          <button
            class="tab-item"
            :class="{ active: tab === 'network' }"
            @click="setTab('network')"
          >
            <span
              v-if="forumEnabled"
              class="pulse-dot gold"
            />
            网络探索
          </button>
        </div>
      </div>

      <!-- Content -->
      <ScrollPanel
        class="flex-1 min-h-0"
        :pt="{ barY: { class: 'w-2! rounded! bg-#373737! transition!' } }"
      >
        <div class="p-4 pt-0">
          <ExploreTabTravel v-if="tab === 'travel'" />
          <ExploreTabNetwork v-else />
        </div>
      </ScrollPanel>
    </div>
  </div>
</template>

<style scoped>
.explore-root {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  width: 100%;
  position: relative;
}

.back-btn {
  position: absolute;
  top: 16px;
  left: 16px;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(20, 20, 20, 0.6);
  backdrop-filter: blur(12px);
  color: rgba(255, 255, 255, 0.5);
  cursor: pointer;
  transition: all 0.2s;
  z-index: 10;
}
.back-btn:hover {
  border-color: rgba(212, 175, 55, 0.3);
  color: #d4af37;
  background: rgba(20, 20, 20, 0.8);
}

.explore-panel {
  width: 60%;
  max-width: 680px;
  min-width: 400px;
  height: 85%;
  max-height: 720px;
  display: flex;
  flex-direction: column;
  background: rgba(20, 20, 20, 0.5);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  backdrop-filter: blur(20px);
  overflow: hidden;
}

.explore-header {
  padding: 20px 24px 0;
  flex-shrink: 0;
}

.panel-title {
  color: rgba(255, 255, 255, 0.9);
  font-size: 18px;
  font-weight: 700;
  margin: 0 0 16px;
  letter-spacing: 0.02em;
}

.tab-bar {
  display: flex;
  gap: 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.tab-item {
  position: relative;
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px 12px;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.35);
  background: transparent;
  border: none;
  cursor: pointer;
  transition: color 0.2s;
}
.tab-item:hover {
  color: rgba(255, 255, 255, 0.6);
}
.tab-item.active {
  color: #d4af37;
}
.tab-item.active::after {
  content: '';
  position: absolute;
  left: 16px;
  right: 16px;
  bottom: -1px;
  height: 2px;
  background: #d4af37;
  border-radius: 1px;
}

/* Pulse dots */
.pulse-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  animation: pulse 2s ease-in-out infinite;
}
.pulse-dot.green {
  background: #4ade80;
  box-shadow: 0 0 4px rgba(74, 222, 128, 0.5);
}
.pulse-dot.gold {
  background: #d4af37;
  box-shadow: 0 0 4px rgba(212, 175, 55, 0.5);
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}
</style>
