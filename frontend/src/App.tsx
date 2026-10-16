import { useEffect, useState } from 'react'
import {
  fetchConstraints,
  fetchGoals,
  generateSchedule,
  saveConstraints,
  saveGoals,
} from './api'
import { ItemList } from './components/ItemList'
import { WeekCalendar } from './components/WeekCalendar'
import type { WeeklySchedule } from './types'
import './App.css'

export default function App() {
  const [goals, setGoals] = useState<string[]>([])
  const [constraints, setConstraints] = useState<string[]>([])
  const [schedule, setSchedule] = useState<WeeklySchedule | null>(null)
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState(false)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [status, setStatus] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false

    async function load() {
      try {
        const [goalsRes, constraintsRes] = await Promise.all([
          fetchGoals(),
          fetchConstraints(),
        ])
        if (cancelled) return
        setGoals(goalsRes.goals)
        setConstraints(constraintsRes.constraints)
      } catch (err) {
        if (!cancelled) {
          setError(
            err instanceof Error
              ? err.message
              : 'Could not load goals and constraints. Is the API running?',
          )
        }
      } finally {
        if (!cancelled) setLoading(false)
      }
    }

    void load()
    return () => {
      cancelled = true
    }
  }, [])

  async function handleSave() {
    setSaving(true)
    setError(null)
    setStatus(null)
    try {
      const [goalsRes, constraintsRes] = await Promise.all([
        saveGoals(goals),
        saveConstraints(constraints),
      ])
      setGoals(goalsRes.goals)
      setConstraints(constraintsRes.constraints)
      setStatus('Goals and constraints saved.')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Save failed.')
    } finally {
      setSaving(false)
    }
  }

  async function handleGenerate() {
    setGenerating(true)
    setError(null)
    setStatus(null)
    try {
      await Promise.all([saveGoals(goals), saveConstraints(constraints)])
      const result = await generateSchedule(goals, constraints)
      setSchedule(result)
      setStatus('Schedule generated for this week.')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Generation failed.')
    } finally {
      setGenerating(false)
    }
  }

  return (
    <div className="app-shell">
      <div className="atmosphere" aria-hidden="true" />

      <header className="top-bar">
        <div>
          <p className="eyebrow">RAG Time Planning</p>
          <h1>Week Planner</h1>
        </div>
        <div className="actions">
          <button
            type="button"
            className="secondary-btn"
            onClick={handleSave}
            disabled={loading || saving || generating}
          >
            {saving ? 'Saving…' : 'Save'}
          </button>
          <button
            type="button"
            className="primary-btn"
            onClick={handleGenerate}
            disabled={loading || generating || (goals.length === 0 && constraints.length === 0)}
          >
            {generating ? 'Generating…' : 'Recommend schedule'}
          </button>
        </div>
      </header>

      {(error || status) && (
        <div className={`banner ${error ? 'banner-error' : 'banner-ok'}`} role="status">
          {error ?? status}
        </div>
      )}

      <main className="layout">
        <aside className="sidebar">
          {loading ? (
            <p className="muted">Loading…</p>
          ) : (
            <>
              <ItemList
                title="Goals"
                description="What you want to make progress on this week."
                items={goals}
                onChange={setGoals}
                placeholder="e.g. Squat 250 lbs"
              />
              <ItemList
                title="Constraints"
                description="Fixed busy times the planner must respect."
                items={constraints}
                onChange={setConstraints}
                placeholder="e.g. Work 8am–6pm Mon–Thu"
              />
            </>
          )}
        </aside>

        <section className="schedule-panel">
          <header className="panel-header">
            <h2>Recommended week</h2>
            <p>
              {schedule
                ? 'Blocks are placed around your constraints and linked to goals.'
                : 'Save your goals and constraints, then ask for a weekly recommendation.'}
            </p>
          </header>

          {schedule ? (
            <>
              <WeekCalendar blocks={schedule.blocks} />
              <aside className="rationale">
                <h3>Why this plan</h3>
                <p>{schedule.rationale}</p>
              </aside>
            </>
          ) : (
            <div className="empty-schedule">
              <p>
                No schedule yet. Add goals and constraints on the left, then hit
                Recommend schedule.
              </p>
            </div>
          )}
        </section>
      </main>
    </div>
  )
}
