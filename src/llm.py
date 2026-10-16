import logging
import os

from dotenv import load_dotenv
from openai import (
    APIConnectionError,
    APIError,
    APITimeoutError,
    AuthenticationError,
    OpenAI,
    RateLimitError,
)

from src.errors import (
    LLMAuthError,
    LLMConfigError,
    LLMProviderError,
    LLMRateLimitError,
    LLMResponseError,
    LLMTimeoutError,
)

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT_SECONDS = 60.0


def load_api_key() -> str:
    """Load the API key from environment variables."""
    load_dotenv()
    key = os.getenv("AI_KEY")
    if not key or not key.strip():
        raise LLMConfigError()
    return key.strip()


def load_model_name(model: str | None = None) -> str:
    """Resolve the model name, failing fast if unset."""
    load_dotenv()
    resolved = (model or os.getenv("AI_MODEL") or "").strip()
    if not resolved:
        raise LLMConfigError(
            "AI_MODEL is not set. Configure the model name and try again."
        )
    return resolved


def initialize_client() -> OpenAI:
    """Initialize the OpenAI-compatible client with the API key."""
    key = load_api_key()
    return OpenAI(
        api_key=key,
        base_url="https://api.groq.com/openai/v1",
        timeout=DEFAULT_TIMEOUT_SECONDS,
    )


def send_prompt(model, messages, json_mode: bool = False) -> str:
    """Send a prompt to the LLM and return the response text.

    Raises domain errors with safe user messages; never returns raw SDK errors.
    """
    resolved_model = load_model_name(model)
    client = initialize_client()
    kwargs: dict = {
        "model": resolved_model,
        "messages": messages,
    }
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}

    try:
        response = client.chat.completions.create(**kwargs)
    except AuthenticationError as exc:
        logger.exception("AI authentication failed")
        raise LLMAuthError(cause=exc) from exc
    except RateLimitError as exc:
        logger.exception("AI rate limit hit")
        raise LLMRateLimitError(cause=exc) from exc
    except APITimeoutError as exc:
        logger.exception("AI request timed out")
        raise LLMTimeoutError(cause=exc) from exc
    except APIConnectionError as exc:
        logger.exception("AI connection failed")
        raise LLMProviderError(
            "Could not reach the AI service. Check your network connection and try again.",
            cause=exc,
        ) from exc
    except APIError as exc:
        logger.exception("AI provider API error")
        raise LLMProviderError(cause=exc) from exc
    except Exception as exc:
        logger.exception("Unexpected AI client failure")
        raise LLMProviderError(cause=exc) from exc

    try:
        content = response.choices[0].message.content
    except (AttributeError, IndexError, TypeError) as exc:
        logger.exception("AI response missing choices/content")
        raise LLMResponseError(
            "The AI returned an empty response. Please try again.",
            cause=exc,
        ) from exc

    if content is None or not str(content).strip():
        raise LLMResponseError("The AI returned an empty response. Please try again.")

    return str(content)
