from dataclasses import dataclass
from functools import lru_cache
from time import sleep
from typing import Any, Callable

from pydantic import ValidationError

from app.intelligence.config import AISettings
from app.intelligence.dependencies import get_ai_settings
from app.intelligence.openai_provider import OpenAIProvider
from app.intelligence.provider import DeterministicPlaceholderProvider, IntelligenceProvider


@dataclass(frozen=True)
class ProviderSelection:
    primary: IntelligenceProvider
    placeholder: DeterministicPlaceholderProvider
    fallback_enabled: bool
    openai_active: bool
    configuration_valid: bool


def build_provider_selection(
    settings: AISettings,
    *,
    client: Any | None = None,
    sleep_fn: Callable[[float], None] = sleep,
) -> ProviderSelection:
    placeholder = DeterministicPlaceholderProvider()
    if settings.provider == "openai" and settings.configured:
        return ProviderSelection(
            primary=OpenAIProvider(settings, client=client, sleep_fn=sleep_fn),
            placeholder=placeholder,
            fallback_enabled=settings.ai_fallback_enabled,
            openai_active=True,
            configuration_valid=True,
        )
    return ProviderSelection(
        primary=placeholder,
        placeholder=placeholder,
        fallback_enabled=settings.ai_fallback_enabled,
        openai_active=False,
        configuration_valid=settings.configured,
    )


@lru_cache
def get_provider_selection() -> ProviderSelection:
    try:
        settings = get_ai_settings()
    except ValidationError:
        return ProviderSelection(
            primary=DeterministicPlaceholderProvider(),
            placeholder=DeterministicPlaceholderProvider(),
            fallback_enabled=True,
            openai_active=False,
            configuration_valid=False,
        )
    return build_provider_selection(settings)


def clear_provider_selection_cache() -> None:
    get_provider_selection.cache_clear()
