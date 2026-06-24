from pathlib import Path
import sys
import tempfile
import unittest

from fastapi.testclient import TestClient


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app import database, repository
from app.main import app
from app.models import (
    LocalizedText,
    PlatformPreference,
    Project,
    ProjectAttachment,
    ProjectCreate,
    ProjectIntake,
    ProjectStatusUpdate,
    ProjectWorkspace,
    ReportDraft,
    ReportSectionUpdate,
)
from app.services import compute_project_readiness, create_workspace, update_intake, update_project_status, update_report_section


class ProjectReadinessLifecycleTests(unittest.TestCase):
    def test_empty_project_readiness_is_draft_with_required_missing_inputs(self) -> None:
        workspace = _workspace(
            project=Project(
                id="empty-project",
                name="",
                industry="",
                goal="",
                status="Draft",
                created_at="2026-06-01",
                updated_at="2026-06-01",
            ),
            intake=ProjectIntake(),
            attachments=[],
            report_status="Draft",
        )

        readiness = compute_project_readiness(workspace)

        self.assertEqual(readiness.status, "Draft")
        self.assertEqual(readiness.confidence_level, "Low")
        self.assertLess(readiness.score, 50)
        self.assertGreaterEqual(len(readiness.missing_required), 5)
        self.assertEqual(readiness.next_action.en, "Add a project name.")

    def test_complete_intake_is_analyzing_until_report_is_ready(self) -> None:
        workspace = _workspace(
            intake=ProjectIntake(
                project_size="Large",
                io_scale=900,
                motion_requirement=70,
                safety_requirement=82,
                budget_sensitivity=55,
                team_experience="Maintenance team is experienced with Siemens and Rockwell.",
                existing_platform="siemens-tia",
                candidate_platforms=["siemens-tia", "rockwell", "codesys"],
                constraints="Two commissioning windows and limited supplier capacity.",
            ),
            attachments=[],
            report_status="Draft",
        )

        readiness = compute_project_readiness(workspace)

        self.assertEqual(readiness.status, "Analyzing")
        self.assertEqual(readiness.missing_required, [])
        self.assertEqual(readiness.confidence_level, "High")
        self.assertTrue(any(item.en == "Register at least one attachment information record." for item in readiness.recommended_missing))
        self.assertEqual(readiness.next_action.en, "Complete or update report sections to reach Report Ready.")

    def test_attachment_records_improve_readiness_but_are_declared_unparsed(self) -> None:
        workspace = _workspace(
            intake=ProjectIntake(
                project_size="Medium",
                io_scale=360,
                motion_requirement=64,
                safety_requirement=72,
                budget_sensitivity=50,
                team_experience="Controls team can maintain the candidate platforms.",
                existing_platform="rockwell",
                candidate_platforms=["rockwell", "siemens-tia"],
                constraints="Cutover must fit one planned maintenance weekend.",
            ),
            attachments=[
                ProjectAttachment(
                    id="att-asset-list",
                    project_id="attachment-project",
                    file_name="asset-list.xlsx",
                    file_type="Electrical List",
                    declared_purpose="Asset inventory; metadata only, contents are not parsed.",
                    uploaded_at="2026-06-01",
                )
            ],
            report_status="Draft",
        )

        readiness = compute_project_readiness(workspace)

        self.assertEqual(readiness.status, "Analyzing")
        self.assertFalse(any(item.en == "Register at least one attachment information record." for item in readiness.recommended_missing))
        self.assertTrue(
            any("does not read or parse attachment contents" in reason.en for reason in readiness.reasons),
            "Readiness should tell the frontend that attachments are registered but not parsed.",
        )

    def test_report_ready_and_finalized_status_updates_are_deterministic(self) -> None:
        with temporary_database_path():
            database.initialize_schema()
            workspace = create_workspace(
                ProjectCreate(
                    name="Lifecycle Validation Project",
                    industry="Discrete Manufacturing",
                    goal="Validate deterministic status transitions.",
                )
            )
            workspace = update_intake(
                workspace.project.id,
                ProjectIntake(
                    project_size="Medium",
                    io_scale=520,
                    motion_requirement=60,
                    safety_requirement=80,
                    budget_sensitivity=50,
                    team_experience="Team can support Siemens and Rockwell.",
                    existing_platform="siemens-tia",
                    candidate_platforms=["siemens-tia", "rockwell"],
                    constraints="Must preserve scheduled commissioning window.",
                ),
            )
            self.assertIsNotNone(workspace)
            self.assertEqual(workspace.readiness.status, "Analyzing")

            workspace = update_report_section(
                workspace.project.id,
                "executive-summary",
                ReportSectionUpdate(
                    body=LocalizedText(zh="报告可审阅。", en="The report is ready for review."),
                    assumptions=[LocalizedText(zh="仅基于当前输入。", en="Based on current inputs only.")],
                ),
            )
            self.assertIsNotNone(workspace)
            self.assertEqual(workspace.project.status, "Report Ready")
            self.assertEqual(workspace.readiness.status, "Report Ready")

            workspace = update_project_status(workspace.project.id, ProjectStatusUpdate(status="Finalized"))
            self.assertIsNotNone(workspace)
            self.assertEqual(workspace.project.status, "Finalized")
            self.assertEqual(workspace.readiness.status, "Finalized")
            self.assertTrue(any("explicitly marked Finalized" in item.en for item in workspace.readiness.reasons))

    def test_readiness_endpoint_returns_frontend_ready_shape(self) -> None:
        with temporary_database_path():
            with TestClient(app) as client:
                response = client.get("/api/projects")
                project_id = response.json()[0]["project"]["id"]

                response = client.get(f"/api/projects/{project_id}/readiness")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(
            set(payload),
            {
                "score",
                "status",
                "missing_required",
                "recommended_missing",
                "next_action",
                "confidence_level",
                "reasons",
            },
        )
        self.assertIsInstance(payload["reasons"], list)


def _workspace(
    *,
    project: Project | None = None,
    intake: ProjectIntake,
    attachments: list[ProjectAttachment],
    report_status: str,
) -> ProjectWorkspace:
    project = project or Project(
        id="readiness-project",
        name="Readiness Validation Project",
        industry="Manufacturing",
        goal="Validate status and readiness behavior.",
        status="Draft",
        created_at="2026-06-01",
        updated_at="2026-06-01",
    )
    report = ReportDraft(
        project_id=project.id,
        sections=[
            repository._default_report_sections(project.name, "2026-06-01")[0],
        ],
        version=1,
        status=report_status,
    )
    return ProjectWorkspace(
        project=project,
        intake=intake,
        preferences=[
            PlatformPreference(platform_id="siemens-tia", preference_weight=70),
            PlatformPreference(platform_id="rockwell", preference_weight=65),
            PlatformPreference(platform_id="codesys", preference_weight=55),
        ],
        attachments=attachments,
        report=report,
    )


class temporary_database_path:
    def __enter__(self):
        self._temp_dir = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self._previous_path = database.DATABASE_PATH
        database.DATABASE_PATH = Path(self._temp_dir.name) / "plc_copilot_test.db"
        return database.DATABASE_PATH

    def __exit__(self, exc_type, exc, tb):
        database.DATABASE_PATH = self._previous_path
        self._temp_dir.cleanup()


if __name__ == "__main__":
    unittest.main()
