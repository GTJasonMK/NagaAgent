import { ref, watch } from 'vue'

export interface BackgroundItem {
  id: string
  name: string
  description: string
  price: number // 积分
  filename: string // filename in premium-assets/backgrounds/
}

// ── 背景目录（16:9 图片，放置于 premium-assets/backgrounds/） ──
export const BACKGROUND_CATALOG: BackgroundItem[] = [
  {
    id: 'starry-night',
    name: '星夜回廊',
    description: '深邃星空下的无尽廊道，璀璨繁星照亮归途',
    price: 200,
    filename: 'starry-night.png',
  },
  {
    id: 'golden-sunset',
    name: '落日熔金',
    description: '金色夕阳洒满天际，温暖光芒笼罩大地',
    price: 150,
    filename: 'golden-sunset.png',
  },
  {
    id: 'cyber-city',
    name: '霓虹都市',
    description: '赛博朋克风格的未来都市，霓虹灯映照雨夜',
    price: 300,
    filename: 'cyber-city.png',
  },
  {
    id: 'sakura-garden',
    name: '樱之庭院',
    description: '落英缤纷的日式庭院，花瓣随风飘散',
    price: 250,
    filename: 'sakura-garden.png',
  },
  {
    id: 'aurora-sky',
    name: '极光穹顶',
    description: '北极光在夜空中舞动，绿紫交织的神秘光幕',
    price: 350,
    filename: 'aurora-sky.png',
  },
  {
    id: 'ocean-depths',
    name: '深海秘境',
    description: '幽蓝深海中的奇幻世界，光线穿透海面',
    price: 200,
    filename: 'ocean-depths.png',
  },
]

const STORAGE_KEY_OWNED = 'naga-bg-owned'
const STORAGE_KEY_ACTIVE = 'naga-bg-active'

function loadOwned(): string[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY_OWNED)
    return raw ? JSON.parse(raw) : []
  }
  catch {
    return []
  }
}

function loadActive(): string | null {
  return localStorage.getItem(STORAGE_KEY_ACTIVE) || null
}

const ownedBackgrounds = ref<string[]>(loadOwned())
const activeBackground = ref<string | null>(loadActive())

watch(ownedBackgrounds, (ids) => {
  localStorage.setItem(STORAGE_KEY_OWNED, JSON.stringify(ids))
}, { deep: true })

watch(activeBackground, (id) => {
  if (id) {
    localStorage.setItem(STORAGE_KEY_ACTIVE, id)
  }
  else {
    localStorage.removeItem(STORAGE_KEY_ACTIVE)
  }
})

export function useBackground() {
  function isOwned(id: string): boolean {
    return ownedBackgrounds.value.includes(id)
  }

  function isActive(id: string): boolean {
    return activeBackground.value === id
  }

  function purchase(id: string): boolean {
    if (ownedBackgrounds.value.includes(id)) return false
    ownedBackgrounds.value = [...ownedBackgrounds.value, id]
    return true
  }

  function apply(id: string) {
    activeBackground.value = id
  }

  function resetToDefault() {
    activeBackground.value = null
  }

  function getBackgroundUrl(id: string): string | null {
    const item = BACKGROUND_CATALOG.find(b => b.id === id)
    if (!item) return null
    return `naga-bg://${item.filename}`
  }

  function getActiveBackgroundUrl(): string | null {
    if (!activeBackground.value) return null
    return getBackgroundUrl(activeBackground.value)
  }

  return {
    ownedBackgrounds,
    activeBackground,
    isOwned,
    isActive,
    purchase,
    apply,
    resetToDefault,
    getBackgroundUrl,
    getActiveBackgroundUrl,
    BACKGROUND_CATALOG,
  }
}
