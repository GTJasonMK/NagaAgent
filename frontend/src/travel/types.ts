export interface TravelDiscovery {
  url: string
  title: string
  summary: string
  foundAt: string
  tags: string[]
}

export interface SocialInteraction {
  type: string
  postId?: string
  contentPreview: string
  timestamp: string
}

export interface TravelSession {
  sessionId: string
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled'
  createdAt: string
  startedAt?: string
  completedAt?: string
  timeLimitMinutes: number
  creditLimit: number
  wantFriends: boolean
  friendDescription?: string
  openclawSessionKey?: string
  tokensUsed: number
  creditsUsed: number
  elapsedMinutes: number
  discoveries: TravelDiscovery[]
  socialInteractions: SocialInteraction[]
  summary?: string
  error?: string
}
