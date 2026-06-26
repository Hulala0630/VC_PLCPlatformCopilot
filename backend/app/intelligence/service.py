import json
from datetime import UTC, datetime
from collections.abc import Iterator
from uuid import uuid4

from app.data import ECOSYSTEMS
from app.intelligence.models import (
    BenchmarkAnalysisRequest,
    BenchmarkAnalysisResponse,
    BenchmarkExplanationRequest,
    ConnectionTestResponse,
    FallbackReason,
    GlobalChatRequest,
    IntelligenceResponse,
    ProjectAnalysisRequest,
    ProjectChatRequest,
    ProjectSummaryRequest,
    ProjectSummaryResponse,
    ReportGenerationRequest,
    ReportGenerationResponse,
    ReportSectionRewriteRequest,
    ReportSectionRewriteResponse,
    SafeProviderError,
)
from app.intelligence.openai_provider import OpenAIProvider, ProviderCallError
from app.intelligence.provider import DeterministicPlaceholderProvider
from app.intelligence.provider_factory import get_provider_selection
from app.models import PlcEcosystem, ProjectWorkspace, ReportSection
from app.services import create_benchmark, get_workspace


class IntelligenceProjectNotFoundError(Exception):
    pass


class IntelligenceSectionNotFoundError(Exception):
    pass


class IntelligencePlatformError(ValueError):
    pass


class IntelligenceProviderUnavailableError(Exception):
    def __init__(self, reason: FallbackReason, retryable: bool) -> None:
        super().__init__(reason)
        self.reason = reason
        self.retryable = retryable
        self.request_id = f"failed-{uuid4().hex}"


_deterministic_provider = DeterministicPlaceholderProvider()


def global_chat(request: GlobalChatRequest) -> IntelligenceResponse:
    platforms = _platforms(request.platform_ids)
    return _execute("global_chat", request, platforms)


def project_chat(project_id: str, request: ProjectChatRequest) -> IntelligenceResponse:
    workspace = _workspace(project_id)
    return _execute("project_chat", request, workspace, create_benchmark(workspace))


def analyze_project(project_id: str, request: ProjectAnalysisRequest) -> IntelligenceResponse:
    workspace = _workspace(project_id)
    return _execute("analyze_project", request, workspace, create_benchmark(workspace))


def explain_benchmark(project_id: str, request: BenchmarkExplanationRequest) -> IntelligenceResponse:
    workspace = _workspace(project_id)
    return _execute("explain_benchmark", request, workspace, create_benchmark(workspace))


def analyze_benchmark(project_id: str, request: BenchmarkAnalysisRequest) -> BenchmarkAnalysisResponse:
    workspace = _workspace(project_id)
    return _execute("analyze_benchmark", request, workspace, create_benchmark(workspace))


def summarize_project(project_id: str, request: ProjectSummaryRequest) -> ProjectSummaryResponse:
    workspace = _workspace(project_id)
    return _execute("summarize_project", request, workspace, create_benchmark(workspace))


def stream_benchmark_analysis(project_id: str, request: BenchmarkAnalysisRequest) -> Iterator[str]:
    result = analyze_benchmark(project_id, request)
    return iter(
        [
            _sse(
                "chunk",
                {
                    "type": "chunk",
                    "done": False,
                    "content": result.ranking_rationale.model_dump(),
                    "request_id": result.request_id,
                },
            ),
            _sse("done", {"type": "done", "done": True, "result": result.model_dump(mode="json")}),
        ]
    )


def stream_project_summary(project_id: str, request: ProjectSummaryRequest) -> Iterator[str]:
    result = summarize_project(project_id, request)
    return iter(
        [
            _sse(
                "chunk",
                {
                    "type": "chunk",
                    "done": False,
                    "content": result.summary.model_dump(),
                    "request_id": result.request_id,
                },
            ),
            _sse("done", {"type": "done", "done": True, "result": result.model_dump(mode="json")}),
        ]
    )


def generate_report(project_id: str, request: ReportGenerationRequest) -> ReportGenerationResponse:
    workspace = _workspace(project_id)
    return _execute("generate_report", request, workspace, create_benchmark(workspace))


def rewrite_report_section(
    project_id: str,
    section_id: str,
    request: ReportSectionRewriteRequest,
) -> ReportSectionRewriteResponse:
    workspace = _workspace(project_id)
    section = _section(workspace, section_id)
    return _execute(
        "rewrite_report_section",
        request,
        workspace,
        section,
        create_benchmark(workspace),
    )


def test_connection() -> ConnectionTestResponse:
    selection = get_provider_selection()
    if selection.openai_active and isinstance(selection.primary, OpenAIProvider):
        return selection.primary.connection_test()
    return ConnectionTestResponse(
        connected=False,
        provider="placeholder",
        model_profile=None,
        latency_ms=0,
        error_category="configuration_error",
    )


def _execute(method_name: str, request, *args):
    if not request.use_ai:
        return getattr(_deterministic_provider, method_name)(request, *args)

    selection = get_provider_selection()
    if not selection.openai_active:
        error = ProviderCallError("configuration_error", _default_profile(method_name))
        if selection.fallback_enabled:
            fallback = getattr(selection.placeholder, method_name)(request, *args)
            return _mark_fallback(fallback, error)
        reason, retryable = _public_failure(error.category)
        raise IntelligenceProviderUnavailableError(reason, retryable)

    method = getattr(selection.primary, method_name)
    try:
        return method(request, *args)
    except ProviderCallError as error:
        if selection.openai_active and selection.fallback_enabled:
            fallback = getattr(selection.placeholder, method_name)(request, *args)
            return _mark_fallback(fallback, error)
        reason, retryable = _public_failure(error.category)
        raise IntelligenceProviderUnavailableError(reason, retryable) from None


def _mark_fallback(response, error: ProviderCallError):
    reason, retryable = _public_failure(error.category)
    return response.model_copy(
        update={
            "mode": "deterministic_fallback",
            "execution_status": "ai_fallback",
            "provider": "placeholder",
            "model_profile": error.profile,
            "fallback_reason": reason,
            "retryable": retryable,
            "request_id": f"fallback-{uuid4().hex}",
            "ai_used": False,
            "generated_at": datetime.now(UTC).isoformat(),
        }
    )


def _public_failure(category: SafeProviderError) -> tuple[FallbackReason, bool]:
    mapping: dict[SafeProviderError, tuple[FallbackReason, bool]] = {
        "timeout": ("timeout", True),
        "rate_limit": ("rate_limit", True),
        "authentication": ("authentication", False),
        "unsupported_model": ("unsupported_model", False),
        "invalid_response": ("invalid_response", True),
        "provider_server_error": ("provider_unavailable", True),
        "connection_error": ("provider_unavailable", True),
        "configuration_error": ("provider_unavailable", False),
        "invalid_request": ("provider_unavailable", False),
        "unsupported_response_format": ("provider_unavailable", False),
    }
    return mapping[category]


def _default_profile(method_name: str):
    if method_name in {"generate_report", "rewrite_report_section"}:
        return "quality"
    if method_name == "global_chat":
        return "fast"
    return "balanced"


def _sse(event: str, payload: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(payload, ensure_ascii=False, separators=(',', ':'))}\n\n"


def _workspace(project_id: str) -> ProjectWorkspace:
    workspace = get_workspace(project_id)
    if workspace is None:
        raise IntelligenceProjectNotFoundError(project_id)
    return workspace


def _section(workspace: ProjectWorkspace, section_id: str) -> ReportSection:
    section = next((item for item in workspace.report.sections if item.id == section_id), None)
    if section is None:
        raise IntelligenceSectionNotFoundError(section_id)
    return section


def _platforms(platform_ids: list[str]) -> list[PlcEcosystem]:
    if not platform_ids:
        return ECOSYSTEMS

    platform_by_id = {platform.id: platform for platform in ECOSYSTEMS}
    unknown = sorted({platform_id for platform_id in platform_ids if platform_id not in platform_by_id})
    if unknown:
        raise IntelligencePlatformError(f"Unknown platform: {', '.join(unknown)}")
    return [platform_by_id[platform_id] for platform_id in platform_ids]
