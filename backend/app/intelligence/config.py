from pathlib import Path
from urllib.parse import urlparse

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.intelligence.models import AIConfigurationStatus, QualityProfile


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
LOCAL_ENV_FILE = REPOSITORY_ROOT / ".env.local"


class AISettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=LOCAL_ENV_FILE,
        env_file_encoding="utf-8",
        env_prefix="",
        extra="ignore",
        populate_by_name=True,
    )

    ai_provider: str = Field(default="placeholder", validation_alias="AI_PROVIDER")
    openai_api_key: SecretStr | None = Field(
        default=None,
        validation_alias="OPENAI_API_KEY",
        exclude=True,
        repr=False,
    )
    openai_base_url: str = Field(
        default="https://api.openai.com/v1",
        validation_alias="OPENAI_BASE_URL",
    )
    ai_model_fast: str = Field(default="", validation_alias="AI_MODEL_FAST")
    ai_model_balanced: str = Field(default="", validation_alias="AI_MODEL_BALANCED")
    ai_model_quality: str = Field(default="", validation_alias="AI_MODEL_QUALITY")
    ai_request_timeout_seconds: float = Field(
        default=45.0,
        ge=1,
        le=300,
        validation_alias="AI_REQUEST_TIMEOUT_SECONDS",
    )
    ai_max_retries: int = Field(
        default=2,
        ge=1,
        le=2,
        validation_alias="AI_MAX_RETRIES",
    )
    ai_fallback_enabled: bool = Field(
        default=True,
        validation_alias="AI_FALLBACK_ENABLED",
    )

    @property
    def provider(self) -> str:
        return self.ai_provider.strip().lower() or "placeholder"

    @property
    def quality_profiles(self) -> list[QualityProfile]:
        if self.provider != "openai":
            return []
        profiles: list[QualityProfile] = []
        if self.ai_model_fast.strip():
            profiles.append("fast")
        if self.ai_model_balanced.strip():
            profiles.append("balanced")
        if self.ai_model_quality.strip():
            profiles.append("quality")
        return profiles

    @property
    def configuration_errors(self) -> list[str]:
        if self.provider == "placeholder":
            return []
        if self.provider != "openai":
            return ["AI_PROVIDER must be 'placeholder' or 'openai'."]

        errors: list[str] = []
        if not self._has_api_key():
            errors.append("OPENAI_API_KEY is required when AI_PROVIDER is 'openai'.")
        if not self._valid_base_url():
            errors.append("OPENAI_BASE_URL must be an absolute HTTP(S) URL.")
        if not self.ai_model_fast.strip():
            errors.append("AI_MODEL_FAST is required when AI_PROVIDER is 'openai'.")
        if not self.ai_model_balanced.strip():
            errors.append("AI_MODEL_BALANCED is required when AI_PROVIDER is 'openai'.")
        if not self.ai_model_quality.strip():
            errors.append("AI_MODEL_QUALITY is required when AI_PROVIDER is 'openai'.")
        return errors

    @property
    def configured(self) -> bool:
        return not self.configuration_errors

    def to_status(self) -> AIConfigurationStatus:
        return AIConfigurationStatus(
            configured=self.configured,
            provider=self.provider,
            quality_profiles=self.quality_profiles,
            fallback_enabled=self.ai_fallback_enabled,
            configuration_errors=self.configuration_errors,
        )

    def _has_api_key(self) -> bool:
        return bool(self.openai_api_key and self.openai_api_key.get_secret_value().strip())

    def _valid_base_url(self) -> bool:
        value = self.openai_base_url.strip()
        parsed = urlparse(value)
        return parsed.scheme in {"http", "https"} and bool(parsed.netloc)
