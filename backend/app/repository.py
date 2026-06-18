from __future__ import annotations

import json
from sqlite3 import Connection, Row
from uuid import uuid4

from app.data import ECOSYSTEMS, PROJECT_WORKSPACES
from app.database import get_connection, initialize_schema
from app.models import (
    LocalizedText,
    PlatformPreference,
    Project,
    ProjectAttachment,
    ProjectAttachmentCreate,
    ProjectCreate,
    ProjectIntake,
    ProjectWorkspace,
    ReportDraft,
    ReportSection,
    ReportSectionUpdate,
)
from app.services_time import now_iso_date


def initialize_repository() -> None:
    initialize_schema()
    seed_initial_workspaces_if_empty()


def _json_dump(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def _localized_dump(value: LocalizedText) -> str:
    return _json_dump(value.model_dump())


def _localized_load(value: str) -> LocalizedText:
    return LocalizedText.model_validate(json.loads(value))


def _localized_list_dump(values: list[LocalizedText]) -> str:
    return _json_dump([item.model_dump() for item in values])


def _localized_list_load(value: str | None) -> list[LocalizedText]:
    if not value:
        return []
    return [LocalizedText.model_validate(item) for item in json.loads(value)]


def _default_report_sections(project_name: str, generated_at: str) -> list[ReportSection]:
    return [
        ReportSection(
            id="executive-summary",
            title=LocalizedText(zh="执行摘要", en="Executive Summary"),
            body=LocalizedText(
                zh=f"{project_name} 当前处于本地持久化决策草稿阶段，建议先完善输入资料再发布正式推荐。",
                en=f"{project_name} is in a local persisted decision draft stage. Complete inputs before issuing a formal recommendation.",
            ),
            assumptions=[LocalizedText(zh="附件仅登记 metadata，当前版本不解析文件内容。", en="Attachments are metadata-only and are not parsed in this version.")],
            last_generated_at=generated_at,
        ),
        ReportSection(
            id="project-inputs",
            title=LocalizedText(zh="项目输入", en="Project Inputs"),
            body=LocalizedText(
                zh="报告汇总行业、目标、I/O 规模、运动与安全需求、团队经验和候选平台。",
                en="The report summarizes industry, goal, I/O scale, motion and safety needs, team experience, and candidate platforms.",
            ),
            assumptions=[LocalizedText(zh="输入由用户手动维护，并保存到本地 SQLite。", en="Inputs are maintained manually and saved to local SQLite.")],
            last_generated_at=generated_at,
        ),
        ReportSection(
            id="platform-benchmark",
            title=LocalizedText(zh="平台基准对比", en="Platform Benchmark"),
            body=LocalizedText(
                zh="平台排序由技术评分和用户倾向权重共同决定。",
                en="Platform ranking is determined by technical scores and user preference weights.",
            ),
            assumptions=[LocalizedText(zh="基础平台评分来自 mock profile。", en="Base platform scores come from mock profiles.")],
            last_generated_at=generated_at,
        ),
    ]


def seed_initial_workspaces_if_empty() -> None:
    with get_connection() as connection:
        count = connection.execute("SELECT COUNT(*) AS count FROM projects").fetchone()["count"]
        if count > 0:
            return
        for workspace in PROJECT_WORKSPACES:
            _insert_workspace(connection, workspace)


def list_workspaces() -> list[ProjectWorkspace]:
    with get_connection() as connection:
        rows = connection.execute("SELECT * FROM projects ORDER BY created_at DESC, id ASC").fetchall()
        return [_workspace_from_project_row(connection, row) for row in rows]


def get_workspace(project_id: str) -> ProjectWorkspace | None:
    with get_connection() as connection:
        row = connection.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
        if row is None:
            return None
        return _workspace_from_project_row(connection, row)


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
            sections=_default_report_sections(payload.name, today),
            version=1,
            status="Draft",
        ),
    )
    with get_connection() as connection:
        _insert_workspace(connection, workspace)
    return workspace


def delete_workspace(project_id: str) -> bool:
    with get_connection() as connection:
        if not _project_exists(connection, project_id):
            return False
        connection.execute("DELETE FROM projects WHERE id = ?", (project_id,))
        return True


def update_project_status(project_id: str, status: str) -> ProjectWorkspace | None:
    with get_connection() as connection:
        if not _project_exists(connection, project_id):
            return None
        connection.execute(
            "UPDATE projects SET status = ?, updated_at = ? WHERE id = ?",
            (status, now_iso_date(), project_id),
        )
        return _workspace_from_project_id(connection, project_id)


def update_report_status(project_id: str, status: str) -> ProjectWorkspace | None:
    with get_connection() as connection:
        if not _project_exists(connection, project_id):
            return None
        connection.execute(
            "UPDATE report_drafts SET status = ? WHERE project_id = ?",
            (status, project_id),
        )
        _touch_project(connection, project_id)
        return _workspace_from_project_id(connection, project_id)


def update_intake(project_id: str, intake: ProjectIntake) -> ProjectWorkspace | None:
    with get_connection() as connection:
        if not _project_exists(connection, project_id):
            return None
        connection.execute(
            """
            INSERT INTO project_intakes (
                project_id, project_size, io_scale, motion_requirement, safety_requirement,
                budget_sensitivity, team_experience, existing_platform, candidate_platforms, constraints
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(project_id) DO UPDATE SET
                project_size = excluded.project_size,
                io_scale = excluded.io_scale,
                motion_requirement = excluded.motion_requirement,
                safety_requirement = excluded.safety_requirement,
                budget_sensitivity = excluded.budget_sensitivity,
                team_experience = excluded.team_experience,
                existing_platform = excluded.existing_platform,
                candidate_platforms = excluded.candidate_platforms,
                constraints = excluded.constraints
            """,
            (
                project_id,
                intake.project_size,
                intake.io_scale,
                intake.motion_requirement,
                intake.safety_requirement,
                intake.budget_sensitivity,
                intake.team_experience,
                intake.existing_platform,
                _json_dump(intake.candidate_platforms),
                intake.constraints,
            ),
        )
        _touch_project(connection, project_id)
        return _workspace_from_project_id(connection, project_id)


def update_preferences(project_id: str, preferences: list[PlatformPreference]) -> ProjectWorkspace | None:
    with get_connection() as connection:
        if not _project_exists(connection, project_id):
            return None
        connection.execute("DELETE FROM platform_preferences WHERE project_id = ?", (project_id,))
        connection.executemany(
            """
            INSERT INTO platform_preferences (project_id, platform_id, preference_weight, user_reason_note)
            VALUES (?, ?, ?, ?)
            """,
            [
                (project_id, item.platform_id, item.preference_weight, item.user_reason_note)
                for item in preferences
            ],
        )
        _touch_project(connection, project_id)
        return _workspace_from_project_id(connection, project_id)


def add_attachment(project_id: str, payload: ProjectAttachmentCreate) -> ProjectWorkspace | None:
    with get_connection() as connection:
        if not _project_exists(connection, project_id):
            return None
        attachment = ProjectAttachment(
            id=f"att-{uuid4().hex[:8]}",
            project_id=project_id,
            file_name=payload.file_name,
            file_type=payload.file_type,
            declared_purpose=payload.declared_purpose,
            uploaded_at=now_iso_date(),
        )
        connection.execute(
            """
            INSERT INTO project_attachments (id, project_id, file_name, file_type, declared_purpose, uploaded_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                attachment.id,
                attachment.project_id,
                attachment.file_name,
                attachment.file_type,
                attachment.declared_purpose,
                attachment.uploaded_at,
            ),
        )
        _touch_project(connection, project_id)
        return _workspace_from_project_id(connection, project_id)


def update_report_section(project_id: str, section_id: str, payload: ReportSectionUpdate) -> ProjectWorkspace | None:
    with get_connection() as connection:
        if not _project_exists(connection, project_id):
            return None
        current = connection.execute(
            "SELECT id FROM report_sections WHERE project_id = ? AND id = ?",
            (project_id, section_id),
        ).fetchone()
        if current is None:
            return None
        connection.execute(
            """
            UPDATE report_sections
            SET body = ?, assumptions = ?, last_generated_at = ?
            WHERE project_id = ? AND id = ?
            """,
            (
                _localized_dump(payload.body),
                _localized_list_dump(payload.assumptions),
                now_iso_date(),
                project_id,
                section_id,
            ),
        )
        connection.execute(
            "UPDATE report_drafts SET version = version + 1, status = 'Ready' WHERE project_id = ?",
            (project_id,),
        )
        _touch_project(connection, project_id)
        return _workspace_from_project_id(connection, project_id)


def _insert_workspace(connection: Connection, workspace: ProjectWorkspace) -> None:
    connection.execute(
        """
        INSERT INTO projects (id, name, industry, goal, status, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            workspace.project.id,
            workspace.project.name,
            workspace.project.industry,
            workspace.project.goal,
            workspace.project.status,
            workspace.project.created_at,
            workspace.project.updated_at,
        ),
    )
    update_intake_in_connection(connection, workspace.project.id, workspace.intake)
    connection.executemany(
        """
        INSERT INTO platform_preferences (project_id, platform_id, preference_weight, user_reason_note)
        VALUES (?, ?, ?, ?)
        """,
        [
            (workspace.project.id, item.platform_id, item.preference_weight, item.user_reason_note)
            for item in workspace.preferences
        ],
    )
    connection.executemany(
        """
        INSERT INTO project_attachments (id, project_id, file_name, file_type, declared_purpose, uploaded_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        [
            (
                item.id,
                item.project_id,
                item.file_name,
                item.file_type,
                item.declared_purpose,
                item.uploaded_at,
            )
            for item in workspace.attachments
        ],
    )
    connection.execute(
        "INSERT INTO report_drafts (project_id, version, status) VALUES (?, ?, ?)",
        (workspace.report.project_id, workspace.report.version, workspace.report.status),
    )
    connection.executemany(
        """
        INSERT INTO report_sections (project_id, id, title, body, assumptions, last_generated_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        [
            (
                workspace.project.id,
                section.id,
                _localized_dump(section.title),
                _localized_dump(section.body),
                _localized_list_dump(section.assumptions),
                section.last_generated_at,
            )
            for section in workspace.report.sections
        ],
    )


def update_intake_in_connection(connection: Connection, project_id: str, intake: ProjectIntake) -> None:
    connection.execute(
        """
        INSERT INTO project_intakes (
            project_id, project_size, io_scale, motion_requirement, safety_requirement,
            budget_sensitivity, team_experience, existing_platform, candidate_platforms, constraints
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            project_id,
            intake.project_size,
            intake.io_scale,
            intake.motion_requirement,
            intake.safety_requirement,
            intake.budget_sensitivity,
            intake.team_experience,
            intake.existing_platform,
            _json_dump(intake.candidate_platforms),
            intake.constraints,
        ),
    )


def _project_exists(connection: Connection, project_id: str) -> bool:
    row = connection.execute("SELECT 1 FROM projects WHERE id = ?", (project_id,)).fetchone()
    return row is not None


def _touch_project(connection: Connection, project_id: str) -> None:
    connection.execute(
        "UPDATE projects SET updated_at = ? WHERE id = ?",
        (now_iso_date(), project_id),
    )


def _workspace_from_project_id(connection: Connection, project_id: str) -> ProjectWorkspace:
    row = connection.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
    return _workspace_from_project_row(connection, row)


def _workspace_from_project_row(connection: Connection, row: Row) -> ProjectWorkspace:
    project = Project(
        id=row["id"],
        name=row["name"],
        industry=row["industry"] or "",
        goal=row["goal"] or "",
        status=row["status"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )
    return ProjectWorkspace(
        project=project,
        intake=_load_intake(connection, project.id),
        preferences=_load_preferences(connection, project.id),
        attachments=_load_attachments(connection, project.id),
        report=_load_report(connection, project),
    )


def _load_intake(connection: Connection, project_id: str) -> ProjectIntake:
    row = connection.execute("SELECT * FROM project_intakes WHERE project_id = ?", (project_id,)).fetchone()
    if row is None:
        return ProjectIntake()
    return ProjectIntake(
        project_size=row["project_size"] or "Medium",
        io_scale=row["io_scale"] or 0,
        motion_requirement=row["motion_requirement"] if row["motion_requirement"] is not None else 50,
        safety_requirement=row["safety_requirement"] if row["safety_requirement"] is not None else 50,
        budget_sensitivity=row["budget_sensitivity"] if row["budget_sensitivity"] is not None else 50,
        team_experience=row["team_experience"] or "",
        existing_platform=row["existing_platform"] or "",
        candidate_platforms=json.loads(row["candidate_platforms"] or "[]"),
        constraints=row["constraints"] or "",
    )


def _load_preferences(connection: Connection, project_id: str) -> list[PlatformPreference]:
    rows = connection.execute(
        "SELECT * FROM platform_preferences WHERE project_id = ?",
        (project_id,),
    ).fetchall()
    preferences = [
        PlatformPreference(
            platform_id=row["platform_id"],
            preference_weight=row["preference_weight"],
            user_reason_note=row["user_reason_note"] or "",
        )
        for row in rows
    ]
    order = {platform.id: index for index, platform in enumerate(ECOSYSTEMS)}
    return sorted(preferences, key=lambda item: order.get(item.platform_id, len(order)))


def _load_attachments(connection: Connection, project_id: str) -> list[ProjectAttachment]:
    rows = connection.execute(
        "SELECT * FROM project_attachments WHERE project_id = ? ORDER BY uploaded_at ASC, id ASC",
        (project_id,),
    ).fetchall()
    return [
        ProjectAttachment(
            id=row["id"],
            project_id=row["project_id"],
            file_name=row["file_name"],
            file_type=row["file_type"] or "Other",
            declared_purpose=row["declared_purpose"] or "",
            uploaded_at=row["uploaded_at"],
        )
        for row in rows
    ]


def _load_report(connection: Connection, project: Project) -> ReportDraft:
    draft_row = connection.execute(
        "SELECT * FROM report_drafts WHERE project_id = ?",
        (project.id,),
    ).fetchone()
    if draft_row is None:
        sections = _default_report_sections(project.name, project.updated_at)
        return ReportDraft(project_id=project.id, sections=sections, version=1, status="Draft")

    section_rows = connection.execute(
        "SELECT * FROM report_sections WHERE project_id = ? ORDER BY rowid ASC",
        (project.id,),
    ).fetchall()
    sections = [
        ReportSection(
            id=row["id"],
            title=_localized_load(row["title"]),
            body=_localized_load(row["body"]),
            assumptions=_localized_list_load(row["assumptions"]),
            last_generated_at=row["last_generated_at"],
        )
        for row in section_rows
    ]
    return ReportDraft(
        project_id=project.id,
        sections=sections,
        version=draft_row["version"],
        status=draft_row["status"],
    )
