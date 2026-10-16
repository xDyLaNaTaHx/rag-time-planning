"""Domain errors for schedule generation with safe user-facing messages."""


class PlannerError(Exception):
    """Base error with a stable code and user-safe message."""

    code: str = "planner_error"
    status_code: int = 500
    user_message: str = "Something went wrong while generating a schedule."

    def __init__(self, message: str | None = None, *, cause: BaseException | None = None):
        self.user_message = message or self.__class__.user_message
        self.__cause__ = cause
        super().__init__(self.user_message)

    def to_detail(self) -> dict[str, str]:
        return {"code": self.code, "message": self.user_message}


class LLMConfigError(PlannerError):
    code = "ai_config_error"
    status_code = 503
    user_message = (
        "The AI service is not configured correctly. "
        "Check AI_KEY and AI_MODEL, then try again."
    )


class LLMProviderError(PlannerError):
    code = "ai_provider_error"
    status_code = 503
    user_message = (
        "The AI service failed while generating a schedule. Please try again shortly."
    )


class LLMAuthError(LLMProviderError):
    code = "ai_auth_error"
    status_code = 503
    user_message = (
        "The AI service rejected the request credentials. "
        "Check AI_KEY and try again."
    )


class LLMRateLimitError(LLMProviderError):
    code = "ai_rate_limit"
    status_code = 503
    user_message = (
        "The AI service is rate-limited right now. Wait a moment and try again."
    )


class LLMTimeoutError(LLMProviderError):
    code = "ai_timeout"
    status_code = 503
    user_message = (
        "The AI service timed out while generating a schedule. Please try again."
    )


class LLMResponseError(PlannerError):
    code = "ai_response_error"
    status_code = 422
    user_message = (
        "The AI returned a schedule that could not be used. Please try generating again."
    )
