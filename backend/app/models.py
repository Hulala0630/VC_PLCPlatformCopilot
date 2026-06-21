from typing import Literal

from pydantic import BaseModel, Field


Language = Literal["zh", "en"]
RiskLevel = Literal["Low", "Medium", "High"]
ProjectStatus = Literal["Draft", "Analyzing", "Report Ready", "Finalized"]
ProjectSize = Literal["Small", "Medium", "Large"]
AttachmentType = Literal["Electrical List", "I/O List", "Requirements", "Architecture", "Other"]
ConfidenceLevel = Literal["Low", "Medium", "High"]


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
    official_url: str
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
    status: ProjectStatus = "Draft"
    created_at: str
    updated_at: str


class ProjectIntake(BaseModel):
    project_size: ProjectSize = "Medium"
    io_scale: int = Field(default=0, ge=0)
    motion_requirement: int = Field(default=50, ge=0, le=100)
    safety_requirement: int = Field(default=50, ge=0, le=100)
    budget_sensitivity: int = Field(default=50, ge=0, le=100)
    team_experience: str = ""
    existing_platform: str = ""
    candidate_platforms: list[str] = Field(default_factory=list)
    constraints: str = ""


class PlatformPreference(BaseModel):
    platform_id: str
    preference_weight: int = Field(default=50, ge=0, le=100)
    user_reason_note: str = ""


class ProjectAttachment(BaseModel):
    id: str
    project_id: str
    file_name: str
    file_type: AttachmentType = "Other"
    declared_purpose: str = ""
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
    assumptions: list[LocalizedText] = Field(default_factory=list)
    last_generated_at: str


class ReportDraft(BaseModel):
    project_id: str
    sections: list[ReportSection]
    version: int = Field(default=1, ge=1)
    status: Literal["Draft", "Ready"] = "Draft"


class ProjectReadiness(BaseModel):
    score: int = Field(ge=0, le=100)
    status: ProjectStatus
    missing_required: list[LocalizedText] = Field(default_factory=list)
    recommended_missing: list[LocalizedText] = Field(default_factory=list)
    next_action: LocalizedText
    confidence_level: ConfidenceLevel
    reasons: list[LocalizedText] = Field(default_factory=list)


def default_project_readiness() -> ProjectReadiness:
    return ProjectReadiness(
        score=0,
        status="Draft",
        missing_required=[],
        recommended_missing=[],
        next_action=LocalizedText(zh="完善项目基础信息。", en="Complete basic project information."),
        confidence_level="Low",
        reasons=[],
    )


class ProjectWorkspace(BaseModel):
    project: Project
    intake: ProjectIntake
    preferences: list[PlatformPreference]
    attachments: list[ProjectAttachment]
    report: ReportDraft
    readiness: ProjectReadiness = Field(default_factory=default_project_readiness)


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: LocalizedText


class ProjectCreate(BaseModel):
    name: str
    industry: str = ""
    goal: str = ""


class ProjectAttachmentCreate(BaseModel):
    file_name: str
    file_type: AttachmentType = "Other"
    declared_purpose: str = ""


class ReportSectionUpdate(BaseModel):
    body: LocalizedText
    assumptions: list[LocalizedText] = Field(default_factory=list)


class ProjectStatusUpdate(BaseModel):
    status: ProjectStatus
