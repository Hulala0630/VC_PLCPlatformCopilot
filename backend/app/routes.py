from fastapi import APIRouter

from app.data import PLATFORMS
from app.models import MigrationEstimate, MigrationEstimateRequest, PlatformProfile
from app.services import estimate_migration

router = APIRouter()


@router.get("/platforms", response_model=list[PlatformProfile])
def list_platforms() -> list[PlatformProfile]:
    return PLATFORMS


@router.post("/migration-estimate", response_model=MigrationEstimate)
def create_migration_estimate(request: MigrationEstimateRequest) -> MigrationEstimate:
    return estimate_migration(request)
