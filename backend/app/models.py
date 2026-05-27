from typing import Literal

from pydantic import BaseModel, Field


class PlatformScores(BaseModel):
    productivity: int = Field(ge=0, le=100)
    motion: int = Field(ge=0, le=100)
    safety: int = Field(ge=0, le=100)
    simulation: int = Field(ge=0, le=100)
    openness: int = Field(ge=0, le=100)
    scalability: int = Field(ge=0, le=100)
    talent: int = Field(ge=0, le=100)
    cost_efficiency: int = Field(ge=0, le=100)


class PlatformMetrics(BaseModel):
    tco_index: int = Field(ge=0, le=100)
    learning_curve: int = Field(ge=0, le=100)
    vendor_lock_in: int = Field(ge=0, le=100)
    migration_complexity: int = Field(ge=0, le=100)


class PlatformProfile(BaseModel):
    id: str
    name: str
    vendor: str
    summary: str
    best_for: list[str]
    business_position: str
    licensing_model: str
    engineering_software: str
    ecosystem_risk: Literal["Low", "Medium", "High"]
    scores: PlatformScores
    metrics: PlatformMetrics


class MigrationEstimateRequest(BaseModel):
    source: str
    target: str
    reusable_assets: int = Field(ge=0, le=100)
    rewrite_effort: int = Field(ge=0, le=100)
    testing_effort: int = Field(ge=0, le=100)
    validation_effort: int = Field(ge=0, le=100)
    training_effort: int = Field(ge=0, le=100)
    downtime_risk: int = Field(ge=0, le=100)


class MigrationEstimate(BaseModel):
    engineering_effort_index: int = Field(ge=0, le=100)
    cost_level: str
    uncertainty: str
    assumptions: list[str]
