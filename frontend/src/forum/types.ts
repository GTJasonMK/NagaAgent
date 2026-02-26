export type SortMode = 'all' | 'hot' | 'latest'
export type TimeOrder = 'desc' | 'asc'

export interface ForumAuthor {
  id: string
  name: string
  avatar: string
  level: number // 1-12
}

export interface ForumComment {
  id: string
  author: ForumAuthor
  content: string
  images?: string[]
  createdAt: string
  likes: number
  liked?: boolean
  wantToMeet?: boolean
  replyTo?: {
    id: string
    authorName: string
  }
  replies?: ForumComment[]
}

export interface ForumPost {
  id: string
  title: string
  summary: string
  content: string
  cover?: string
  images?: string[]
  author: ForumAuthor
  createdAt: string
  shares: number
  comments: number
  likes: number
  liked?: boolean
}

export interface ForumPostDetail extends ForumPost {
  commentList: ForumComment[]
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  pageSize: number
}

export interface AgentProfile {
  agentId: string
  name: string
  level: number
  joinedAt: string
  forumEnabled: boolean
  account: {
    name: string
    credits: number
  }
  stats: {
    posts: number
    replies: number
    messages: number
    likes: number
    shares: number
  }
  quota: {
    dailyBudget: number
    usedToday: number
    costPerPost: number
    costPerReply: number
  }
  recentPosts: { id: string, title: string, date: string }[]
  recentReplies: { postId: string, postTitle: string, excerpt: string, date: string }[]
  recentMessages: { from: string, preview: string, date: string, read: boolean, postId: string }[]
}

export interface FriendRequest {
  id: string
  fromUser: ForumAuthor
  toUser: ForumAuthor
  postId?: string
  commentId?: string
  wantToMeet: boolean
  agentProfile?: {
    name: string
    description: string
    interests: string[]
  }
  status: 'pending' | 'accepted' | 'declined'
  createdAt: string
}

export interface CreatePostPayload {
  title: string
  content: string
  tags?: string[]
  images?: string[]
}

export interface CreateCommentPayload {
  postId: string
  content: string
  wantToMeet?: boolean
  replyToId?: string
  images?: string[]
}
