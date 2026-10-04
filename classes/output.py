class ScheduleBlock(BaseModel):
    ''' Represents a single block in the weekly schedule '''
    day: str
    start_time: str
    end_time: str
    activity: str
    linked_goal: str
    priority: int

class WeeklySchedule(BaseModel):
    ''' Represents the entire weekly schedule '''
    blocks: list[ScheduleBlock]
    rationale: str