from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from src.main import generate_schedule_response
from src.schemas import (
    ConstraintsPayload,
    GoalsPayload,
    ScheduleRequest,
    WeeklySchedule,
)
from src.store import store

app = FastAPI(title="RAG Time Planner", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/goals", response_model=GoalsPayload)
def get_goals():
    return GoalsPayload(goals=store.goals)


@app.put("/api/goals", response_model=GoalsPayload)
def put_goals(payload: GoalsPayload):
    return GoalsPayload(goals=store.set_goals(payload.goals))


@app.get("/api/constraints", response_model=ConstraintsPayload)
def get_constraints():
    return ConstraintsPayload(constraints=store.constraints)


@app.put("/api/constraints", response_model=ConstraintsPayload)
def put_constraints(payload: ConstraintsPayload):
    return ConstraintsPayload(constraints=store.set_constraints(payload.constraints))


@app.post("/api/schedule/generate", response_model=WeeklySchedule)
def generate_schedule(request: ScheduleRequest | None = None):
    payload = request or ScheduleRequest()
    goals = payload.goals if payload.goals is not None else store.goals
    constraints = (
        payload.constraints if payload.constraints is not None else store.constraints
    )

    if not goals and not constraints:
        raise HTTPException(
            status_code=400,
            detail="Add at least one goal or constraint before generating a schedule.",
        )

    try:
        return generate_schedule_response(
            goals=goals,
            constraints=constraints,
            query=payload.query,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Failed to generate schedule: {exc}",
        ) from exc


@app.get("/")
def home():
    """Legacy endpoint: returns a free-text schedule using stored goals/constraints."""
    schedule = generate_schedule_response(
        goals=store.goals,
        constraints=store.constraints,
    )
    return {
        "response": schedule.rationale,
        "schedule": schedule.model_dump(),
    }
