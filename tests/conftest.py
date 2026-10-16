import pytest


@pytest.fixture
def sample_schedule_json() -> dict:
    return {
        "blocks": [
            {
                "day": "Friday",
                "start_time": "09:00",
                "end_time": "10:00",
                "activity": "Squat training",
                "linked_goal": "Squat 250 lbs",
                "priority": 1,
            }
        ],
        "rationale": "Train outside work hours.",
    }
