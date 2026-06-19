from fastapi import APIRouter, Depends, HTTPException

from app.intelligence.dependencies import get_ai_configuration_status
from app.intelligence.models import (
    AIConfigurationStatus,
    BenchmarkExplanationRequest,
    ConnectionTestResponse,
    GlobalChatRequest,
    IntelligenceResponse,
    ProjectAnalysisRequest,
    ProjectChatRequest,
    ReportGenerationRequest,
    ReportGenerationResponse,
    ReportSectionRewriteRequest,
)
from app.intelligence.service import (
    IntelligencePlatformError,
    IntelligenceProviderUnavailableError,
    IntelligenceProjectNotFoundError,
    IntelligenceSectionNotFoundError,
    analyze_project,
    explain_benchmark,
    generate_report,
    global_chat,
    project_chat,
    rewrite_report_section,
    test_connection,
)

router = APIRouter()


def _run(action):
    try:
        return action()
    except IntelligenceProjectNotFoundError as error:
        raise HTTPException(status_code=404, detail="Project not found") from error
    except IntelligenceSectionNotFoundError as error:
        raise HTTPException(status_code=404, detail="Report section not found") from error
    except (IntelligencePlatformError, ValueError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except IntelligenceProviderUnavailableError as error:
        raise HTTPException(
            status_code=502,
            detail={"error_category": error.category},
        ) from error


@router.get("/intelligence/status", response_model=AIConfigurationStatus)
def get_intelligence_status(
    status: AIConfigurationStatus = Depends(get_ai_configuration_status),
) -> AIConfigurationStatus:
    return status


@router.post("/intelligence/connection-test", response_model=ConnectionTestResponse)
def post_connection_test() -> ConnectionTestResponse:
    return test_connection()


@router.post("/intelligence/global/chat", response_model=IntelligenceResponse)
def post_global_chat(payload: GlobalChatRequest) -> IntelligenceResponse:
    return _run(lambda: global_chat(payload))


@router.post("/projects/{project_id}/intelligence/chat", response_model=IntelligenceResponse)
def post_project_chat(project_id: str, payload: ProjectChatRequest) -> IntelligenceResponse:
    return _run(lambda: project_chat(project_id, payload))


@router.post("/projects/{project_id}/intelligence/analyze", response_model=IntelligenceResponse)
def post_project_analysis(project_id: str, payload: ProjectAnalysisRequest) -> IntelligenceResponse:
    return _run(lambda: analyze_project(project_id, payload))


@router.post("/projects/{project_id}/benchmark/explain", response_model=IntelligenceResponse)
def post_benchmark_explanation(project_id: str, payload: BenchmarkExplanationRequest) -> IntelligenceResponse:
    return _run(lambda: explain_benchmark(project_id, payload))


@router.post("/projects/{project_id}/report/generate", response_model=ReportGenerationResponse)
def post_report_generation(project_id: str, payload: ReportGenerationRequest) -> ReportGenerationResponse:
    return _run(lambda: generate_report(project_id, payload))


@router.post("/projects/{project_id}/report/sections/{section_id}/rewrite", response_model=IntelligenceResponse)
def post_report_section_rewrite(
    project_id: str,
    section_id: str,
    payload: ReportSectionRewriteRequest,
) -> IntelligenceResponse:
    return _run(lambda: rewrite_report_section(project_id, section_id, payload))
