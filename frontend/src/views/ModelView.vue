<script setup lang="ts">
import { Button, InputNumber, ProgressBar, Textarea, ToggleSwitch } from 'primevue'
import { useToast } from 'primevue/usetoast'
import { computed, onMounted, onUnmounted, ref } from 'vue'
import BoxContainer from '@/components/BoxContainer.vue'
import ConfigItem from '@/components/ConfigItem.vue'
import coreApi from '@/api/core'
import type { TravelSession } from '@/api/core'

const toast = useToast()

// 配置
const timeLimit = ref(300)
const creditLimit = ref(1000)
const wantFriends = ref(true)
const friendDescription = ref('')

// 状态
const loading = ref(false)
const travelSession = ref<TravelSession | null>(null)
const isActive = ref(false)
const historyList = ref<TravelSession[]>([])
let pollTimer: ReturnType<typeof setInterval> | null = null

const isRunning = computed(() => travelSession.value?.status === 'running')
const isCompleted = computed(() =>
  travelSession.value?.status === 'completed'
  || travelSession.value?.status === 'failed'
  || travelSession.value?.status === 'cancelled',
)

const timeProgress = computed(() => {
  if (!travelSession.value) return 0
  return Math.min(100, (travelSession.value.elapsedMinutes / travelSession.value.timeLimitMinutes) * 100)
})

const creditProgress = computed(() => {
  if (!travelSession.value) return 0
  return Math.min(100, (travelSession.value.creditsUsed / travelSession.value.creditLimit) * 100)
})

function formatMinutes(m: number): string {
  const h = Math.floor(m / 60)
  const min = Math.round(m % 60)
  return h > 0 ? `${h}h ${min}m` : `${min}m`
}

function formatDate(iso?: string): string {
  if (!iso) return '-'
  const d = new Date(iso)
  return `${d.getMonth() + 1}/${d.getDate()} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

const statusLabel: Record<string, string> = {
  pending: '准备中',
  running: '旅行中',
  completed: '已完成',
  failed: '失败',
  cancelled: '已取消',
}

async function fetchStatus() {
  try {
    const res = await coreApi.getTravelStatus()
    travelSession.value = res.session
    isActive.value = res.active
  } catch {
    // ignore
  }
}

async function fetchHistory() {
  try {
    const res = await coreApi.getTravelHistory()
    historyList.value = res.sessions
  } catch {
    // ignore
  }
}

function startPolling() {
  stopPolling()
  pollTimer = setInterval(async () => {
    await fetchStatus()
    // 如果旅行完成，停止轮询并刷新历史
    if (travelSession.value && !isActive.value) {
      stopPolling()
      toast.add({ severity: 'success', summary: '旅行完成', detail: `发现了 ${travelSession.value.discoveries?.length ?? 0} 个有趣内容`, life: 5000 })
      fetchHistory()
    }
  }, 30000)
}

function stopPolling() {
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }
}

async function startTravel() {
  loading.value = true
  try {
    await coreApi.startTravel({
      timeLimitMinutes: timeLimit.value,
      creditLimit: creditLimit.value,
      wantFriends: wantFriends.value,
      friendDescription: friendDescription.value || undefined,
    })
    toast.add({ severity: 'success', summary: '出发！', detail: '旅行已开始', life: 3000 })
    await fetchStatus()
    startPolling()
  } catch (e: any) {
    const msg = e?.response?.data?.detail || e?.message || '启动失败'
    toast.add({ severity: 'error', summary: '启动失败', detail: msg, life: 5000 })
  } finally {
    loading.value = false
  }
}

async function stopTravel() {
  try {
    await coreApi.stopTravel()
    toast.add({ severity: 'info', summary: '已停止', detail: '旅行已取消', life: 3000 })
    stopPolling()
    await fetchStatus()
    fetchHistory()
  } catch {
    toast.add({ severity: 'error', summary: '操作失败', detail: '停止旅行失败', life: 3000 })
  }
}

function viewSession(session: TravelSession) {
  travelSession.value = session
  isActive.value = false
}

onMounted(async () => {
  await fetchStatus()
  if (isActive.value) {
    startPolling()
  }
  fetchHistory()
})

onUnmounted(() => {
  stopPolling()
})
</script>

<template>
  <BoxContainer class="text-sm">
    <div class="flex flex-col gap-5 p-2 pb-8">
      <!-- 旅行进行中 -->
      <template v-if="isRunning && travelSession">
        <div class="flex items-center gap-2 text-white/80 text-base font-bold">
          <span class="inline-block w-2 h-2 rounded-full bg-green-400 animate-pulse" />
          旅行进行中
        </div>

        <!-- 时间进度 -->
        <div class="flex flex-col gap-1">
          <div class="flex justify-between text-xs text-white/50">
            <span>已用时间</span>
            <span>{{ formatMinutes(travelSession.elapsedMinutes) }} / {{ formatMinutes(travelSession.timeLimitMinutes) }}</span>
          </div>
          <ProgressBar :value="timeProgress" :show-value="false" class="h-2!" />
        </div>

        <!-- 积分进度 -->
        <div class="flex flex-col gap-1">
          <div class="flex justify-between text-xs text-white/50">
            <span>已用积分</span>
            <span>{{ travelSession.creditsUsed }} / {{ travelSession.creditLimit }}</span>
          </div>
          <ProgressBar :value="creditProgress" :show-value="false" class="h-2!" />
        </div>

        <!-- 实时发现 -->
        <div v-if="travelSession.discoveries.length" class="flex flex-col gap-2">
          <div class="text-white/40 text-xs">
            发现 ({{ travelSession.discoveries.length }})
          </div>
          <div class="flex flex-col gap-1.5 max-h-40 overflow-y-auto">
            <div
              v-for="(d, i) in travelSession.discoveries.slice(-5)"
              :key="i"
              class="flex items-start gap-2 px-2 py-1.5 rounded bg-white/3 text-xs"
            >
              <span class="text-#d4af37 shrink-0">*</span>
              <div class="min-w-0">
                <div class="text-white/70 truncate">{{ d.title }}</div>
                <div class="text-white/30 truncate">{{ d.summary }}</div>
              </div>
            </div>
          </div>
        </div>

        <!-- 停止按钮 -->
        <div class="flex justify-center mt-2">
          <Button
            label="停止旅行"
            severity="danger"
            outlined
            class="px-8!"
            @click="stopTravel"
          />
        </div>
      </template>

      <!-- 旅行结果 -->
      <template v-else-if="isCompleted && travelSession">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-2 text-white/80 text-base font-bold">
            <span
              class="inline-block w-2 h-2 rounded-full"
              :class="travelSession.status === 'completed' ? 'bg-blue-400' : 'bg-red-400'"
            />
            {{ statusLabel[travelSession.status] || travelSession.status }}
          </div>
          <span class="text-white/30 text-xs">{{ formatDate(travelSession.completedAt) }}</span>
        </div>

        <!-- 总结 -->
        <div v-if="travelSession.summary" class="text-white/60 text-xs leading-relaxed bg-white/3 rounded-lg p-3">
          {{ travelSession.summary }}
        </div>

        <!-- 错误信息 -->
        <div v-if="travelSession.error" class="text-red-400/70 text-xs bg-red-500/5 rounded-lg p-3">
          {{ travelSession.error }}
        </div>

        <!-- 发现列表 -->
        <div v-if="travelSession.discoveries.length" class="flex flex-col gap-2">
          <div class="text-white/40 text-xs">
            发现 ({{ travelSession.discoveries.length }})
          </div>
          <div class="flex flex-col gap-1.5 max-h-60 overflow-y-auto">
            <a
              v-for="(d, i) in travelSession.discoveries"
              :key="i"
              :href="d.url"
              target="_blank"
              class="flex items-start gap-2 px-2 py-1.5 rounded bg-white/3 text-xs hover:bg-white/6 transition no-underline"
            >
              <span class="text-#d4af37 shrink-0">*</span>
              <div class="min-w-0">
                <div class="text-white/70 truncate">{{ d.title }}</div>
                <div class="text-white/30 truncate">{{ d.summary }}</div>
                <div v-if="d.tags.length" class="flex gap-1 mt-0.5">
                  <span v-for="tag in d.tags" :key="tag" class="text-#d4af37/40 text-[10px]">#{{ tag }}</span>
                </div>
              </div>
            </a>
          </div>
        </div>

        <!-- 社交互动 -->
        <div v-if="travelSession.socialInteractions.length" class="flex flex-col gap-2">
          <div class="text-white/40 text-xs">
            社交互动 ({{ travelSession.socialInteractions.length }})
          </div>
          <div class="flex flex-col gap-1.5">
            <div
              v-for="(s, i) in travelSession.socialInteractions"
              :key="i"
              class="flex items-center gap-2 px-2 py-1.5 rounded bg-white/3 text-xs"
            >
              <span class="text-white/30 shrink-0">{{ s.type === 'post_created' ? '发帖' : s.type === 'reply_sent' ? '回复' : '好友' }}</span>
              <span class="text-white/50 truncate">{{ s.contentPreview }}</span>
            </div>
          </div>
        </div>

        <div class="border-t border-white/8 my-1" />

        <!-- 返回设置 -->
        <div class="flex justify-center">
          <Button
            label="开始新旅行"
            outlined
            class="px-6!"
            @click="travelSession = null"
          />
        </div>
      </template>

      <!-- 旅行配置 -->
      <template v-else>
        <!-- 时间限制 -->
        <ConfigItem name="时间限制" description="本次旅行的最长时间">
          <InputNumber
            v-model="timeLimit"
            :min="5" :max="720" suffix=" 分钟"
            show-buttons
          />
        </ConfigItem>

        <!-- 积分限制 -->
        <ConfigItem name="积分限制" description="本次旅行最多消耗的积分">
          <InputNumber
            v-model="creditLimit"
            :min="10" :max="10000" suffix=" 积分"
            show-buttons
          />
        </ConfigItem>
        <div class="text-xs text-white/30 -mt-2 pl-1">
          1元 = 100积分，通过 NagaBusiness 计费系统消耗
        </div>

        <div class="border-t border-white/8 my-1" />

        <!-- 社交开关 -->
        <ConfigItem name="想认识朋友吗？" description="允许 Naga 在旅途中与其他 AI 社交互动">
          <ToggleSwitch v-model="wantFriends" />
        </ConfigItem>

        <!-- 交友描述 -->
        <div v-show="wantFriends" class="flex flex-col gap-2">
          <div class="text-white/60 text-xs pl-1">
            想认识什么朋友？
          </div>
          <Textarea
            v-model="friendDescription"
            rows="3"
            class="resize-none"
            placeholder="描述你希望 Naga 认识的朋友类型..."
          />
        </div>

        <!-- 出发按钮 -->
        <div class="flex justify-center mt-2">
          <Button
            label="出发！"
            class="px-8!"
            :loading="loading"
            @click="startTravel"
          />
        </div>

        <div class="border-t border-white/8 my-1" />

        <!-- 历史旅行 -->
        <div class="flex flex-col gap-2">
          <div class="text-white/40 text-xs">
            旅行记录
          </div>
          <div v-if="!historyList.length" class="flex items-center justify-center min-h-20 rounded-lg border border-white/6 bg-white/2 text-white/25 text-sm">
            暂无旅行记录
          </div>
          <div v-else class="flex flex-col gap-1.5 max-h-60 overflow-y-auto">
            <button
              v-for="session in historyList.slice(0, 10)"
              :key="session.sessionId"
              class="flex items-center justify-between px-3 py-2 rounded-lg bg-white/3 hover:bg-white/6 transition border-none cursor-pointer text-left w-full"
              @click="viewSession(session)"
            >
              <div class="flex flex-col gap-0.5 min-w-0">
                <div class="text-white/60 text-xs truncate">
                  {{ formatDate(session.createdAt) }}
                  <span class="text-white/30 ml-2">{{ formatMinutes(session.elapsedMinutes) }}</span>
                </div>
                <div class="text-white/30 text-[10px]">
                  {{ session.discoveries?.length ?? 0 }} 个发现
                </div>
              </div>
              <span
                class="text-[10px] px-1.5 py-0.5 rounded shrink-0"
                :class="{
                  'bg-green-500/10 text-green-400/60': session.status === 'completed',
                  'bg-red-500/10 text-red-400/60': session.status === 'failed',
                  'bg-yellow-500/10 text-yellow-400/60': session.status === 'cancelled',
                  'bg-blue-500/10 text-blue-400/60': session.status === 'running',
                }"
              >
                {{ statusLabel[session.status] || session.status }}
              </span>
            </button>
          </div>
        </div>
      </template>
    </div>
  </BoxContainer>
</template>
