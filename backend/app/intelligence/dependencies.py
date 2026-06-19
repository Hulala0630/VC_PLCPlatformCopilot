from functools import lru_cache

from pydantic import ValidationError

from app.intelligence.config import AISettings
from app.intelligence.models import AIConfigurationStatus


_ENV_FIELD_NAMES = {
    "ai_provider": "AI_PROVIDER",
    "openai_api_key": "OPENAI_API_KEY",
    "openai_base_url": "OPENAI_BASE_URL",
    "ai_model_fast": "AI_MODEL_FAST",
    "ai_model_balanced": "AI_MODEL_BALANCED",
    "ai_model_quality": "AI_MODEL_QUALITY",
    "ai_request_timeout_seconds": "AI_REQUEST_TIMEOUT_SECONDS",
    "ai_max_retries": "AI_MAX_RETRIES",
    "ai_fallback_enabled": "AI_FALLBACK_ENABLED",
}


@lru_cache
def get_ai_settings() -> AISettings:
    return AISettings()


@lru_cache
def get_ai_configuration_status() -> AIConfigurationStatus:
    try:
        return get_ai_settings().to_status()
    except ValidationError as error:
        return AIConfigurationStatus(
            configured=False,
            provider="invalid",
            quality_profiles=[],
            fallback_enabled=True,
            configuration_errors=_safe_validation_errors(error),
        )


def clear_ai_settings_cache() -> None:
    get_ai_settings.cache_clear()
    get_ai_configuration_status.cache_clear()


def _safe_validation_errors(error: ValidationError) -> list[str]:
    messages: list[str] = []
    for item in error.errors(include_url=False, include_context=False, include_input=False):
        location = str(item["loc"][-1]) if item.get("loc") else "AI configuration"
        field_name = _ENV_FIELD_NAMES.get(location.lower(), location.upper())
        message = f"Invalid value for {field_name}."
        if message not in messages:
            messages.append(message)
    return messages or ["AI configuration is invalid."]
