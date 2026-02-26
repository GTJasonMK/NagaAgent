import type { AgentProfile, CreateCommentPayload, CreatePostPayload, ForumPost, ForumPostDetail, PaginatedResponse, SortMode, TimeOrder } from './types'
import { MOCK_AGENT_PROFILE, MOCK_POSTS } from './mock'
import coreApi from '@/api/core'

const USE_MOCK = false

// ─── Mock helpers ───────────────────────────────

function mockDelay<T>(data: T, ms = 200): Promise<T> {
  return new Promise(resolve => setTimeout(() => resolve(data), ms))
}

function applyFilters(
  posts: ForumPostDetail[],
  sort: SortMode,
  timeOrder: TimeOrder,
  yearMonth: string | null,
): ForumPostDetail[] {
  let result = [...posts]

  // Year-month filter
  if (yearMonth) {
    result = result.filter((p) => {
      const d = new Date(p.createdAt)
      const ym = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`
      return ym === yearMonth
    })
  }

  // Sort
  if (sort === 'hot') {
    result.sort((a, b) => (b.likes + b.comments) - (a.likes + a.comments))
  }
  else if (sort === 'latest') {
    result.sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime())
  }

  // Time order (only applies to 'all' and 'latest' — 'hot' is always by popularity)
  if (sort !== 'hot') {
    if (timeOrder === 'asc') {
      result.sort((a, b) => new Date(a.createdAt).getTime() - new Date(b.createdAt).getTime())
    }
    else {
      result.sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime())
    }
  }

  return result
}

// ─── Real API helpers ──────────────────────────

async function apiGet<T>(path: string, params?: Record<string, any>): Promise<T> {
  return coreApi.instance.get(path, { params })
}

async function apiPost<T>(path: string, body?: any): Promise<T> {
  return coreApi.instance.post(path, body)
}

// ─── API functions ──────────────────────────────

export async function fetchPosts(
  sort: SortMode = 'all',
  page = 1,
  pageSize = 20,
  timeOrder: TimeOrder = 'desc',
  yearMonth: string | null = null,
): Promise<PaginatedResponse<ForumPost>> {
  if (!USE_MOCK) {
    try {
      return await apiGet('/forum/api/posts', { sort, page, page_size: pageSize, time_order: timeOrder, year_month: yearMonth })
    } catch {
      // fallback to mock
    }
  }
  const filtered = applyFilters(MOCK_POSTS, sort, timeOrder, yearMonth)
  const start = (page - 1) * pageSize
  const items = filtered.slice(start, start + pageSize)
  return mockDelay({ items, total: filtered.length, page, pageSize })
}

export async function fetchPost(id: string): Promise<ForumPostDetail> {
  if (!USE_MOCK) {
    try {
      return await apiGet(`/forum/api/posts/${id}`)
    } catch {
      // fallback to mock
    }
  }
  const post = MOCK_POSTS.find(p => p.id === id)
  if (!post)
    throw new Error(`Post not found: ${id}`)
  return mockDelay({ ...post })
}

export async function likePost(id: string): Promise<{ likes: number, liked: boolean }> {
  if (!USE_MOCK) {
    try {
      return await apiPost(`/forum/api/posts/${id}/like`)
    } catch {
      // fallback to mock
    }
  }
  const post = MOCK_POSTS.find(p => p.id === id)
  if (!post)
    throw new Error(`Post not found: ${id}`)
  post.liked = !post.liked
  post.likes += post.liked ? 1 : -1
  return mockDelay({ likes: post.likes, liked: post.liked })
}

export async function likeComment(
  commentId: string,
): Promise<{ likes: number, liked: boolean }> {
  if (!USE_MOCK) {
    try {
      return await apiPost(`/forum/api/comments/${commentId}/like`)
    } catch {
      // fallback to mock
    }
  }
  for (const post of MOCK_POSTS) {
    const comment = findComment(post.commentList, commentId)
    if (comment) {
      comment.liked = !comment.liked
      comment.likes += comment.liked ? 1 : -1
      return mockDelay({ likes: comment.likes, liked: comment.liked })
    }
  }
  throw new Error(`Comment not found: ${commentId}`)
}

export async function fetchAgentProfile(): Promise<AgentProfile> {
  if (!USE_MOCK) {
    try {
      return await apiGet('/forum/api/profile')
    } catch {
      // fallback to mock
    }
  }
  return mockDelay({ ...MOCK_AGENT_PROFILE })
}

export async function createPost(payload: CreatePostPayload): Promise<ForumPost> {
  return apiPost('/forum/api/posts', payload)
}

export async function createComment(payload: CreateCommentPayload): Promise<{ success: boolean }> {
  return apiPost(`/forum/api/posts/${payload.postId}/comments`, payload)
}

export async function acceptFriendRequest(requestId: string): Promise<{ success: boolean }> {
  return apiPost(`/forum/api/friend-request/${requestId}/accept`)
}

export async function declineFriendRequest(requestId: string): Promise<{ success: boolean }> {
  return apiPost(`/forum/api/friend-request/${requestId}/decline`)
}

function findComment(
  comments: ForumPostDetail['commentList'],
  id: string,
): ForumPostDetail['commentList'][number] | undefined {
  for (const c of comments) {
    if (c.id === id) return c
    if (c.replies) {
      const found = findComment(c.replies, id)
      if (found) return found
    }
  }
  return undefined
}
