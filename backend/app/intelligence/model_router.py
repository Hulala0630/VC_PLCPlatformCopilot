from typing import Literal

from app.intelligence.config import AISettings
from app.intelligence.models import QualityProfile


IntelligenceCapability = Literal[
    "global_chat",
    "project_chat",
    "project_analysis",
    "benchmark_explanation",
    "report_generation",
    "report_section_rewrite",
    "connection_test",
]


DEFAULT_MODEL_PROFILES: dict[IntelligenceCapability, QualityProfile] = {
    "global_chat": "fast",
    "project_chat": "balanced",
    "project_analysis": "balanced",
    "benchmark_explanation": "balanced",
    "report_generation": "quality",
    "report_section_rewrite": "quality",
    "connection_test": "fast",
}


class ModelRouter:
    def __init__(self, settings: AISettings) -> None:
        self._settings = settings

    def profile_for(
        self,
        capability: IntelligenceCapability,
        override: QualityProfile | None = None,
    ) -> QualityProfile:
        return override or DEFAULT_MODEL_PROFILES[capability]

    def model_for(self, profile: QualityProfile) -> str:
        models = {
            "fast": self._settings.ai_model_fast,
            "balanced": self._settings.ai_model_balanced,
            "quality": self._settings.ai_model_quality,
        }
        model = models[profile].strip()
        if not model:
            raise ValueError(f"Model profile '{profile}' is not configured.")
        return model
