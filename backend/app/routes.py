from fastapi import APIRouter, HTTPException

from app.data import ECOSYSTEMS
from app.models import (
    BenchmarkResult,
    PlatformPreference,
    PlcEcosystem,
    ProjectAttachmentCreate,
    ProjectCreate,
    ProjectIntake,
    ProjectReadiness,
    ProjectStatusUpdate,
    ProjectWorkspace,
    ReportSectionUpdate,
)
from app.services import (
    add_attachment,
    create_benchmark,
    create_workspace,
    delete_workspace,
    get_project_readiness,
    get_workspace,
    list_workspaces,
    update_intake,
    update_preferences,
    update_project_status,
    update_report_section,
)

router = APIRouter()


def _workspace_or_404(project_id: str) -> ProjectWorkspace:
    workspace = get_workspace(project_id)
    if workspace is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return workspace


def _bad_request_from_value_error(error: ValueError) -> HTTPException:
    return HTTPException(status_code=400, detail=str(error))


@router.get("/ecosystems", response_model=list[PlcEcosystem])
def list_ecosystems() -> list[PlcEcosystem]:
    return ECOSYSTEMS


@router.get("/platforms", response_model=list[PlcEcosystem])
def list_platforms() -> list[PlcEcosystem]:
    return ECOSYSTEMS


@router.get("/projects", response_model=list[ProjectWorkspace])
def list_projects() -> list[ProjectWorkspace]:
    return list_workspaces()


@router.get("/projects/{project_id}", response_model=ProjectWorkspace)
def get_project(project_id: str) -> ProjectWorkspace:
    return _workspace_or_404(project_id)


@router.get("/projects/{project_id}/readiness", response_model=ProjectReadiness)
def get_readiness(project_id: str) -> ProjectReadiness:
    readiness = get_project_readiness(project_id)
    if readiness is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return readiness


@router.post("/projects", response_model=ProjectWorkspace, status_code=201)
def post_project(payload: ProjectCreate) -> ProjectWorkspace:
    return create_workspace(payload)


@router.delete("/projects/{project_id}", status_code=204)
def delete_project(project_id: str) -> None:
    deleted = delete_workspace(project_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Project not found")


@router.put("/projects/{project_id}/status", response_model=ProjectWorkspace)
def put_project_status(project_id: str, payload: ProjectStatusUpdate) -> ProjectWorkspace:
    try:
        workspace = update_project_status(project_id, payload)
    except ValueError as error:
        raise _bad_request_from_value_error(error) from error
    if workspace is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return workspace


@router.put("/projects/{project_id}/intake", response_model=ProjectWorkspace)
def put_project_intake(project_id: str, payload: ProjectIntake) -> ProjectWorkspace:
    try:
        workspace = update_intake(project_id, payload)
    except ValueError as error:
        raise _bad_request_from_value_error(error) from error
    if workspace is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return workspace


@router.put("/projects/{project_id}/preferences", response_model=ProjectWorkspace)
def put_project_preferences(project_id: str, payload: list[PlatformPreference]) -> ProjectWorkspace:
    try:
        workspace = update_preferences(project_id, payload)
    except ValueError as error:
        raise _bad_request_from_value_error(error) from error
    if workspace is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return workspace


@router.post("/projects/{project_id}/attachments", response_model=ProjectWorkspace)
def post_project_attachment(project_id: str, payload: ProjectAttachmentCreate) -> ProjectWorkspace:
    workspace = add_attachment(project_id, payload)
    if workspace is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return workspace


@router.post("/projects/{project_id}/benchmark", response_model=list[BenchmarkResult])
def benchmark_project(project_id: str) -> list[BenchmarkResult]:
    workspace = _workspace_or_404(project_id)
    try:
        return create_benchmark(workspace)
    except ValueError as error:
        raise _bad_request_from_value_error(error) from error


@router.post("/benchmark", response_model=list[BenchmarkResult])
def benchmark_workspace(payload: ProjectWorkspace) -> list[BenchmarkResult]:
    try:
        return create_benchmark(payload)
    except ValueError as error:
        raise _bad_request_from_value_error(error) from error


@router.put("/projects/{project_id}/report/sections/{section_id}", response_model=ProjectWorkspace)
def put_report_section(project_id: str, section_id: str, payload: ReportSectionUpdate) -> ProjectWorkspace:
    if get_workspace(project_id) is None:
        raise HTTPException(status_code=404, detail="Project not found")
    updated = update_report_section(project_id, section_id, payload)
    if updated is None:
        raise HTTPException(status_code=404, detail="Report section not found")
    return updated
