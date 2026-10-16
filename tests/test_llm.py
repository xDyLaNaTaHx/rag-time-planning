from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from openai import (
    APIConnectionError,
    APIError,
    APITimeoutError,
    AuthenticationError,
    RateLimitError,
)

from src import llm
from src.errors import (
    LLMAuthError,
    LLMConfigError,
    LLMProviderError,
    LLMRateLimitError,
    LLMResponseError,
    LLMTimeoutError,
)


def _completion(content: str | None):
    return SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content=content))]
    )


def _provider_cases():
    request = MagicMock()
    response_401 = MagicMock(status_code=401)
    response_429 = MagicMock(status_code=429)
    return [
        (
            AuthenticationError(
                message="unauthorized",
                response=response_401,
                body=None,
            ),
            LLMAuthError,
        ),
        (
            RateLimitError(
                message="slow down",
                response=response_429,
                body=None,
            ),
            LLMRateLimitError,
        ),
        (APITimeoutError(request=request), LLMTimeoutError),
        (
            APIConnectionError(request=request, message="offline"),
            LLMProviderError,
        ),
        (
            APIError(message="upstream", request=request, body=None),
            LLMProviderError,
        ),
    ]


def test_load_api_key_missing(monkeypatch):
    monkeypatch.delenv("AI_KEY", raising=False)
    monkeypatch.setattr(llm, "load_dotenv", lambda: None)
    with pytest.raises(LLMConfigError) as exc_info:
        llm.load_api_key()
    assert exc_info.value.code == "ai_config_error"


def test_load_model_name_missing(monkeypatch):
    monkeypatch.delenv("AI_MODEL", raising=False)
    monkeypatch.setattr(llm, "load_dotenv", lambda: None)
    with pytest.raises(LLMConfigError):
        llm.load_model_name(None)


def test_send_prompt_success(monkeypatch):
    monkeypatch.setenv("AI_KEY", "test-key")
    monkeypatch.setenv("AI_MODEL", "test-model")
    monkeypatch.setattr(llm, "load_dotenv", lambda: None)

    client = MagicMock()
    client.chat.completions.create.return_value = _completion('{"ok": true}')
    monkeypatch.setattr(llm, "initialize_client", lambda: client)

    result = llm.send_prompt("test-model", [{"role": "user", "content": "hi"}])
    assert result == '{"ok": true}'
    client.chat.completions.create.assert_called_once()


@pytest.mark.parametrize(("raised", "expected"), _provider_cases())
def test_send_prompt_maps_provider_errors(monkeypatch, raised, expected):
    monkeypatch.setenv("AI_KEY", "test-key")
    monkeypatch.setenv("AI_MODEL", "test-model")
    monkeypatch.setattr(llm, "load_dotenv", lambda: None)

    client = MagicMock()
    client.chat.completions.create.side_effect = raised
    monkeypatch.setattr(llm, "initialize_client", lambda: client)

    with pytest.raises(expected) as exc_info:
        llm.send_prompt("test-model", [{"role": "user", "content": "hi"}])

    assert exc_info.value.code.startswith("ai_")
    assert "traceback" not in exc_info.value.user_message.lower()
    assert "unauthorized" not in exc_info.value.user_message.lower()
    assert "upstream" not in exc_info.value.user_message.lower()


def test_send_prompt_empty_content(monkeypatch):
    monkeypatch.setenv("AI_KEY", "test-key")
    monkeypatch.setenv("AI_MODEL", "test-model")
    monkeypatch.setattr(llm, "load_dotenv", lambda: None)

    client = MagicMock()
    client.chat.completions.create.return_value = _completion("   ")
    monkeypatch.setattr(llm, "initialize_client", lambda: client)

    with pytest.raises(LLMResponseError) as exc_info:
        llm.send_prompt("test-model", [{"role": "user", "content": "hi"}])
    assert exc_info.value.code == "ai_response_error"


def test_send_prompt_none_content(monkeypatch):
    monkeypatch.setenv("AI_KEY", "test-key")
    monkeypatch.setenv("AI_MODEL", "test-model")
    monkeypatch.setattr(llm, "load_dotenv", lambda: None)

    client = MagicMock()
    client.chat.completions.create.return_value = _completion(None)
    monkeypatch.setattr(llm, "initialize_client", lambda: client)

    with pytest.raises(LLMResponseError):
        llm.send_prompt("test-model", [{"role": "user", "content": "hi"}])
