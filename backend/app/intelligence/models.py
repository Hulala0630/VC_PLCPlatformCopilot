from typing import Literal

from pydantic import AliasChoices, BaseModel, Field, field_validator

from app.models import Language, LocalizedText


IntelligenceMode = Literal["deterministic_placeholder", "openai", "deterministic_fallback"]
IntelligenceProviderName = Literal["openai", "placeholder"]
IntelligenceExecutionStatus = Literal["ai_success", "basic_analysis", "ai_fallback"]
FallbackReason = Literal[
    "timeout",
    "rate_limit",
    "authentication",
    "unsupported_model",
    "invalid_response",
    "provider_unavailable",
]
SafeProviderError = Literal[
    "timeout",
    "authentication",
    "rate_limit",
    "provider_server_error",
    "invalid_response",
    "invalid_request",
    "unsupported_model",
    "unsupported_response_format",
    "connection_error",
    "configuration_error",
]
IntelligenceScope = Literal[
    "global",
    "project",
    "project_analysis",
    "benchmark_explanation",
    "benchmark_analysis",
    "project_summary",
    "report_generation",
    "report_section",
]
IntelligenceSourceType = Literal[
    "platform_profile",
    "project_intake",
    "platform_preference",
    "benchmark_result",
    "project_readiness",
    "report_section",
    "attachment_metadata",
]
ReportAudience = Literal["executive", "technical", "management", "sales"]
QualityProfile = Literal["fast", "balanced", "quality"]
ProjectAnalysisFocus = Literal["project", "attachments"]


def _non_empty(value: str) -> str:
    value = value.strip()
    if not value:
        raise ValueError("Value must not be empty.")
    return value


class GlobalChatRequest(BaseModel):
    question: str
    language: Language
    platform_ids: list[str] = Field(default_factory=list)
    use_ai: bool = True
    quality_profile: QualityProfile | None = Field(
        default=None,
        validation_alias=AliasChoices("quality_profile", "quality"),
    )

    @field_validator("question")
    @classmethod
    def validate_question(cls, value: str) -> str:
        return _non_empty(value)


class ProjectChatRequest(BaseModel):
    question: str
    language: Language
    use_ai: bool = True
    quality_profile: QualityProfile | None = Field(
        default=None,
        validation_alias=AliasChoices("quality_profile", "quality"),
    )

    @field_validator("question")
    @classmethod
    def validate_question(cls, value: str) -> str:
        return _non_empty(value)


class ProjectAnalysisRequest(BaseModel):
    language: Language
    focus: ProjectAnalysisFocus = "project"
    use_ai: bool = True
    quality_profile: QualityProfile | None = Field(
        default=None,
        validation_alias=AliasChoices("quality_profile", "quality"),
    )


class BenchmarkExplanationRequest(BaseModel):
    language: Language
    use_ai: bool = True
    quality_profile: QualityProfile | None = Field(
        default=None,
        validation_alias=AliasChoices("quality_profile", "quality"),
    )


class BenchmarkAnalysisRequest(BaseModel):
    language: Language
    use_ai: bool = True
    quality_profile: QualityProfile | None = Field(
        default=None,
        validation_alias=AliasChoices("quality_profile", "quality"),
    )


class ProjectSummaryRequest(BaseModel):
    language: Language
    use_ai: bool = True
    quality_profile: QualityProfile | None = Field(
        default=None,
        validation_alias=AliasChoices("quality_profile", "quality"),
    )


class ReportGenerationRequest(BaseModel):
    language: Language
    audience: ReportAudience
    use_ai: bool = True
    quality_profile: QualityProfile | None = Field(
        default=None,
        validation_alias=AliasChoices("quality_profile", "quality"),
    )


class ReportSectionRewriteRequest(BaseModel):
    instruction: str
    language: Language
    audience: ReportAudience
    use_ai: bool = True
    quality_profile: QualityProfile | None = Field(
        default=None,
        validation_alias=AliasChoices("quality_profile", "quality"),
    )

    @field_validator("instruction")
    @classmethod
    def validate_instruction(cls, value: str) -> str:
        return _non_empty(value)


class IntelligenceSource(BaseModel):
    id: str
    type: IntelligenceSourceType
    label: LocalizedText
    detail: LocalizedText


class IntelligenceResponse(BaseModel):
    id: str
    execution_status: IntelligenceExecutionStatus = "basic_analysis"
    mode: IntelligenceMode = "deterministic_placeholder"
    provider: IntelligenceProviderName = "placeholder"
    model_profile: QualityProfile | None = None
    fallback_reason: FallbackReason | None = None
    retryable: bool = False
    request_id: str
    scope: IntelligenceScope
    answer: LocalizedText
    sources: list[IntelligenceSource]
    assumptions: list[LocalizedText]
    uncertainty: list[LocalizedText]
    missing_inputs: list[LocalizedText]
    follow_up_questions: list[LocalizedText]
    next_actions: list[LocalizedText] = Field(default_factory=list)
    ai_used: bool = False
    document_parsing_used: Literal[False] = False
    generated_at: str


class GeneratedReportSection(BaseModel):
    section_id: str
    title: LocalizedText
    draft_body: LocalizedText


class ReportGenerationResponse(BaseModel):
    id: str
    execution_status: IntelligenceExecutionStatus = "basic_analysis"
    mode: IntelligenceMode = "deterministic_placeholder"
    provider: IntelligenceProviderName = "placeholder"
    model_profile: QualityProfile | None = None
    fallback_reason: FallbackReason | None = None
    retryable: bool = False
    request_id: str
    scope: Literal["report_generation"] = "report_generation"
    audience: ReportAudience
    sections: list[GeneratedReportSection]
    sources: list[IntelligenceSource]
    assumptions: list[LocalizedText]
    uncertainty: list[LocalizedText]
    missing_inputs: list[LocalizedText]
    ai_used: bool = False
    document_parsing_used: Literal[False] = False
    generated_at: str


class ReportSectionRewriteResponse(BaseModel):
    id: str
    execution_status: IntelligenceExecutionStatus = "basic_analysis"
    section_id: str
    suggested_body: LocalizedText
    assumptions: list[LocalizedText]
    uncertainty: list[LocalizedText]
    sources: list[IntelligenceSource]
    mode: IntelligenceMode = "deterministic_placeholder"
    provider: IntelligenceProviderName = "placeholder"
    model_profile: QualityProfile | None = None
    ai_used: bool = False
    fallback_reason: FallbackReason | None = None
    retryable: bool = False
    request_id: str
    document_parsing_used: Literal[False] = False
    generated_at: str


class BenchmarkAnalysisResponse(BaseModel):
    id: str
    execution_status: IntelligenceExecutionStatus = "basic_analysis"
    mode: IntelligenceMode = "deterministic_placeholder"
    provider: IntelligenceProviderName = "placeholder"
    model_profile: QualityProfile | None = None
    fallback_reason: FallbackReason | None = None
    retryable: bool = False
    request_id: str
    scope: Literal["benchmark_analysis"] = "benchmark_analysis"
    recommended_platform: str | None
    ranking_rationale: LocalizedText
    technical_fit_analysis: LocalizedText
    preference_impact: LocalizedText
    risk_assessment: LocalizedText
    assumptions: list[LocalizedText]
    uncertainty: list[LocalizedText]
    next_actions: list[LocalizedText]
    sources: list[IntelligenceSource]
    baseline: list[dict]
    ai_used: bool = False
    document_parsing_used: Literal[False] = False
    generated_at: str


class ProjectSummaryResponse(BaseModel):
    id: str
    execution_status: IntelligenceExecutionStatus = "basic_analysis"
    mode: IntelligenceMode = "deterministic_placeholder"
    provider: IntelligenceProviderName = "placeholder"
    model_profile: QualityProfile | None = None
    fallback_reason: FallbackReason | None = None
    retryable: bool = False
    request_id: str
    scope: Literal["project_summary"] = "project_summary"
    summary: LocalizedText
    recommended_focus: list[LocalizedText]
    assumptions: list[LocalizedText]
    uncertainty: list[LocalizedText]
    next_actions: list[LocalizedText]
    sources: list[IntelligenceSource]
    ai_used: bool = False
    document_parsing_used: Literal[False] = False
    generated_at: str


class AIConfigurationStatus(BaseModel):
    configured: bool
    provider: str
    quality_profiles: list[QualityProfile]
    fallback_enabled: bool
    configuration_errors: list[str]


class ConnectionTestResponse(BaseModel):
    connected: bool
    provider: IntelligenceProviderName
    model_profile: QualityProfile | None
    latency_ms: int
    error_category: SafeProviderError | None
