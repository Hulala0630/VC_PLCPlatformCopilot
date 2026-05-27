from fastapi import APIRouter, HTTPException

from app.data import ECOSYSTEMS, PROJECT_WORKSPACES
from app.models import BenchmarkResult, PlcEcosystem, ProjectWorkspace
from app.services import create_benchmark

router = APIRouter()


@router.get("/ecosystems", response_model=list[PlcEcosystem])
def list_ecosystems() -> list[PlcEcosystem]:
    return ECOSYSTEMS


@router.get("/platforms", response_model=list[PlcEcosystem])
def list_platforms() -> list[PlcEcosystem]:
    return ECOSYSTEMS


@router.get("/projects", response_model=list[ProjectWorkspace])
def list_projects() -> list[ProjectWorkspace]:
    return PROJECT_WORKSPACES


@router.get("/projects/{project_id}", response_model=ProjectWorkspace)
def get_project(project_id: str) -> ProjectWorkspace:
    for workspace in PROJECT_WORKSPACES:
        if workspace.project.id == project_id:
            return workspace
    raise HTTPException(status_code=404, detail="Project not found")


@router.post("/benchmark", response_model=list[BenchmarkResult])
def benchmark_project(workspace: ProjectWorkspace) -> list[BenchmarkResult]:
    return create_benchmark(workspace)
