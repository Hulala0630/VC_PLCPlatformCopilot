from app.data import ECOSYSTEMS
from app.intelligence.models import (
    BenchmarkExplanationRequest,
    GlobalChatRequest,
    IntelligenceResponse,
    ProjectAnalysisRequest,
    ProjectChatRequest,
    ReportGenerationRequest,
    ReportGenerationResponse,
    ReportSectionRewriteRequest,
)
from app.intelligence.provider import DeterministicPlaceholderProvider, IntelligenceProvider
from app.models import PlcEcosystem, ProjectWorkspace, ReportSection
from app.services import create_benchmark, get_workspace


class IntelligenceProjectNotFoundError(Exception):
    pass


class IntelligenceSectionNotFoundError(Exception):
    pass


class IntelligencePlatformError(ValueError):
    pass


provider: IntelligenceProvider = DeterministicPlaceholderProvider()


def global_chat(request: GlobalChatRequest) -> IntelligenceResponse:
    platforms = _platforms(request.platform_ids)
    return provider.global_chat(request, platforms)


def project_chat(project_id: str, request: ProjectChatRequest) -> IntelligenceResponse:
    workspace = _workspace(project_id)
    return provider.project_chat(request, workspace, create_benchmark(workspace))


def analyze_project(project_id: str, request: ProjectAnalysisRequest) -> IntelligenceResponse:
    workspace = _workspace(project_id)
    return provider.analyze_project(request, workspace, create_benchmark(workspace))


def explain_benchmark(project_id: str, request: BenchmarkExplanationRequest) -> IntelligenceResponse:
    workspace = _workspace(project_id)
    return provider.explain_benchmark(request, workspace, create_benchmark(workspace))


def generate_report(project_id: str, request: ReportGenerationRequest) -> ReportGenerationResponse:
    workspace = _workspace(project_id)
    return provider.generate_report(request, workspace, create_benchmark(workspace))


def rewrite_report_section(
    project_id: str,
    section_id: str,
    request: ReportSectionRewriteRequest,
) -> IntelligenceResponse:
    workspace = _workspace(project_id)
    section = _section(workspace, section_id)
    return provider.rewrite_report_section(request, workspace, section, create_benchmark(workspace))


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
