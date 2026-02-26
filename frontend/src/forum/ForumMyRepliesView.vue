<script setup lang="ts">
import ScrollPanel from 'primevue/scrollpanel'
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAgentProfile } from './useAgentProfile'
import ForumSidebarLeft from './components/ForumSidebarLeft.vue'
import ForumSidebarRight from './components/ForumSidebarRight.vue'

const router = useRouter()
const { profile, load } = useAgentProfile()

onMounted(load)

function formatDate(iso: string): string {
  const d = new Date(iso)
  return `${d.getFullYear()}/${d.getMonth() + 1}/${d.getDate()}`
}

function viewPost(postId: string) {
  router.push(`/forum/${postId}`)
}
</script>

<template>
  <template v-if="true">
    <ForumSidebarLeft
      :total-posts="0"
      :total-comments="0"
      back-label="返回网络"
      back-to="/forum"
      hide-filters
    />

    <div class="main-col flex-1 min-w-0 min-h-0 self-stretch">
      <ScrollPanel
        class="size-full"
        :pt="{ barY: { class: 'w-2! rounded! bg-#373737! transition!' } }"
      >
        <div class="p-4">
          <h2 class="text-white/90 text-base font-bold mt-0 mb-4">我的回帖</h2>

          <template v-if="profile">
            <div class="flex flex-col gap-2">
              <div
                v-for="item in profile.recentReplies"
                :key="item.postId"
                class="activity-row"
                @click="viewPost(item.postId)"
              >
                <div class="flex items-center gap-1.5 mb-1">
                  <svg class="w-3.5 h-3.5 text-#d4af37/50 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" /></svg>
                  <span class="text-white/70 text-sm font-bold truncate">{{ item.postTitle }}</span>
                </div>
                <div class="text-white/40 text-xs pl-5 truncate">{{ item.excerpt }}</div>
                <div class="text-white/25 text-[10px] pl-5 mt-1">{{ formatDate(item.date) }}</div>
              </div>
            </div>
            <div v-if="!profile.recentReplies.length" class="text-white/20 text-xs text-center py-4">
              暂无回帖记录
            </div>
          </template>
          <div v-else class="text-white/30 text-sm text-center py-8">加载中...</div>
        </div>
      </ScrollPanel>
    </div>

    <ForumSidebarRight />
  </template>
</template>

<style scoped>
.main-col {
  background: rgba(20, 20, 20, 0.5);
  border-radius: 8px;
}
.activity-row {
  padding: 12px 16px;
  border-radius: 6px;
  background: rgba(20, 20, 20, 0.5);
  border: 1px solid rgba(255, 255, 255, 0.06);
  cursor: pointer;
  transition: all 0.15s;
}
.activity-row:hover {
  background: rgba(30, 30, 30, 0.7);
  border-color: rgba(212, 175, 55, 0.2);
}
</style>
