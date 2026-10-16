export interface ScheduleBlock {
  day: string
  start_time: string
  end_time: string
  activity: string
  linked_goal: string
  priority: number
}

export interface WeeklySchedule {
  blocks: ScheduleBlock[]
  rationale: string
}
