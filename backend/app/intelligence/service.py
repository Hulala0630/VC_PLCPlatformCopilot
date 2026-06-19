from datetime import UTC, datetime
from uuid import uuid4

from app.data import ECOSYSTEMS
from app.intelligence.models import (
    BenchmarkExplanationRequest,
    ConnectionTestResponse,
    GlobalChatRequest,
    IntelligenceResponse,
    ProjectAnalysisRequest,
    ProjectChatRequest,
    ReportGenerationRequest,
    ReportGenerationResponse,
    ReportSectionRewriteRequest,
    SafeProviderError,
)
from app.intelligence.openai_provider import OpenAIProvider, ProviderCallError
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
    def __init__(self, category: SafeProviderError) -> None:
        super().__init__(category)
        self.category = category


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


def generate_report(project_id: str, request: ReportGenerationRequest) -> ReportGenerationResponse:
    workspace = _workspace(project_id)
    return _execute("generate_report", request, workspace, create_benchmark(workspace))


def rewrite_report_section(
    project_id: str,
    section_id: str,
    request: ReportSectionRewriteRequest,
) -> IntelligenceResponse:
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


def _execute(method_name: str, *args):
    selection = get_provider_selection()
    request = args[0] if args else None
    use_ai = getattr(request, "use_ai", True)
    provider = selection.primary if use_ai else selection.placeholder
    method = getattr(provider, method_name)
    try:
        return method(*args)
    except ProviderCallError as error:
        if use_ai and selection.openai_active and selection.fallback_enabled:
            fallback = getattr(selection.placeholder, method_name)(*args)
            return _mark_fallback(fallback, error)
        raise IntelligenceProviderUnavailableError(error.category) from None


def _mark_fallback(response, error: ProviderCallError):
    return response.model_copy(
        update={
            "mode": "deterministic_fallback",
            "provider": "placeholder",
            "model_profile": error.profile,
            "fallback_reason": error.category,
            "request_id": f"fallback-{uuid4().hex}",
            "ai_used": False,
            "generated_at": datetime.now(UTC).isoformat(),
        }
    )


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
