import type { WeeklySchedule } from './types'

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(path, {
    headers: { 'Content-Type': 'application/json', ...(init?.headers ?? {}) },
    ...init,
  })

  if (!response.ok) {
    let detail = response.statusText
    try {
      const body = await response.json()
      detail = body.detail ?? JSON.stringify(body)
    } catch {
      /* ignore parse errors */
    }
    throw new Error(typeof detail === 'string' ? detail : JSON.stringify(detail))
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
