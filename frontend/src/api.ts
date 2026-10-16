import type { WeeklySchedule } from './types'

export interface ApiErrorBody {
  code?: string
  message?: string
}

export class ApiError extends Error {
  status: number
  code: string

  constructor(message: string, status: number, code = 'unknown_error') {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.code = code
  }

  get isAiFailure(): boolean {
    return this.code.startsWith('ai_') || this.status === 503
  }
}

function formatDetail(detail: unknown, fallback: string): { message: string; code: string } {
  if (typeof detail === 'string') {
    return { message: detail, code: 'unknown_error' }
  }

  if (detail && typeof detail === 'object') {
    const body = detail as ApiErrorBody
    if (typeof body.message === 'string' && body.message.trim()) {
      return {
        message: body.message,
        code: typeof body.code === 'string' ? body.code : 'unknown_error',
      }
    }
  }

  if (Array.isArray(detail)) {
    return { message: JSON.stringify(detail), code: 'validation_error' }
  }

  return { message: fallback, code: 'unknown_error' }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response
  try {
    response = await fetch(path, {
      headers: { 'Content-Type': 'application/json', ...(init?.headers ?? {}) },
      ...init,
    })
  } catch {
    throw new ApiError(
      'Could not reach the planner API. Is the backend running?',
      0,
      'network_error',
    )
  }

  if (!response.ok) {
    let detail: unknown = response.statusText
    try {
      const body = await response.json()
      detail = body.detail ?? body
    } catch {
      /* ignore parse errors */
    }

    const { message, code } = formatDetail(detail, response.statusText || 'Request failed')
    throw new ApiError(message, response.status, code)
  }

  return response.json() as Promise<T>
}

export function fetchGoals() {
  return request<{ goals: string[] }>('/api/goals')
}

export function saveGoals(goals: string[]) {
  return request<{ goals: string[] }>('/api/goals', {
    method: 'PUT',
    body: JSON.stringify({ goals }),
  })
}

export function fetchConstraints() {
  return request<{ constraints: string[] }>('/api/constraints')
}

export function saveConstraints(constraints: string[]) {
  return request<{ constraints: string[] }>('/api/constraints', {
    method: 'PUT',
    body: JSON.stringify({ constraints }),
  })
}

export function generateSchedule(goals: string[], constraints: string[]) {
  return request<WeeklySchedule>('/api/schedule/generate', {
    method: 'POST',
    body: JSON.stringify({ goals, constraints }),
  })
}
