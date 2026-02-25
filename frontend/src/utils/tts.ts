import { ref } from 'vue'
import { ACCESS_TOKEN } from '@/api'
import API from '@/api/core'

const audio = ref<HTMLAudioElement | null>(null)
export const isPlaying = ref(false)
let maxDurationTimer: number | null = null
let abortController: AbortController | null = null

const MAX_PLAYBACK_DURATION = 30000 // 30秒最大播放时长

/** 移除 markdown 代码块（```...```）和行内代码（`...`），只保留自然语言文本 */
function stripCodeBlocks(text: string): string {
  return text
    .replace(/```[\s\S]*?```/g, '') // 移除代码块
    .replace(/`[^`]+`/g, '')        // 移除行内代码
    .replace(/\n{3,}/g, '\n\n')     // 压缩多余空行
    .trim()
}

export function speak(text: string): Promise<void> {
  stop()

  // 移除代码块，只朗读自然语言
  const cleanText = stripCodeBlocks(text)
  if (!cleanText) return Promise.resolve()

  // 走 API Server 代理（和 chatStream 同一个 endpoint），后端自动判断走 NagaBusiness 还是本地 edge-tts
  const url = `${API.endpoint}/tts/speech`

  const isLoggedIn = !!ACCESS_TOKEN.value
  const headers: Record<string, string> = { 'Content-Type': 'application/json' }
  if (isLoggedIn) {
    headers.Authorization = `Bearer ${ACCESS_TOKEN.value}`
  }

  // 创建 AbortController 以便中途取消 fetch
  abortController = new AbortController()
  const { signal } = abortController

  return fetch(url, {
    method: 'POST',
    headers,
    signal,
    body: JSON.stringify({
      model: isLoggedIn ? 'default' : 'tts-1',
      input: cleanText,
      voice: isLoggedIn ? 'Cherry' : 'zh-CN-XiaoyiNeural',
      speed: 1.0,
      response_format: 'mp3',
    }),
  }).then(async (res) => {
    if (!res.ok)
      throw new Error(`TTS responded ${res.status}`)
    const blob = await res.blob()
    if (blob.size === 0)
      throw new Error('TTS returned empty audio')

    // 如果已被 stop() 中止，不再播放
    if (signal.aborted) return

    const audioBlob = blob.type.startsWith('audio/') ? blob : new Blob([blob], { type: 'audio/mpeg' })
    const objectUrl = URL.createObjectURL(audioBlob)
    const el = new Audio(objectUrl)
    audio.value = el

    // 严格时机：音频真正开始播放时才设 isPlaying=true（驱动 Live2D 张嘴）
    el.onplay = () => {
      isPlaying.value = true
    }

    el.onended = () => {
      cleanup(objectUrl)
    }

    el.onerror = () => {
      cleanup(objectUrl)
    }

    // 设置30秒最大播放时长定时器
    maxDurationTimer = window.setTimeout(() => {
      if (audio.value) {
        stop()
      }
    }, MAX_PLAYBACK_DURATION)

    el.play()
  }).catch((err) => {
    // AbortError 是正常取消，不需要报错
    if (err instanceof DOMException && err.name === 'AbortError') return
    cleanup()
    console.error('[TTS] speak failed:', err)
    throw err
  })
}

function cleanup(objectUrl?: string) {
  if (maxDurationTimer) {
    clearTimeout(maxDurationTimer)
    maxDurationTimer = null
  }
  isPlaying.value = false
  if (objectUrl) {
    URL.revokeObjectURL(objectUrl)
  }
  audio.value = null
}

export function stop() {
  // 取消正在进行的 fetch 请求
  if (abortController) {
    abortController.abort()
    abortController = null
  }

  // 清除定时器
  if (maxDurationTimer) {
    clearTimeout(maxDurationTimer)
    maxDurationTimer = null
  }

  if (audio.value) {
    audio.value.pause()
    audio.value = null
  }
  // 立即闭嘴
  isPlaying.value = false
}
