from app.data import ECOSYSTEMS
from app.models import (
    BenchmarkResult,
    LocalizedText,
    PlatformPreference,
    PlcEcosystem,
    ProjectAttachmentCreate,
    ProjectCreate,
    ProjectIntake,
    ProjectWorkspace,
    ReportSectionUpdate,
)
from app import repository


def list_platform_ids() -> set[str]:
    return {platform.id for platform in ECOSYSTEMS}


def find_ecosystem(platform_id: str) -> PlcEcosystem | None:
    return next((platform for platform in ECOSYSTEMS if platform.id == platform_id), None)


def list_workspaces() -> list[ProjectWorkspace]:
    return repository.list_workspaces()


def get_workspace(project_id: str) -> ProjectWorkspace | None:
    return repository.get_workspace(project_id)


def create_workspace(payload: ProjectCreate) -> ProjectWorkspace:
    return repository.create_workspace(payload)


def validate_platform_ids(platform_ids: list[str], field_name: str) -> None:
    known_ids = list_platform_ids()
    unknown_ids = sorted({platform_id for platform_id in platform_ids if platform_id not in known_ids})
    if unknown_ids:
        known = ", ".join(sorted(known_ids))
        unknown = ", ".join(unknown_ids)
        raise ValueError(f"Unknown {field_name}: {unknown}. Known platforms: {known}.")


def update_intake(project_id: str, intake: ProjectIntake) -> ProjectWorkspace | None:
    validate_platform_ids(intake.candidate_platforms, "candidate platform")
    if intake.existing_platform:
        validate_platform_ids([intake.existing_platform], "existing platform")
    return repository.update_intake(project_id, intake)


def update_preferences(project_id: str, preferences: list[PlatformPreference]) -> ProjectWorkspace | None:
    validate_platform_ids([item.platform_id for item in preferences], "preference platform")
    return repository.update_preferences(project_id, preferences)


def add_attachment(project_id: str, payload: ProjectAttachmentCreate) -> ProjectWorkspace | None:
    return repository.add_attachment(project_id, payload)


def update_report_section(project_id: str, section_id: str, payload: ReportSectionUpdate) -> ProjectWorkspace | None:
    return repository.update_report_section(project_id, section_id, payload)


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
