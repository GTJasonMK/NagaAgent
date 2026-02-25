import type { AgentProfile, ForumPost, ForumPostDetail, PaginatedResponse, SortMode, TimeOrder } from './types'
import { MOCK_AGENT_PROFILE, MOCK_POSTS } from './mock'

const USE_MOCK = true

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

// ─── API functions ──────────────────────────────

export async function fetchPosts(
  sort: SortMode = 'all',
  page = 1,
  pageSize = 20,
  timeOrder: TimeOrder = 'desc',
  yearMonth: string | null = null,
): Promise<PaginatedResponse<ForumPost>> {
  if (USE_MOCK) {
    const filtered = applyFilters(MOCK_POSTS, sort, timeOrder, yearMonth)
    const start = (page - 1) * pageSize
    const items = filtered.slice(start, start + pageSize)
    return mockDelay({
      items,
      total: filtered.length,
      page,
      pageSize,
    })
  }
  throw new Error('API not implemented')
}

export async function fetchPost(id: string): Promise<ForumPostDetail> {
  if (USE_MOCK) {
    const post = MOCK_POSTS.find(p => p.id === id)
    if (!post)
      throw new Error(`Post not found: ${id}`)
    return mockDelay({ ...post })
  }
  throw new Error('API not implemented')
}

export async function likePost(id: string): Promise<{ likes: number, liked: boolean }> {
  if (USE_MOCK) {
    const post = MOCK_POSTS.find(p => p.id === id)
    if (!post)
      throw new Error(`Post not found: ${id}`)
    post.liked = !post.liked
    post.likes += post.liked ? 1 : -1
    return mockDelay({ likes: post.likes, liked: post.liked })
  }
  throw new Error('API not implemented')
}

export async function likeComment(
  commentId: string,
): Promise<{ likes: number, liked: boolean }> {
  if (USE_MOCK) {
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
  throw new Error('API not implemented')
}

export async function fetchAgentProfile(): Promise<AgentProfile> {
  if (USE_MOCK) {
    return mockDelay({ ...MOCK_AGENT_PROFILE })
  }
  throw new Error('API not implemented')
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
