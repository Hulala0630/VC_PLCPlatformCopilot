from collections.abc import Callable
from datetime import UTC, datetime
from time import perf_counter, sleep
from typing import Any
from uuid import uuid4

import openai
from openai import OpenAI
from pydantic import BaseModel, ValidationError, field_validator, model_validator

from app.intelligence.config import AISettings
from app.intelligence.model_router import IntelligenceCapability, ModelRouter
from app.intelligence.models import (
    BenchmarkAnalysisRequest,
    BenchmarkAnalysisResponse,
    BenchmarkExplanationRequest,
    ConnectionTestResponse,
    GeneratedReportSection,
    GlobalChatRequest,
    IntelligenceResponse,
    ProjectAnalysisRequest,
    ProjectChatRequest,
    ProjectSummaryRequest,
    ProjectSummaryResponse,
    QualityProfile,
    ReportGenerationRequest,
    ReportGenerationResponse,
    ReportSectionRewriteRequest,
    ReportSectionRewriteResponse,
    SafeProviderError,
)
from app.intelligence.prompts import (
    PromptBundle,
    benchmark_analysis_prompt,
    benchmark_explanation_prompt,
    connection_test_prompt,
    global_chat_prompt,
    project_analysis_prompt,
    project_chat_prompt,
    project_summary_prompt,
    report_generation_prompt,
    report_section_rewrite_prompt,
)
from app.intelligence.provider import DeterministicPlaceholderProvider
from app.models import BenchmarkResult, LocalizedText, PlcEcosystem, ProjectWorkspace, ReportSection


class ProviderCallError(Exception):
    def __init__(self, category: SafeProviderError, profile: QualityProfile) -> None:
        super().__init__(category)
        self.category = category
        self.profile = profile


class _StructuredIntelligenceOutput(BaseModel):
    answer: LocalizedText
    assumptions: list[LocalizedText]
    uncertainty: list[LocalizedText]
    follow_up_questions: list[LocalizedText]

    @field_validator("answer")
    @classmethod
    def answer_must_be_bilingual(cls, value: LocalizedText) -> LocalizedText:
        if not value.zh.strip() or not value.en.strip():
            raise ValueError("Bilingual answer is required.")
        return value

    @model_validator(mode="after")
    def user_content_must_avoid_engineering_terms(self):
        _ensure_user_safe_text(
            [self.answer, *self.assumptions, *self.uncertainty, *self.follow_up_questions]
        )
        return self


class _StructuredReportSection(BaseModel):
    section_id: str
    draft_body: LocalizedText

    @field_validator("draft_body")
    @classmethod
    def body_must_be_bilingual(cls, value: LocalizedText) -> LocalizedText:
        if not value.zh.strip() or not value.en.strip():
            raise ValueError("Bilingual report body is required.")
        return value


class _StructuredReportOutput(BaseModel):
    sections: list[_StructuredReportSection]
    assumptions: list[LocalizedText]
    uncertainty: list[LocalizedText]

    @model_validator(mode="after")
    def user_content_must_avoid_engineering_terms(self):
        _ensure_user_safe_text(
            [
                *(section.draft_body for section in self.sections),
                *self.assumptions,
                *self.uncertainty,
            ]
        )
        return self


class _StructuredSectionRewriteOutput(BaseModel):
    section_id: str
    suggested_body: LocalizedText
    assumptions: list[LocalizedText]
    uncertainty: list[LocalizedText]

    @field_validator("suggested_body")
    @classmethod
    def body_must_be_bilingual(cls, value: LocalizedText) -> LocalizedText:
        if not value.zh.strip() or not value.en.strip():
            raise ValueError("Bilingual report body is required.")
        return value

    @model_validator(mode="after")
    def user_content_must_avoid_engineering_terms(self):
        _ensure_user_safe_text([self.suggested_body, *self.assumptions, *self.uncertainty])
        return self


class _StructuredBenchmarkAnalysisOutput(BaseModel):
    recommended_platform: str | None
    ranking_rationale: LocalizedText
    technical_fit_analysis: LocalizedText
    preference_impact: LocalizedText
    risk_assessment: LocalizedText
    assumptions: list[LocalizedText]
    uncertainty: list[LocalizedText]
    next_actions: list[LocalizedText]

    @model_validator(mode="after")
    def user_content_must_avoid_engineering_terms(self):
        _ensure_user_safe_text(
            [
                self.ranking_rationale,
                self.technical_fit_analysis,
                self.preference_impact,
                self.risk_assessment,
                *self.assumptions,
                *self.uncertainty,
                *self.next_actions,
            ]
        )
        return self


class _StructuredProjectSummaryOutput(BaseModel):
    summary: LocalizedText
    recommended_focus: list[LocalizedText]
    assumptions: list[LocalizedText]
    uncertainty: list[LocalizedText]
    next_actions: list[LocalizedText]

    @model_validator(mode="after")
    def user_content_must_avoid_engineering_terms(self):
        _ensure_user_safe_text(
            [
                self.summary,
                *self.recommended_focus,
                *self.assumptions,
                *self.uncertainty,
                *self.next_actions,
            ]
        )
        return self


class OpenAIProvider:
    mode = "openai"

    def __init__(
        self,
        settings: AISettings,
        *,
        client: Any | None = None,
        sleep_fn: Callable[[float], None] = sleep,
        clock: Callable[[], float] = perf_counter,
    ) -> None:
        self._settings = settings
        self._router = ModelRouter(settings)
        self._placeholder = DeterministicPlaceholderProvider()
        self._sleep = sleep_fn
        self._clock = clock
        self._client = client or OpenAI(
            api_key=settings.openai_api_key.get_secret_value() if settings.openai_api_key else None,
            base_url=settings.openai_base_url,
            timeout=settings.ai_request_timeout_seconds,
            max_retries=0,
        )

    def global_chat(self, request: GlobalChatRequest, platforms: list[PlcEcosystem]) -> IntelligenceResponse:
        baseline = self._placeholder.global_chat(request, platforms)
        return self._intelligence_response(
            baseline,
            "global_chat",
            request.quality_profile,
            global_chat_prompt(request, platforms),
        )

    def project_chat(
        self,
        request: ProjectChatRequest,
        workspace: ProjectWorkspace,
        benchmark: list[BenchmarkResult],
    ) -> IntelligenceResponse:
        baseline = self._placeholder.project_chat(request, workspace, benchmark)
        return self._intelligence_response(
            baseline,
            "project_chat",
            request.quality_profile,
            project_chat_prompt(request, workspace, benchmark),
        )

    def analyze_project(
        self,
        request: ProjectAnalysisRequest,
        workspace: ProjectWorkspace,
        benchmark: list[BenchmarkResult],
    ) -> IntelligenceResponse:
        baseline = self._placeholder.analyze_project(request, workspace, benchmark)
        response = self._intelligence_response(
            baseline,
            "project_analysis",
            request.quality_profile,
            project_analysis_prompt(request, workspace, benchmark),
        )
        if request.focus == "attachments":
            response = response.model_copy(
                update={
                    "answer": LocalizedText(
                        zh=f"{baseline.answer.zh} {response.answer.zh}",
                        en=f"{baseline.answer.en} {response.answer.en}",
                    ),
                    "next_actions": baseline.next_actions,
                }
            )
        return response

    def explain_benchmark(
        self,
        request: BenchmarkExplanationRequest,
        workspace: ProjectWorkspace,
        benchmark: list[BenchmarkResult],
    ) -> IntelligenceResponse:
        baseline = self._placeholder.explain_benchmark(request, workspace, benchmark)
        return self._intelligence_response(
            baseline,
            "benchmark_explanation",
            request.quality_profile,
            benchmark_explanation_prompt(request, workspace, benchmark),
        )

    def analyze_benchmark(
        self,
        request: BenchmarkAnalysisRequest,
        workspace: ProjectWorkspace,
        benchmark: list[BenchmarkResult],
    ) -> BenchmarkAnalysisResponse:
        baseline = self._placeholder.analyze_benchmark(request, workspace, benchmark)
        profile = self._router.profile_for("benchmark_analysis", request.quality_profile)
        response, parsed = self._parse(
            profile,
            benchmark_analysis_prompt(request, workspace, benchmark),
            _StructuredBenchmarkAnalysisOutput,
        )
        if parsed.recommended_platform is not None and parsed.recommended_platform not in {
            item.platform_id for item in benchmark
        }:
            raise ProviderCallError("invalid_response", profile)
        return baseline.model_copy(
            update={
                "mode": "openai",
                "execution_status": "ai_success",
                "provider": "openai",
                "model_profile": profile,
                "fallback_reason": None,
                "request_id": self._request_id(response),
                "recommended_platform": parsed.recommended_platform,
                "ranking_rationale": parsed.ranking_rationale,
                "technical_fit_analysis": parsed.technical_fit_analysis,
                "preference_impact": parsed.preference_impact,
                "risk_assessment": parsed.risk_assessment,
                "assumptions": _merge_localized(baseline.assumptions, parsed.assumptions),
                "uncertainty": _merge_localized(baseline.uncertainty, parsed.uncertainty),
                "next_actions": _merge_localized(baseline.next_actions, parsed.next_actions),
                "ai_used": True,
                "generated_at": _now(),
            }
        )

    def summarize_project(
        self,
        request: ProjectSummaryRequest,
        workspace: ProjectWorkspace,
        benchmark: list[BenchmarkResult],
    ) -> ProjectSummaryResponse:
        baseline = self._placeholder.summarize_project(request, workspace, benchmark)
        profile = self._router.profile_for("project_summary", request.quality_profile)
        response, parsed = self._parse(
            profile,
            project_summary_prompt(request, workspace, benchmark),
            _StructuredProjectSummaryOutput,
        )
        return baseline.model_copy(
            update={
                "mode": "openai",
                "execution_status": "ai_success",
                "provider": "openai",
                "model_profile": profile,
                "fallback_reason": None,
                "request_id": self._request_id(response),
                "summary": parsed.summary,
                "recommended_focus": _merge_localized(baseline.recommended_focus, parsed.recommended_focus),
                "assumptions": _merge_localized(baseline.assumptions, parsed.assumptions),
                "uncertainty": _merge_localized(baseline.uncertainty, parsed.uncertainty),
                "next_actions": _merge_localized(baseline.next_actions, parsed.next_actions),
                "ai_used": True,
                "generated_at": _now(),
            }
        )

    def generate_report(
        self,
        request: ReportGenerationRequest,
        workspace: ProjectWorkspace,
        benchmark: list[BenchmarkResult],
    ) -> ReportGenerationResponse:
        baseline = self._placeholder.generate_report(request, workspace, benchmark)
        profile = self._router.profile_for("report_generation", request.quality_profile)
        response, parsed = self._parse(
            profile,
            report_generation_prompt(request, workspace, benchmark),
            _StructuredReportOutput,
        )
        sections = self._validated_report_sections(parsed, workspace.report.sections, profile)
        return baseline.model_copy(
            update={
                "mode": "openai",
                "execution_status": "ai_success",
                "provider": "openai",
                "model_profile": profile,
                "fallback_reason": None,
                "request_id": self._request_id(response),
                "sections": sections,
                "assumptions": _merge_localized(baseline.assumptions, parsed.assumptions),
                "uncertainty": _merge_localized(baseline.uncertainty, parsed.uncertainty),
                "ai_used": True,
                "generated_at": _now(),
            }
        )

    def rewrite_report_section(
        self,
        request: ReportSectionRewriteRequest,
        workspace: ProjectWorkspace,
        section: ReportSection,
        benchmark: list[BenchmarkResult],
    ) -> ReportSectionRewriteResponse:
        baseline = self._placeholder.rewrite_report_section(request, workspace, section, benchmark)
        profile = self._router.profile_for("report_section_rewrite", request.quality_profile)
        response, parsed = self._parse(
            profile,
            report_section_rewrite_prompt(request, workspace, section, benchmark),
            _StructuredSectionRewriteOutput,
        )
        if parsed.section_id != section.id:
            raise ProviderCallError("invalid_response", profile)
        return baseline.model_copy(
            update={
                "mode": "openai",
                "execution_status": "ai_success",
                "provider": "openai",
                "model_profile": profile,
                "fallback_reason": None,
                "request_id": self._request_id(response),
                "suggested_body": parsed.suggested_body,
                "assumptions": _merge_localized(baseline.assumptions, parsed.assumptions),
                "uncertainty": _merge_localized(baseline.uncertainty, parsed.uncertainty),
                "ai_used": True,
                "generated_at": _now(),
            }
        )

    def connection_test(self) -> ConnectionTestResponse:
        profile: QualityProfile = "fast"
        model = self._router.model_for(profile)
        prompt = connection_test_prompt()
        started = self._clock()
        try:
            self._call_with_retry(
                profile,
                lambda: self._client.responses.create(
                    model=model,
                    instructions=prompt.instructions,
                    input=prompt.input,
                    max_output_tokens=64,
                    store=False,
                    timeout=self._settings.ai_request_timeout_seconds,
                ),
            )
        except ProviderCallError as error:
            return ConnectionTestResponse(
                connected=False,
                provider="openai",
                model_profile=profile,
                latency_ms=max(0, round((self._clock() - started) * 1000)),
                error_category=error.category,
            )
        return ConnectionTestResponse(
            connected=True,
            provider="openai",
            model_profile=profile,
            latency_ms=max(0, round((self._clock() - started) * 1000)),
            error_category=None,
        )

    def _intelligence_response(
        self,
        baseline: IntelligenceResponse,
        capability: IntelligenceCapability,
        override: QualityProfile | None,
        prompt: PromptBundle,
    ) -> IntelligenceResponse:
        profile = self._router.profile_for(capability, override)
        response, parsed = self._parse(profile, prompt, _StructuredIntelligenceOutput)
        return baseline.model_copy(
            update={
                "mode": "openai",
                "execution_status": "ai_success",
                "provider": "openai",
                "model_profile": profile,
                "fallback_reason": None,
                "request_id": self._request_id(response),
                "answer": parsed.answer,
                "assumptions": _merge_localized(baseline.assumptions, parsed.assumptions),
                "uncertainty": _merge_localized(baseline.uncertainty, parsed.uncertainty),
                "follow_up_questions": parsed.follow_up_questions,
                "ai_used": True,
                "generated_at": _now(),
            }
        )

    def _parse(self, profile: QualityProfile, prompt: PromptBundle, output_type: type[BaseModel]):
        model = self._router.model_for(profile)

        def call():
            response = self._client.responses.parse(
                model=model,
                instructions=prompt.instructions,
                input=prompt.input,
                text_format=output_type,
                store=False,
                timeout=self._settings.ai_request_timeout_seconds,
            )
            parsed = getattr(response, "output_parsed", None)
            if parsed is None:
                raise _InvalidStructuredOutputError()
            if not isinstance(parsed, output_type):
                parsed = output_type.model_validate(parsed)
            return response, parsed

        return self._call_with_retry(profile, call)

    def _call_with_retry(self, profile: QualityProfile, call: Callable[[], Any]):
        attempts = self._settings.ai_max_retries + 1
        last_error: ProviderCallError | None = None
        for attempt in range(attempts):
            try:
                return call()
            except Exception as error:
                categorized = ProviderCallError(_error_category(error), profile)
                last_error = categorized
                if attempt >= attempts - 1 or not _retryable(categorized.category):
                    raise categorized from None
                self._sleep(0.25 * (2**attempt))
        raise last_error or ProviderCallError("connection_error", profile)

    def _validated_report_sections(
        self,
        parsed: _StructuredReportOutput,
        existing: list[ReportSection],
        profile: QualityProfile,
    ) -> list[GeneratedReportSection]:
        expected_ids = [section.id for section in existing]
        returned_ids = [section.section_id for section in parsed.sections]
        if returned_ids != expected_ids or len(set(returned_ids)) != len(returned_ids):
            raise ProviderCallError("invalid_response", profile)
        existing_by_id = {section.id: section for section in existing}
        return [
            GeneratedReportSection(
                section_id=item.section_id,
                title=existing_by_id[item.section_id].title,
                draft_body=item.draft_body,
            )
            for item in parsed.sections
        ]

    def _request_id(self, response: Any) -> str:
        request_id = getattr(response, "_request_id", None) or getattr(response, "id", None)
        return str(request_id) if request_id else f"request-{uuid4().hex}"


class _InvalidStructuredOutputError(Exception):
    pass


def _ensure_user_safe_text(values: list[LocalizedText]) -> None:
    forbidden = (
        "placeholder",
        "provider",
        "fallback",
        "deterministic_fallback",
        "deterministic",
        "deterministic service",
        "metadata",
        "mock",
        "internal",
        "dev wording",
        "developer wording",
        "model id",
        "model_id",
        "api key",
        "api_key",
        "authorization header",
        "secret key",
        "persistence",
        "persisted",
        "scoring logic",
        "deterministic scoring",
        "does not modify scoring logic",
        "will not overwrite charts",
        "元数据",
        "持久化",
        "不会修改评分逻辑",
        "不会覆盖图表",
    )
    for value in values:
        combined = f"{value.zh}\n{value.en}".lower()
        if any(term.lower() in combined for term in forbidden):
            raise ValueError("User-facing content contains an internal implementation term.")


def _error_category(error: Exception) -> SafeProviderError:
    if isinstance(error, (ValidationError, _InvalidStructuredOutputError)):
        return "invalid_response"
    if isinstance(error, openai.APITimeoutError):
        return "timeout"
    if isinstance(error, openai.AuthenticationError):
        return "authentication"
    if isinstance(error, openai.RateLimitError):
        return "rate_limit"
    if isinstance(error, openai.InternalServerError):
        return "provider_server_error"
    if isinstance(error, openai.BadRequestError):
        if _provider_error_param(error) == "text.format":
            return "unsupported_response_format"
        return "invalid_request"
    if isinstance(error, openai.NotFoundError):
        return "unsupported_model"
    if isinstance(error, openai.APIConnectionError):
        return "connection_error"
    if isinstance(error, openai.APIStatusError) and error.status_code >= 500:
        return "provider_server_error"
    return "connection_error"


def _provider_error_param(error: openai.BadRequestError) -> str | None:
    body = getattr(error, "body", None)
    if not isinstance(body, dict):
        return None
    nested = body.get("error")
    source = nested if isinstance(nested, dict) else body
    param = source.get("param")
    return str(param) if param else None


def _retryable(category: SafeProviderError) -> bool:
    return category in {
        "timeout",
        "rate_limit",
        "provider_server_error",
        "invalid_response",
        "connection_error",
    }


def _merge_localized(base: list[LocalizedText], generated: list[LocalizedText]) -> list[LocalizedText]:
    values: list[LocalizedText] = []
    seen: set[tuple[str, str]] = set()
    for item in [*base, *generated]:
        key = (item.zh, item.en)
        if key not in seen:
            values.append(item)
            seen.add(key)
    return values


def _now() -> str:
    return datetime.now(UTC).isoformat()
