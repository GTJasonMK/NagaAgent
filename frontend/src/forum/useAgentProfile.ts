import { ref } from 'vue'
import type { ForumProfile } from './types'
import { fetchProfile } from './api'

const profile = ref<ForumProfile | null>(null)
let loading: Promise<void> | null = null

export function useForumProfile() {
  async function load() {
    if (profile.value) return
    if (!loading) {
      loading = fetchProfile().then((data) => {
        profile.value = data
      }).catch(() => {
        // 后端暂不可用
      })
    }
    await loading
  }

  async function reload() {
    loading = null
    profile.value = null
    await load()
  }

  return { profile, load, reload }
}

// Backward-compatible alias
export function useAgentProfile() {
  return useForumProfile()
}
