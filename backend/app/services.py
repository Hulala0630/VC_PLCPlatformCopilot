from app import repository
from app.data import ECOSYSTEMS
from app.models import (
    BenchmarkResult,
    LocalizedText,
    PlatformPreference,
    PlcEcosystem,
    ProjectAttachmentCreate,
    ProjectCreate,
    ProjectIntake,
    ProjectReadiness,
    ProjectStatus,
    ProjectStatusUpdate,
    ProjectWorkspace,
    ReportSectionUpdate,
)


def list_platform_ids() -> set[str]:
    return {platform.id for platform in ECOSYSTEMS}


def find_ecosystem(platform_id: str) -> PlcEcosystem | None:
    return next((platform for platform in ECOSYSTEMS if platform.id == platform_id), None)


def list_workspaces() -> list[ProjectWorkspace]:
    return [sync_project_status(workspace.project.id) for workspace in repository.list_workspaces()]


def get_workspace(project_id: str) -> ProjectWorkspace | None:
    workspace = repository.get_workspace(project_id)
    if workspace is None:
        return None
    return sync_project_status(project_id)


def create_workspace(payload: ProjectCreate) -> ProjectWorkspace:
    workspace = repository.create_workspace(payload)
    return sync_project_status(workspace.project.id)


def delete_workspace(project_id: str) -> bool:
    return repository.delete_workspace(project_id)


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
    workspace = repository.update_intake(project_id, intake)
    if workspace is None:
        return None
    return sync_project_status(project_id)


def update_preferences(project_id: str, preferences: list[PlatformPreference]) -> ProjectWorkspace | None:
    validate_platform_ids([item.platform_id for item in preferences], "preference platform")
    workspace = repository.update_preferences(project_id, preferences)
    if workspace is None:
        return None
    return sync_project_status(project_id)


def add_attachment(project_id: str, payload: ProjectAttachmentCreate) -> ProjectWorkspace | None:
    workspace = repository.add_attachment(project_id, payload)
    if workspace is None:
        return None
    return sync_project_status(project_id)


def update_report_section(project_id: str, section_id: str, payload: ReportSectionUpdate) -> ProjectWorkspace | None:
    workspace = repository.update_report_section(project_id, section_id, payload)
    if workspace is None:
        return None
    return sync_project_status(project_id)


def update_project_status(project_id: str, payload: ProjectStatusUpdate) -> ProjectWorkspace | None:
    if payload.status == "Finalized":
        return _workspace_with_readiness(repository.update_project_status(project_id, "Finalized"))

    if payload.status == "Analyzing":
        workspace = repository.update_project_status(project_id, "Analyzing")
        if workspace is None:
            return None
        repository.update_report_status(project_id, "Draft")
        return sync_project_status(project_id, allow_auto_status=True)

    raise ValueError("Only explicit Finalized status and reopening to Analyzing are supported.")


def get_project_readiness(project_id: str) -> ProjectReadiness | None:
    workspace = get_workspace(project_id)
    if workspace is None:
        return None
    return workspace.readiness


def sync_project_status(project_id: str, allow_auto_status: bool = True) -> ProjectWorkspace:
    workspace = repository.get_workspace(project_id)
    if workspace is None:
        raise ValueError(f"Project not found: {project_id}")

    readiness = compute_project_readiness(workspace)
    derived_status = derive_project_status(workspace, readiness)

    if workspace.project.status == "Finalized":
        readiness = readiness.model_copy(update={"status": "Finalized"})
        return workspace.model_copy(update={"readiness": readiness})

    if allow_auto_status and workspace.project.status != derived_status:
        workspace = repository.update_project_status(project_id, derived_status)
        if workspace is None:
            raise ValueError(f"Project not found: {project_id}")
        readiness = readiness.model_copy(update={"status": derived_status})

    return workspace.model_copy(update={"readiness": readiness})


def compute_project_readiness(workspace: ProjectWorkspace) -> ProjectReadiness:
    candidate_count = len(workspace.intake.candidate_platforms)
    candidate_ids = set(workspace.intake.candidate_platforms)
    preference_ids = {item.platform_id for item in workspace.preferences}
    report_sections_exist = len(workspace.report.sections) > 0

    required_checks = [
        (bool(workspace.project.name.strip()), LocalizedText(zh="填写项目名称。", en="Add a project name.")),
        (bool(workspace.project.industry.strip()), LocalizedText(zh="填写项目行业。", en="Add the project industry.")),
        (bool(workspace.project.goal.strip()), LocalizedText(zh="填写项目目标。", en="Add the project goal.")),
        (workspace.intake.io_scale > 0, LocalizedText(zh="填写大于 0 的 I/O 规模。", en="Set I/O scale greater than 0.")),
        (candidate_count >= 2, LocalizedText(zh="至少选择 2 个候选平台。", en="Select at least two candidate platforms.")),
    ]
    recommended_checks = [
        (bool(workspace.intake.team_experience.strip()), LocalizedText(zh="补充团队经验。", en="Add team experience.")),
        (bool(workspace.intake.constraints.strip()), LocalizedText(zh="补充项目约束。", en="Add project constraints.")),
        (bool(workspace.intake.existing_platform.strip()), LocalizedText(zh="补充现有平台。", en="Add the existing platform.")),
        (len(workspace.attachments) > 0, LocalizedText(zh="登记至少一个附件记录。", en="Register at least one attachment record.")),
        (
            candidate_count > 0 and candidate_ids.issubset(preference_ids),
            LocalizedText(zh="为所有候选平台设置偏好权重。", en="Set preference weights for all candidate platforms."),
        ),
        (report_sections_exist, LocalizedText(zh="准备报告分区。", en="Prepare report sections.")),
    ]

    passed_required = sum(1 for passed, _ in required_checks if passed)
    passed_recommended = sum(1 for passed, _ in recommended_checks if passed)
    score = round((passed_required / len(required_checks)) * 70 + (passed_recommended / len(recommended_checks)) * 30)
    score = max(0, min(100, score))

    missing_required = [message for passed, message in required_checks if not passed]
    recommended_missing = [message for passed, message in recommended_checks if not passed]
    confidence_level = "High" if score >= 75 else "Medium" if score >= 50 else "Low"

    reasons = [
        LocalizedText(
            zh=f"必填项完成 {passed_required}/{len(required_checks)}，建议项完成 {passed_recommended}/{len(recommended_checks)}。",
            en=f"Required checks passed {passed_required}/{len(required_checks)}; recommended checks passed {passed_recommended}/{len(recommended_checks)}.",
        ),
        LocalizedText(
            zh=f"候选平台数量为 {candidate_count}。",
            en=f"Candidate platform count is {candidate_count}.",
        ),
    ]
    if workspace.project.status == "Finalized":
        reasons.append(LocalizedText(zh="项目已由用户显式标记为 Finalized。", en="The project was explicitly marked Finalized by the user."))

    next_action = _next_action(missing_required, recommended_missing, workspace)
    status = derive_project_status(workspace, None, score=score, missing_required=missing_required)

    return ProjectReadiness(
        score=score,
        status=status,
        missing_required=missing_required,
        recommended_missing=recommended_missing,
        next_action=next_action,
        confidence_level=confidence_level,
        reasons=reasons,
    )


def derive_project_status(
    workspace: ProjectWorkspace,
    readiness: ProjectReadiness | None,
    *,
    score: int | None = None,
    missing_required: list[LocalizedText] | None = None,
) -> ProjectStatus:
    if workspace.project.status == "Finalized":
        return "Finalized"

    readiness_score = readiness.score if readiness is not None else score or 0
    missing = readiness.missing_required if readiness is not None else missing_required or []
    missing_en = {item.en for item in missing}
    candidate_count = len(workspace.intake.candidate_platforms)
    goal_or_industry_missing = "Add the project goal." in missing_en or "Add the project industry." in missing_en

    if readiness_score < 50 or candidate_count < 2 or goal_or_industry_missing:
        return "Draft"

    report_sections_exist = len(workspace.report.sections) > 0
    has_report_body = any(section.body.zh.strip() or section.body.en.strip() for section in workspace.report.sections)
    benchmark_ready = _benchmark_can_be_generated(workspace)

    if (
        readiness_score >= 70
        and candidate_count >= 2
        and workspace.report.status == "Ready"
        and report_sections_exist
        and has_report_body
        and benchmark_ready
    ):
        return "Report Ready"

    return "Analyzing"


def _next_action(
    missing_required: list[LocalizedText],
    recommended_missing: list[LocalizedText],
    workspace: ProjectWorkspace,
) -> LocalizedText:
    if missing_required:
        return missing_required[0]
    if workspace.report.status != "Ready":
        return LocalizedText(zh="完善或更新报告分区以进入 Report Ready。", en="Complete or update report sections to reach Report Ready.")
    if recommended_missing:
        return recommended_missing[0]
    return LocalizedText(zh="可以运行 benchmark 并复核报告结论。", en="Run the benchmark and review report conclusions.")


def _benchmark_can_be_generated(workspace: ProjectWorkspace) -> bool:
    try:
        create_benchmark(workspace)
    except ValueError:
        return False
    return True


def _workspace_with_readiness(workspace: ProjectWorkspace | None) -> ProjectWorkspace | None:
    if workspace is None:
        return None
    readiness = compute_project_readiness(workspace)
    if workspace.project.status == "Finalized":
        readiness = readiness.model_copy(update={"status": "Finalized"})
    return workspace.model_copy(update={"readiness": readiness})


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
