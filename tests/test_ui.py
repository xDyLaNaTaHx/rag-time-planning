import json

import pytest
from fastapi.testclient import TestClient

from src.errors import LLMProviderError, LLMResponseError, LLMTimeoutError
from src.schemas import WeeklySchedule
from src.ui import app


@pytest.fixture
def client():
    return TestClient(app)


def test_generate_rejects_empty_inputs(client, monkeypatch):
    monkeypatch.setattr("src.ui.store.goals", [])
    monkeypatch.setattr("src.ui.store.constraints", [])

    response = client.post("/api/schedule/generate", json={"goals": [], "constraints": []})

    assert response.status_code == 400
    body = response.json()["detail"]
    assert body["code"] == "missing_inputs"
    assert "goal" in body["message"].lower()


def test_generate_success(client, monkeypatch, sample_schedule_json):
    schedule = WeeklySchedule.model_validate(sample_schedule_json)
    monkeypatch.setattr("src.ui.generate_schedule_response", lambda **_: schedule)

    response = client.post(
        "/api/schedule/generate",
        json={"goals": ["Squat 250 lbs"], "constraints": ["Work 8am-6pm"]},
    )

    assert response.status_code == 200
    assert response.json()["blocks"][0]["activity"] == "Squat training"


def test_generate_maps_provider_failure(client, monkeypatch):
    def boom(**_kwargs):
        raise LLMProviderError()

    monkeypatch.setattr("src.ui.generate_schedule_response", boom)

    response = client.post(
        "/api/schedule/generate",
        json={"goals": ["Goal"], "constraints": []},
    )

    assert response.status_code == 503
    detail = response.json()["detail"]
    assert detail["code"] == "ai_provider_error"
    assert "AI service failed" in detail["message"]
    # Must not leak exception class noise
    assert "LLMProviderError" not in detail["message"]
    assert "Traceback" not in json.dumps(response.json())


def test_generate_maps_timeout(client, monkeypatch):
    monkeypatch.setattr(
        "src.ui.generate_schedule_response",
        lambda **_: (_ for _ in ()).throw(LLMTimeoutError()),
    )

    response = client.post(
        "/api/schedule/generate",
        json={"goals": ["Goal"], "constraints": []},
    )

    assert response.status_code == 503
    assert response.json()["detail"]["code"] == "ai_timeout"


def test_generate_maps_bad_ai_response(client, monkeypatch):
    def boom(**_kwargs):
        raise LLMResponseError()

    monkeypatch.setattr("src.ui.generate_schedule_response", boom)

    response = client.post(
        "/api/schedule/generate",
        json={"goals": ["Goal"], "constraints": []},
    )

    assert response.status_code == 422
    assert response.json()["detail"]["code"] == "ai_response_error"


def test_generate_maps_unexpected_failure(client, monkeypatch):
    def boom(**_kwargs):
        raise RuntimeError("secret internal details")

    monkeypatch.setattr("src.ui.generate_schedule_response", boom)

    response = client.post(
        "/api/schedule/generate",
        json={"goals": ["Goal"], "constraints": []},
    )

    assert response.status_code == 500
    detail = response.json()["detail"]
    assert detail["code"] == "schedule_generation_failed"
    assert "secret internal details" not in detail["message"]


def test_legacy_home_maps_ai_failure(client, monkeypatch):
    monkeypatch.setattr(
        "src.ui.generate_schedule_response",
        lambda **_: (_ for _ in ()).throw(LLMProviderError()),
    )

    response = client.get("/")

    assert response.status_code == 503
    assert response.json()["detail"]["code"] == "ai_provider_error"
