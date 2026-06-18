from typing import Literal

from pydantic import BaseModel, Field, field_validator

from app.models import Language, LocalizedText


IntelligenceMode = Literal["deterministic_placeholder"]
IntelligenceScope = Literal[
    "global",
    "project",
    "project_analysis",
    "benchmark_explanation",
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


def _non_empty(value: str) -> str:
    value = value.strip()
    if not value:
        raise ValueError("Value must not be empty.")
    return value


class GlobalChatRequest(BaseModel):
    question: str
    language: Language
    platform_ids: list[str] = Field(default_factory=list)

    @field_validator("question")
    @classmethod
    def validate_question(cls, value: str) -> str:
        return _non_empty(value)


class ProjectChatRequest(BaseModel):
    question: str
    language: Language

    @field_validator("question")
    @classmethod
    def validate_question(cls, value: str) -> str:
        return _non_empty(value)


class ProjectAnalysisRequest(BaseModel):
    language: Language


class BenchmarkExplanationRequest(BaseModel):
    language: Language


class ReportGenerationRequest(BaseModel):
    language: Language
    audience: ReportAudience


class ReportSectionRewriteRequest(BaseModel):
    instruction: str
    language: Language
    audience: ReportAudience

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
    mode: IntelligenceMode = "deterministic_placeholder"
    scope: IntelligenceScope
    answer: LocalizedText
    sources: list[IntelligenceSource]
    assumptions: list[LocalizedText]
    uncertainty: list[LocalizedText]
    missing_inputs: list[LocalizedText]
    follow_up_questions: list[LocalizedText]
    ai_used: Literal[False] = False
    document_parsing_used: Literal[False] = False
    generated_at: str


class GeneratedReportSection(BaseModel):
    section_id: str
    title: LocalizedText
    draft_body: LocalizedText


class ReportGenerationResponse(BaseModel):
    id: str
    mode: IntelligenceMode = "deterministic_placeholder"
    scope: Literal["report_generation"] = "report_generation"
    audience: ReportAudience
    sections: list[GeneratedReportSection]
    sources: list[IntelligenceSource]
    assumptions: list[LocalizedText]
    uncertainty: list[LocalizedText]
    missing_inputs: list[LocalizedText]
    ai_used: Literal[False] = False
    document_parsing_used: Literal[False] = False
    generated_at: str
