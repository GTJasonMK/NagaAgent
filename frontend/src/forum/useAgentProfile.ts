import { ref } from 'vue'
import type { AgentProfile } from './types'
import { fetchAgentProfile as apiFetch } from './api'

const profile = ref<AgentProfile | null>(null)
let loading: Promise<void> | null = null

export function useAgentProfile() {
  async function load() {
    if (profile.value) return
    if (!loading) {
      loading = apiFetch().then((data) => {
        profile.value = data
      })
    }
    await loading
  }

  function markMessagesRead() {
    if (profile.value) {
      profile.value.recentMessages = profile.value.recentMessages.map(m => ({ ...m, read: true }))
    }
  }

  function setForumEnabled(enabled: boolean) {
    if (profile.value) {
      profile.value.forumEnabled = enabled
    }
  }

  function setDailyBudget(value: number) {
    if (profile.value) {
      profile.value.quota.dailyBudget = Math.max(0, Math.round(value))
    }
  }

  return { profile, load, markMessagesRead, setForumEnabled, setDailyBudget }
}
