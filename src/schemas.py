from pydantic import BaseModel, Field


class ScheduleBlock(BaseModel):
    """A single block in the weekly schedule."""

    day: str = Field(description="Day of week, e.g. Monday")
    start_time: str = Field(description="Start time in HH:MM 24h format")
    end_time: str = Field(description="End time in HH:MM 24h format")
    activity: str
    linked_goal: str
    priority: int = Field(ge=1, le=5, description="1 = highest priority")


class WeeklySchedule(BaseModel):
    """Full weekly schedule proposal."""

    blocks: list[ScheduleBlock]
    rationale: str


class GoalsPayload(BaseModel):
    goals: list[str]


class ConstraintsPayload(BaseModel):
    constraints: list[str]


class ScheduleRequest(BaseModel):
    goals: list[str] | None = None
    constraints: list[str] | None = None
    query: str = "How should I schedule my week?"
