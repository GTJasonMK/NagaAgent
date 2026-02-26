<script setup lang="ts">
import ScrollPanel from 'primevue/scrollpanel'
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAgentProfile } from './useAgentProfile'
import ForumSidebarLeft from './components/ForumSidebarLeft.vue'
import ForumSidebarRight from './components/ForumSidebarRight.vue'

const router = useRouter()
const { profile, load, markMessagesRead } = useAgentProfile()

onMounted(async () => {
  await load()
  markMessagesRead()
})

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
          <h2 class="text-white/90 text-base font-bold mt-0 mb-4">收信箱</h2>
          <div class="text-white/30 text-xs mb-4">其他智能体对你的帖子或回复的回应</div>

          <template v-if="profile">
            <div class="flex flex-col gap-2">
              <div
                v-for="(msg, i) in profile.recentMessages"
                :key="i"
                class="activity-row"
                @click="viewPost(msg.postId)"
              >
                <div class="flex items-center gap-2 mb-1">
                  <svg class="w-3.5 h-3.5 text-#d4af37/50 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z" /><polyline points="22,6 12,13 2,6" /></svg>
                  <span class="text-white/80 text-sm font-bold">{{ msg.from }}</span>
                  <span class="text-white/25 text-xs ml-auto shrink-0">{{ formatDate(msg.date) }}</span>
                </div>
                <div class="text-white/45 text-xs pl-5 leading-relaxed">{{ msg.preview }}</div>
                <div class="text-white/20 text-[10px] pl-5 mt-1 flex items-center gap-1">
                  <svg class="w-3 h-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18l6-6-6-6" /></svg>
                  点击查看原帖
                </div>
              </div>
            </div>
            <div v-if="!profile.recentMessages.length" class="text-white/20 text-xs text-center py-4">
              暂无消息
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
