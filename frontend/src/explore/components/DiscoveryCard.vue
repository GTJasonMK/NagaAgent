<script setup lang="ts">
import type { TravelDiscovery } from '@/travel/types'

defineProps<{
  discovery: TravelDiscovery
  clickable?: boolean
}>()

function domainOf(url: string): string {
  try {
    return new URL(url).hostname.replace(/^www\./, '')
  } catch {
    return url.slice(0, 20)
  }
}

function timeAgo(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime()
  const m = Math.floor(diff / 60000)
  if (m < 60) return `${m}m`
  const h = Math.floor(m / 60)
  if (h < 24) return `${h}h`
  return `${Math.floor(h / 24)}d`
}
</script>

<template>
  <component
    :is="clickable ? 'a' : 'div'"
    :href="clickable ? discovery.url : undefined"
    :target="clickable ? '_blank' : undefined"
    class="discovery-card"
    :class="{ clickable }"
  >
    <!-- Domain icon -->
    <div class="domain-icon">
      {{ domainOf(discovery.url).charAt(0).toUpperCase() }}
    </div>

    <!-- Body -->
    <div class="card-body">
      <div class="card-title">{{ discovery.title }}</div>
      <div class="card-summary">{{ discovery.summary }}</div>
      <div class="card-meta">
        <div v-if="discovery.tags.length" class="tag-list">
          <span v-for="tag in discovery.tags.slice(0, 3)" :key="tag" class="tag">#{{ tag }}</span>
        </div>
        <div class="meta-right">
          <span class="domain-text">{{ domainOf(discovery.url) }}</span>
          <span v-if="discovery.foundAt" class="time-text">{{ timeAgo(discovery.foundAt) }}</span>
        </div>
      </div>
    </div>

    <!-- External link icon -->
    <svg v-if="clickable" class="link-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
      <polyline points="15 3 21 3 21 9" />
      <line x1="10" y1="14" x2="21" y2="3" />
    </svg>
  </component>
</template>

<style scoped>
.discovery-card {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 12px;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
  text-decoration: none;
  transition: all 0.2s;
}
.discovery-card.clickable {
  cursor: pointer;
}
.discovery-card.clickable:hover {
  border-color: rgba(212, 175, 55, 0.3);
  background: rgba(212, 175, 55, 0.04);
}

.domain-icon {
  width: 36px;
  height: 36px;
  border-radius: 6px;
  background: rgba(212, 175, 55, 0.12);
  color: #d4af37;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 700;
  flex-shrink: 0;
}

.card-body {
  flex: 1;
  min-width: 0;
}

.card-title {
  color: rgba(255, 255, 255, 0.85);
  font-size: 13px;
  font-weight: 600;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-summary {
  color: rgba(255, 255, 255, 0.35);
  font-size: 11px;
  line-height: 1.4;
  margin-top: 3px;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 6px;
  gap: 8px;
}

.tag-list {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
  min-width: 0;
}

.tag {
  color: rgba(212, 175, 55, 0.6);
  font-size: 10px;
  background: rgba(212, 175, 55, 0.08);
  padding: 1px 6px;
  border-radius: 10px;
  white-space: nowrap;
}

.meta-right {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-shrink: 0;
}

.domain-text {
  color: rgba(255, 255, 255, 0.2);
  font-size: 10px;
}

.time-text {
  color: rgba(255, 255, 255, 0.15);
  font-size: 10px;
}

.link-icon {
  width: 14px;
  height: 14px;
  color: rgba(255, 255, 255, 0.15);
  flex-shrink: 0;
  margin-top: 2px;
}
.discovery-card.clickable:hover .link-icon {
  color: rgba(212, 175, 55, 0.5);
}
</style>
