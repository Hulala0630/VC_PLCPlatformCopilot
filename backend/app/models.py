from typing import Literal

from pydantic import BaseModel, Field


Language = Literal["zh", "en"]
RiskLevel = Literal["Low", "Medium", "High"]
ProjectStatus = Literal["Draft", "Analyzing", "Report Ready", "Finalized"]


class LocalizedText(BaseModel):
    zh: str
    en: str


class PlatformScores(BaseModel):
    productivity: int = Field(ge=0, le=100)
    motion: int = Field(ge=0, le=100)
    safety: int = Field(ge=0, le=100)
    simulation: int = Field(ge=0, le=100)
    openness: int = Field(ge=0, le=100)
    talent: int = Field(ge=0, le=100)
    cost: int = Field(ge=0, le=100)


class PlcEcosystem(BaseModel):
    id: str
    name: str
    vendor: str
    software: str
    region_strength: LocalizedText
    summary: LocalizedText
    strengths: list[LocalizedText]
    cautions: list[LocalizedText]
    scores: PlatformScores


class Project(BaseModel):
    id: str
    name: str
    industry: str
    goal: str
    status: ProjectStatus
    created_at: str
    updated_at: str


class ProjectIntake(BaseModel):
    project_size: Literal["Small", "Medium", "Large"]
    io_scale: int = Field(ge=0)
    motion_requirement: int = Field(ge=0, le=100)
    safety_requirement: int = Field(ge=0, le=100)
    budget_sensitivity: int = Field(ge=0, le=100)
    team_experience: str
    existing_platform: str
    candidate_platforms: list[str]
    constraints: str


class PlatformPreference(BaseModel):
    platform_id: str
    preference_weight: int = Field(ge=0, le=100)
    user_reason_note: str = ""


class ProjectAttachment(BaseModel):
    id: str
    project_id: str
    file_name: str
    file_type: Literal["Electrical List", "I/O List", "Requirements", "Architecture", "Other"]
    declared_purpose: str
    uploaded_at: str


class BenchmarkResult(BaseModel):
    platform_id: str
    technical_score: int = Field(ge=0, le=100)
    preference_score: int = Field(ge=0, le=100)
    weighted_score: int = Field(ge=0, le=100)
    risk_level: RiskLevel
    rationale: LocalizedText
    assumptions: list[LocalizedText]


class ReportSection(BaseModel):
    id: str
    title: LocalizedText
    body: LocalizedText
    assumptions: list[LocalizedText]
    last_generated_at: str


class ReportDraft(BaseModel):
    project_id: str
    sections: list[ReportSection]
    version: int
    status: Literal["Draft", "Ready"]


class ProjectWorkspace(BaseModel):
    project: Project
    intake: ProjectIntake
    preferences: list[PlatformPreference]
    attachments: list[ProjectAttachment]
    report: ReportDraft


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: LocalizedText
