from datetime import UTC, datetime
from uuid import uuid4

from app.data import ECOSYSTEMS, PROJECT_WORKSPACES
from app.models import (
    BenchmarkResult,
    LocalizedText,
    PlatformPreference,
    PlcEcosystem,
    Project,
    ProjectAttachment,
    ProjectAttachmentCreate,
    ProjectCreate,
    ProjectIntake,
    ProjectWorkspace,
    ReportDraft,
    ReportSectionUpdate,
)


def now_iso_date() -> str:
    return datetime.now(UTC).date().isoformat()


def list_platform_ids() -> set[str]:
    return {platform.id for platform in ECOSYSTEMS}


def find_ecosystem(platform_id: str) -> PlcEcosystem | None:
    return next((platform for platform in ECOSYSTEMS if platform.id == platform_id), None)


def get_workspace(project_id: str) -> ProjectWorkspace | None:
    return next((workspace for workspace in PROJECT_WORKSPACES if workspace.project.id == project_id), None)


def create_workspace(payload: ProjectCreate) -> ProjectWorkspace:
    today = now_iso_date()
    project_id = f"project-{uuid4().hex[:8]}"
    workspace = ProjectWorkspace(
        project=Project(
            id=project_id,
            name=payload.name,
            industry=payload.industry,
            goal=payload.goal,
            status="Draft",
            created_at=today,
            updated_at=today,
        ),
        intake=ProjectIntake(candidate_platforms=[]),
        preferences=[PlatformPreference(platform_id=platform.id, preference_weight=50) for platform in ECOSYSTEMS],
        attachments=[],
        report=ReportDraft(
            project_id=project_id,
            sections=[],
            version=1,
            status="Draft",
        ),
    )
    PROJECT_WORKSPACES.append(workspace)
    return workspace


def validate_platform_ids(platform_ids: list[str], field_name: str) -> None:
    known_ids = list_platform_ids()
    unknown_ids = sorted({platform_id for platform_id in platform_ids if platform_id not in known_ids})
    if unknown_ids:
        known = ", ".join(sorted(known_ids))
        unknown = ", ".join(unknown_ids)
        raise ValueError(f"Unknown {field_name}: {unknown}. Known platforms: {known}.")


def update_intake(workspace: ProjectWorkspace, intake: ProjectIntake) -> ProjectWorkspace:
    validate_platform_ids(intake.candidate_platforms, "candidate platform")
    if intake.existing_platform:
        validate_platform_ids([intake.existing_platform], "existing platform")
    workspace.intake = intake
    workspace.project.updated_at = now_iso_date()
    return workspace


def update_preferences(workspace: ProjectWorkspace, preferences: list[PlatformPreference]) -> ProjectWorkspace:
    validate_platform_ids([item.platform_id for item in preferences], "preference platform")
    workspace.preferences = preferences
    workspace.project.updated_at = now_iso_date()
    return workspace


def add_attachment(workspace: ProjectWorkspace, payload: ProjectAttachmentCreate) -> ProjectWorkspace:
    attachment = ProjectAttachment(
        id=f"att-{uuid4().hex[:8]}",
        project_id=workspace.project.id,
        file_name=payload.file_name,
        file_type=payload.file_type,
        declared_purpose=payload.declared_purpose,
        uploaded_at=now_iso_date(),
    )
    workspace.attachments.append(attachment)
    workspace.project.updated_at = now_iso_date()
    return workspace


def update_report_section(workspace: ProjectWorkspace, section_id: str, payload: ReportSectionUpdate) -> ProjectWorkspace | None:
    for section in workspace.report.sections:
        if section.id == section_id:
            section.body = payload.body
            section.assumptions = payload.assumptions
            section.last_generated_at = now_iso_date()
            workspace.report.version += 1
            workspace.project.updated_at = now_iso_date()
            return workspace
    return None


def _average_score(values: list[int]) -> int:
    return round(sum(values) / len(values))


def create_benchmark(workspace: ProjectWorkspace) -> list[BenchmarkResult]:
    validate_platform_ids(workspace.intake.candidate_platforms, "candidate platform")
    validate_platform_ids([item.platform_id for item in workspace.preferences], "preference platform")

    preference_by_platform = {
        item.platform_id: item.preference_weight
        for item in workspace.preferences
    }
    results: list[BenchmarkResult] = []

    for platform_id in workspace.intake.candidate_platforms:
        platform = find_ecosystem(platform_id)
        if platform is None:
            continue

        scores = platform.scores.model_dump()
        technical_score = _average_score(list(scores.values()))
        preference_score = preference_by_platform.get(platform.id, 50)
        weighted_score = round(technical_score * 0.72 + preference_score * 0.28)
        risk_level = "Low" if weighted_score >= 78 else "Medium" if weighted_score >= 65 else "High"

        results.append(
            BenchmarkResult(
                platform_id=platform.id,
                technical_score=technical_score,
                preference_score=preference_score,
                weighted_score=weighted_score,
                risk_level=risk_level,
                rationale=LocalizedText(
                    zh=f"{platform.name} 的技术均分为 {technical_score}，用户倾向分为 {preference_score}，按 72/28 权重得到 {weighted_score}。",
                    en=f"{platform.name} has technical score {technical_score}, preference score {preference_score}, and weighted score {weighted_score} using the 72/28 formula.",
                ),
                assumptions=[
                    LocalizedText(zh="技术评分来自平台 mock scores 的简单平均值。", en="Technical score is the average of mock platform scores."),
                    LocalizedText(zh="用户倾向评分来自 PlatformPreference；缺省按 50 处理。", en="Preference score comes from PlatformPreference; missing values default to 50."),
                    LocalizedText(zh="本阶段不调用 AI、不解析文件、不使用随机数。", en="This stage does not call AI, parse files, or use randomness."),
                ],
            )
        )

    return sorted(results, key=lambda item: item.weighted_score, reverse=True)
