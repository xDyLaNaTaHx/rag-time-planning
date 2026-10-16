import type { ScheduleBlock } from '../types'

const DAYS = [
  'Monday',
  'Tuesday',
  'Wednesday',
  'Thursday',
  'Friday',
  'Saturday',
  'Sunday',
] as const

const DAY_START_HOUR = 5
const DAY_END_HOUR = 23
const TOTAL_MINUTES = (DAY_END_HOUR - DAY_START_HOUR) * 60

function parseTimeToMinutes(time: string): number {
  const [h, m] = time.split(':').map(Number)
  return h * 60 + (m || 0)
}

function clamp(value: number, min: number, max: number) {
  return Math.min(max, Math.max(min, value))
}

function blockStyle(block: ScheduleBlock) {
  const start = parseTimeToMinutes(block.start_time)
  const end = parseTimeToMinutes(block.end_time)
  const dayStart = DAY_START_HOUR * 60
  const top = clamp(((start - dayStart) / TOTAL_MINUTES) * 100, 0, 100)
  const height = clamp(((end - start) / TOTAL_MINUTES) * 100, 1.5, 100 - top)
  const hue = 150 + ((block.priority - 1) * 18) % 80

  return {
    top: `${top}%`,
    height: `${height}%`,
    background: `hsla(${hue}, 42%, 36%, 0.92)`,
  }
}

const HOUR_LABELS = Array.from(
  { length: DAY_END_HOUR - DAY_START_HOUR + 1 },
  (_, i) => DAY_START_HOUR + i,
)

interface WeekCalendarProps {
  blocks: ScheduleBlock[]
}

export function WeekCalendar({ blocks }: WeekCalendarProps) {
  const byDay = DAYS.map((day) =>
    blocks.filter((b) => b.day.toLowerCase() === day.toLowerCase()),
  )

  return (
    <div className="calendar">
      <div className="calendar-rail" aria-hidden="true">
        {HOUR_LABELS.map((hour) => (
          <div key={hour} className="hour-label">
            {String(hour).padStart(2, '0')}:00
          </div>
        ))}
      </div>

      <div className="calendar-grid">
        {DAYS.map((day, dayIndex) => (
          <div key={day} className="day-column">
            <div className="day-header">{day.slice(0, 3)}</div>
            <div className="day-body">
              {HOUR_LABELS.slice(0, -1).map((hour) => (
                <div key={hour} className="hour-line" />
              ))}
              {byDay[dayIndex].map((block, i) => (
                <article
                  key={`${day}-${block.start_time}-${i}`}
                  className="schedule-block"
                  style={blockStyle(block)}
                  title={`${block.activity}\n${block.start_time}–${block.end_time}\n${block.linked_goal}`}
                >
                  <strong>{block.activity}</strong>
                  <span>
                    {block.start_time}–{block.end_time}
                  </span>
                </article>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
