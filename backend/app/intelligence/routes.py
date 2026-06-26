from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from app.intelligence.dependencies import get_ai_configuration_status
from app.intelligence.models import (
    AIConfigurationStatus,
    BenchmarkAnalysisRequest,
    BenchmarkAnalysisResponse,
    BenchmarkExplanationRequest,
    ConnectionTestResponse,
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
)
from app.intelligence.service import (
    IntelligencePlatformError,
    IntelligenceProviderUnavailableError,
    IntelligenceProjectNotFoundError,
    IntelligenceSectionNotFoundError,
    analyze_benchmark,
    analyze_project,
    explain_benchmark,
    generate_report,
    global_chat,
    project_chat,
    rewrite_report_section,
    stream_benchmark_analysis,
    stream_project_summary,
    summarize_project,
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
            detail={
                "error": "intelligence_request_failed",
                "fallback_reason": error.reason,
                "retryable": error.retryable,
                "request_id": error.request_id,
            },
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


@router.post("/projects/{project_id}/intelligence/benchmark", response_model=BenchmarkAnalysisResponse)
def post_benchmark_analysis(project_id: str, payload: BenchmarkAnalysisRequest) -> BenchmarkAnalysisResponse:
    return _run(lambda: analyze_benchmark(project_id, payload))


@router.post("/projects/{project_id}/intelligence/summary", response_model=ProjectSummaryResponse)
def post_project_summary(project_id: str, payload: ProjectSummaryRequest) -> ProjectSummaryResponse:
    return _run(lambda: summarize_project(project_id, payload))


@router.post("/projects/{project_id}/intelligence/benchmark/stream")
def post_benchmark_analysis_stream(project_id: str, payload: BenchmarkAnalysisRequest) -> StreamingResponse:
    stream = _run(lambda: stream_benchmark_analysis(project_id, payload))
    return StreamingResponse(stream, media_type="text/event-stream")


@router.post("/projects/{project_id}/intelligence/summary/stream")
def post_project_summary_stream(project_id: str, payload: ProjectSummaryRequest) -> StreamingResponse:
    stream = _run(lambda: stream_project_summary(project_id, payload))
    return StreamingResponse(stream, media_type="text/event-stream")


@router.post("/projects/{project_id}/report/generate", response_model=ReportGenerationResponse)
def post_report_generation(project_id: str, payload: ReportGenerationRequest) -> ReportGenerationResponse:
    return _run(lambda: generate_report(project_id, payload))


@router.post(
    "/projects/{project_id}/report/sections/{section_id}/rewrite",
    response_model=ReportSectionRewriteResponse,
)
def post_report_section_rewrite(
    project_id: str,
    section_id: str,
    payload: ReportSectionRewriteRequest,
) -> ReportSectionRewriteResponse:
    return _run(lambda: rewrite_report_section(project_id, section_id, payload))
