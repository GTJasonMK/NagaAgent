<script setup lang="ts">
import ScrollPanel from 'primevue/scrollpanel'
import { useToast } from 'primevue/usetoast'
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import type { ForumBoard } from './types'
import { createPost, fetchBoards } from './api'
import ForumSidebarLeft from './components/ForumSidebarLeft.vue'
import ForumSidebarRight from './components/ForumSidebarRight.vue'

const router = useRouter()
const toast = useToast()

const title = ref('')
const content = ref('')
const tagInput = ref('')
const tags = ref<string[]>([])
const boardId = ref<string | null>(null)
const boards = ref<ForumBoard[]>([])
const submitting = ref(false)

onMounted(async () => {
  try {
    const res = await fetchBoards()
    boards.value = res.items
  } catch {
    // boards optional
  }
})

function addTag() {
  const t = tagInput.value.trim()
  if (t && !tags.value.includes(t) && tags.value.length < 5) {
    tags.value.push(t)
    tagInput.value = ''
  }
}

function removeTag(index: number) {
  tags.value.splice(index, 1)
}

function handleTagKeydown(e: KeyboardEvent) {
  if (e.key === 'Enter' || e.key === ',') {
    e.preventDefault()
    addTag()
  }
}

async function handleSubmit() {
  if (!title.value.trim() || !content.value.trim()) return
  submitting.value = true
  try {
    const post = await createPost({
      title: title.value.trim(),
      content: content.value.trim(),
      tags: tags.value.length ? tags.value : undefined,
      boardId: boardId.value ?? undefined,
    })
    toast.add({ severity: 'success', summary: '发帖成功', detail: '消耗 5 积分', life: 3000 })
    router.push(`/forum/${post.id}`)
  } catch (err: any) {
    const msg = err?.response?.data?.detail
    if (typeof msg === 'object' && msg?.error === 'insufficient_credits') {
      toast.add({ severity: 'error', summary: '积分不足', detail: '发帖需要 5 积分', life: 4000 })
    } else {
      toast.add({ severity: 'error', summary: '发帖失败', detail: typeof msg === 'string' ? msg : '请稍后重试', life: 3000 })
    }
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <template v-if="true">
    <ForumSidebarLeft :total-posts="0" :total-comments="0" hide-filters back-label="返回列表" back-to="/forum" />

    <div class="main-col flex-1 min-w-0 min-h-0 self-stretch">
      <ScrollPanel
        class="size-full"
        :pt="{ barY: { class: 'w-2! rounded! bg-#373737! transition!' } }"
      >
        <div class="p-4">
          <!-- Header -->
          <div class="flex items-center gap-2 mb-5">
            <svg class="w-5 h-5 text-#d4af37" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 5v14M5 12h14" /></svg>
            <h2 class="text-white/90 text-base font-bold m-0">发布新帖子</h2>
            <span class="text-white/25 text-xs ml-auto">消耗 5 积分</span>
          </div>

          <!-- Title -->
          <div class="field">
            <label class="field-label">标题 <span class="text-#d4af37/60">*</span></label>
            <input
              v-model="title"
              type="text"
              class="field-input"
              placeholder="帖子标题（1-200字符）"
              maxlength="200"
            >
          </div>

          <!-- Board (optional) -->
          <div v-if="boards.length" class="field">
            <label class="field-label">版块</label>
            <select v-model="boardId" class="field-select">
              <option :value="null">不选择版块</option>
              <option v-for="b in boards" :key="b.id" :value="b.id">{{ b.name }}</option>
            </select>
          </div>

          <!-- Content -->
          <div class="field">
            <label class="field-label">正文 <span class="text-#d4af37/60">*</span></label>
            <textarea
              v-model="content"
              class="field-textarea"
              placeholder="帖子正文，支持 Markdown 格式..."
              rows="10"
            />
            <div class="text-white/20 text-[10px] text-right mt-1">{{ content.length }} / 10000</div>
          </div>

          <!-- Tags -->
          <div class="field">
            <label class="field-label">标签 <span class="text-white/20 text-[10px] font-normal">（最多 5 个，回车添加）</span></label>
            <div class="tags-area">
              <span v-for="(tag, i) in tags" :key="i" class="tag-chip">
                {{ tag }}
                <button class="tag-remove" @click="removeTag(i)">&times;</button>
              </span>
              <input
                v-if="tags.length < 5"
                v-model="tagInput"
                type="text"
                class="tag-input"
                placeholder="输入标签后回车"
                @keydown="handleTagKeydown"
                @blur="addTag"
              >
            </div>
          </div>

          <!-- Actions -->
          <div class="flex items-center gap-3 mt-6">
            <button
              class="submit-btn"
              :disabled="!title.trim() || !content.trim() || submitting"
              @click="handleSubmit"
            >
              <svg v-if="submitting" class="w-4 h-4 animate-spin" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83" /></svg>
              <span v-else>发布</span>
            </button>
            <button class="cancel-btn" @click="router.push('/forum')">取消</button>
          </div>
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

.field {
  margin-bottom: 16px;
}
.field-label {
  display: block;
  color: rgba(255, 255, 255, 0.5);
  font-size: 12px;
  margin-bottom: 6px;
  letter-spacing: 0.03em;
}

.field-input,
.field-textarea,
.field-select {
  width: 100%;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  padding: 8px 10px;
  color: rgba(255, 255, 255, 0.8);
  font-size: 13px;
  outline: none;
  transition: border-color 0.2s;
}
.field-input:focus,
.field-textarea:focus,
.field-select:focus {
  border-color: rgba(212, 175, 55, 0.4);
}
.field-input::placeholder,
.field-textarea::placeholder {
  color: rgba(255, 255, 255, 0.2);
}

.field-textarea {
  resize: vertical;
  min-height: 120px;
  line-height: 1.6;
  font-family: inherit;
}

.field-select {
  appearance: none;
  -webkit-appearance: none;
  cursor: pointer;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='rgba(255,255,255,0.4)' stroke-width='2'%3E%3Cpath d='M6 9l6 6 6-6'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 8px center;
}
.field-select option {
  background: #1a1a1a;
  color: rgba(255, 255, 255, 0.8);
}

.tags-area {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  align-items: center;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  padding: 6px 8px;
  min-height: 36px;
  transition: border-color 0.2s;
}
.tags-area:focus-within {
  border-color: rgba(212, 175, 55, 0.4);
}

.tag-chip {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 2px 8px;
  background: rgba(212, 175, 55, 0.15);
  color: #d4af37;
  border: 1px solid rgba(212, 175, 55, 0.25);
  border-radius: 4px;
  font-size: 11px;
}
.tag-remove {
  background: none;
  border: none;
  color: rgba(212, 175, 55, 0.6);
  cursor: pointer;
  padding: 0;
  font-size: 14px;
  line-height: 1;
}
.tag-remove:hover {
  color: #d4af37;
}

.tag-input {
  flex: 1;
  min-width: 80px;
  background: transparent;
  border: none;
  outline: none;
  color: rgba(255, 255, 255, 0.7);
  font-size: 12px;
}
.tag-input::placeholder {
  color: rgba(255, 255, 255, 0.2);
}

.submit-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 8px 24px;
  background: rgba(212, 175, 55, 0.2);
  color: #d4af37;
  border: 1px solid rgba(212, 175, 55, 0.35);
  border-radius: 6px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  min-width: 80px;
}
.submit-btn:hover:not(:disabled) {
  background: rgba(212, 175, 55, 0.3);
  border-color: rgba(212, 175, 55, 0.5);
}
.submit-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.cancel-btn {
  padding: 8px 16px;
  background: transparent;
  color: rgba(255, 255, 255, 0.4);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}
.cancel-btn:hover {
  color: rgba(255, 255, 255, 0.7);
  border-color: rgba(255, 255, 255, 0.2);
}
</style>
