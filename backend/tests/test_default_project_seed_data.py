from pathlib import Path
import sys
import tempfile
import unittest


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app import database, repository
from app.data import DEFAULT_REPORT_SECTION_IDS, ECOSYSTEMS, PROJECT_WORKSPACES
from app.models import ProjectCreate
from app.services import create_benchmark


class DefaultProjectSeedDataTests(unittest.TestCase):
    def test_default_projects_are_complete_business_scenarios(self) -> None:
        expected_ids = {
            "ev-line-standardization",
            "high-speed-packaging",
            "legacy-line-siemens-rockwell-migration",
        }
        visible_forbidden_words = ("demo", "test", "mock", "trial")
        platform_ids = {platform.id for platform in ECOSYSTEMS}

        self.assertEqual({workspace.project.id for workspace in PROJECT_WORKSPACES}, expected_ids)
        self.assertGreaterEqual(len(PROJECT_WORKSPACES), 3)

        for workspace in PROJECT_WORKSPACES:
            with self.subTest(project=workspace.project.id):
                visible_text = " ".join(
                    [
                        workspace.project.name,
                        workspace.project.industry,
                        workspace.project.goal,
                    ]
                ).lower()
                self.assertFalse(any(word in visible_text for word in visible_forbidden_words))
                self.assertTrue(workspace.project.name.strip())
                self.assertTrue(workspace.project.industry.strip())
                self.assertTrue(workspace.project.goal.strip())
                self.assertTrue(workspace.project.created_at)
                self.assertTrue(workspace.project.updated_at)
                self.assertIn(workspace.project.status, {"Draft", "Analyzing", "Report Ready", "Finalized"})

                self.assertGreater(workspace.intake.io_scale, 0)
                self.assertGreaterEqual(len(workspace.intake.candidate_platforms), 2)
                self.assertTrue(set(workspace.intake.candidate_platforms).issubset(platform_ids))
                self.assertTrue(workspace.intake.constraints.strip())
                self.assertTrue(workspace.intake.team_experience.strip())
                self.assertTrue(workspace.intake.existing_platform.strip())

                preferences = {item.platform_id: item for item in workspace.preferences}
                self.assertEqual(set(preferences), platform_ids)
                for preference in preferences.values():
                    self.assertTrue(preference.user_reason_note.strip())

                self.assertGreaterEqual(len(workspace.attachments), 1)
                for attachment in workspace.attachments:
                    self.assertTrue(attachment.file_name.strip())
                    self.assertTrue(attachment.file_type.strip())
                    self.assertTrue(attachment.declared_purpose.strip())
                    self.assertTrue(attachment.uploaded_at.strip())

                self.assertEqual([section.id for section in workspace.report.sections], DEFAULT_REPORT_SECTION_IDS)
                for section in workspace.report.sections:
                    self.assertTrue(section.body.zh.strip())
                    self.assertTrue(section.body.en.strip())
                    self.assertTrue(section.assumptions)

    def test_default_projects_generate_deterministic_benchmark_results(self) -> None:
        for workspace in PROJECT_WORKSPACES:
            with self.subTest(project=workspace.project.id):
                results = create_benchmark(workspace)
                self.assertEqual(
                    [result.platform_id for result in results],
                    [
                        result.platform_id
                        for result in sorted(results, key=lambda item: item.weighted_score, reverse=True)
                    ],
                )
                self.assertEqual(
                    {result.platform_id for result in results},
                    set(workspace.intake.candidate_platforms),
                )
                for result in results:
                    self.assertEqual(
                        result.weighted_score,
                        round(result.technical_score * 0.72 + result.preference_score * 0.28),
                    )

    def test_empty_database_is_seeded_with_default_projects(self) -> None:
        with temporary_database_path():
            repository.initialize_repository()

            seeded = repository.list_workspaces()

        self.assertEqual(len(seeded), len(PROJECT_WORKSPACES))
        self.assertEqual(
            {workspace.project.id for workspace in seeded},
            {workspace.project.id for workspace in PROJECT_WORKSPACES},
        )

    def test_existing_user_projects_are_preserved_when_missing_defaults_are_seeded(self) -> None:
        with temporary_database_path():
            database.initialize_schema()
            user_workspace = repository.create_workspace(
                ProjectCreate(
                    name="User Created Migration Project",
                    industry="Automotive",
                    goal="Keep this project untouched by default seed data.",
                )
            )

            repository.seed_initial_workspaces_if_empty()
            workspaces = repository.list_workspaces()

        by_id = {workspace.project.id: workspace for workspace in workspaces}
        self.assertEqual(len(workspaces), len(PROJECT_WORKSPACES) + 1)
        self.assertIn(user_workspace.project.id, by_id)
        self.assertEqual(by_id[user_workspace.project.id].project.name, "User Created Migration Project")
        self.assertTrue({workspace.project.id for workspace in PROJECT_WORKSPACES}.issubset(by_id))

    def test_existing_default_project_is_not_overwritten_by_seed(self) -> None:
        with temporary_database_path():
            database.initialize_schema()
            original = PROJECT_WORKSPACES[0]
            customized = original.model_copy(
                deep=True,
                update={
                    "project": original.project.model_copy(
                        update={
                            "name": "Customer Customized Default Project",
                            "goal": "Keep custom changes after restart.",
                        }
                    )
                },
            )
            with database.get_connection() as connection:
                repository._insert_workspace(connection, customized)

            repository.seed_initial_workspaces_if_empty()
            workspaces = repository.list_workspaces()

        by_id = {workspace.project.id: workspace for workspace in workspaces}
        self.assertEqual(len(workspaces), len(PROJECT_WORKSPACES))
        self.assertEqual(by_id[original.project.id].project.name, "Customer Customized Default Project")
        self.assertEqual(by_id[original.project.id].project.goal, "Keep custom changes after restart.")


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
