import json

import pytest

from src.errors import LLMProviderError, LLMResponseError
from src.main import _extract_json, generate_schedule_response
from src.schemas import WeeklySchedule


def test_extract_json_plain():
    assert _extract_json('{"a": 1}') == {"a": 1}


def test_extract_json_fenced():
    raw = 'Here you go:\n```json\n{"a": 2}\n```\n'
    assert _extract_json(raw) == {"a": 2}


def test_generate_schedule_success(monkeypatch, sample_schedule_json):
    monkeypatch.setattr(
        "src.main.send_prompt",
        lambda **_kwargs: json.dumps(sample_schedule_json),
    )

    result = generate_schedule_response(
        goals=["Squat 250 lbs"],
        constraints=["Work 8am-6pm Monday-Thursday"],
    )

    assert isinstance(result, WeeklySchedule)
    assert result.blocks[0].activity == "Squat training"
    assert "work" in result.rationale.lower()


def test_generate_schedule_invalid_json(monkeypatch):
    monkeypatch.setattr("src.main.send_prompt", lambda **_kwargs: "not-json")

    with pytest.raises(LLMResponseError) as exc_info:
        generate_schedule_response(goals=["Goal"], constraints=[])

    assert exc_info.value.code == "ai_response_error"
    assert "parsed" in exc_info.value.user_message.lower()


def test_generate_schedule_invalid_schema(monkeypatch):
    monkeypatch.setattr(
        "src.main.send_prompt",
        lambda **_kwargs: json.dumps(
            {
                "blocks": [
                    {
                        "day": "Monday",
                        "start_time": "09:00",
                        "end_time": "10:00",
                        "activity": "Lift",
                        "linked_goal": "Strength",
                        "priority": 99,
                    }
                ],
                "rationale": "bad priority",
            }
        ),
    )

    with pytest.raises(LLMResponseError) as exc_info:
        generate_schedule_response(goals=["Strength"], constraints=[])

    assert "unexpected format" in exc_info.value.user_message.lower()


def test_generate_schedule_propagates_provider_error(monkeypatch):
    def boom(**_kwargs):
        raise LLMProviderError()

    monkeypatch.setattr("src.main.send_prompt", boom)

    with pytest.raises(LLMProviderError):
        generate_schedule_response(goals=["Goal"], constraints=[])
