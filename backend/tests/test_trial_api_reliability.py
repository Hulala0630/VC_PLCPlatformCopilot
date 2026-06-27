from pathlib import Path
import os
import sys
import tempfile
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app import database, repository
from app.intelligence.config import AISettings
from app.intelligence.dependencies import clear_ai_settings_cache
from app.main import app
from app.models import ProjectCreate


class TrialApiReliabilityTests(unittest.TestCase):
    def tearDown(self) -> None:
        clear_ai_settings_cache()

    def test_project_workflow_endpoints_do_not_500_with_missing_ai_config(self) -> None:
        with temporary_database_path(), placeholder_ai_environment(), TestClient(app) as client:
            projects_response = client.get("/api/projects")
            self.assertEqual(projects_response.status_code, 200)
            projects = projects_response.json()
            self.assertGreaterEqual(len(projects), 3)
            project_id = projects[0]["project"]["id"]

            detail_response = client.get(f"/api/projects/{project_id}")
            self.assertEqual(detail_response.status_code, 200)

            attachment_response = client.post(
                f"/api/projects/{project_id}/attachments",
                json={
                    "file_name": "trial-asset-register.xlsx",
                    "file_type": "Electrical List",
                    "declared_purpose": "Trial asset register; only file information is stored.",
                },
            )
            self.assertEqual(attachment_response.status_code, 200)
            attachment = attachment_response.json()["attachments"][-1]
            self.assertEqual(attachment["file_name"], "trial-asset-register.xlsx")
            self.assertNotIn("content", attachment)

            benchmark_response = client.post(f"/api/projects/{project_id}/benchmark")
            self.assertEqual(benchmark_response.status_code, 200)
            self.assertGreaterEqual(len(benchmark_response.json()), 1)

            report_response = client.post(
                f"/api/projects/{project_id}/report/generate",
                json={"language": "en", "audience": "technical", "use_ai": True},
            )
            self.assertEqual(report_response.status_code, 200)
            report = report_response.json()
            self.assertEqual(report["execution_status"], "ai_fallback")
            self.assertFalse(report["ai_used"])
            self.assertTrue(report["sections"])
            self.assertTrue(report["assumptions"])
            self.assertTrue(report["uncertainty"])

            section_id = report["sections"][0]["section_id"]
            rewrite_response = client.post(
                f"/api/projects/{project_id}/report/sections/{section_id}/rewrite",
                json={
                    "instruction": "Keep it concise for a trial user.",
                    "language": "en",
                    "audience": "technical",
                    "use_ai": True,
                },
            )
            self.assertEqual(rewrite_response.status_code, 200)
            rewrite = rewrite_response.json()
            self.assertEqual(rewrite["execution_status"], "ai_fallback")
            self.assertFalse(rewrite["ai_used"])
            self.assertEqual(rewrite["section_id"], section_id)
            self.assertTrue(rewrite["suggested_body"]["en"])
            self.assertTrue(rewrite["assumptions"])
            self.assertTrue(rewrite["uncertainty"])

            analyze_response = client.post(
                f"/api/projects/{project_id}/intelligence/analyze",
                json={"language": "en", "focus": "attachments", "use_ai": True},
            )
            self.assertEqual(analyze_response.status_code, 200)
            analysis = analyze_response.json()
            self.assertFalse(analysis["document_parsing_used"])
            self.assertIn("Attachment contents", analysis["answer"]["en"])
            self.assertTrue(any(source["type"] == "attachment_metadata" for source in analysis["sources"]))

    def test_sqlite_data_persists_across_repository_reinitialization(self) -> None:
        with temporary_database_path():
            repository.initialize_repository()
            created = repository.create_workspace(
                ProjectCreate(
                    name="Persistent Trial Project",
                    industry="Food Packaging",
                    goal="Confirm SQLite data survives startup initialization.",
                )
            )

            repository.initialize_repository()
            reloaded = repository.get_workspace(created.project.id)

        self.assertIsNotNone(reloaded)
        self.assertEqual(reloaded.project.name, "Persistent Trial Project")


class temporary_database_path:
    def __enter__(self):
        self._temp_dir = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self._previous_path = database.DATABASE_PATH
        database.DATABASE_PATH = Path(self._temp_dir.name) / "plc_copilot_test.db"
        return database.DATABASE_PATH

    def __exit__(self, exc_type, exc, tb):
        database.DATABASE_PATH = self._previous_path
        self._temp_dir.cleanup()


class placeholder_ai_environment:
    def __enter__(self):
        self._patch_env = patch.dict(os.environ, {"AI_PROVIDER": "placeholder"}, clear=True)
        self._patch_config = patch.dict(AISettings.model_config, {"env_file": None})
        self._patch_env.__enter__()
        self._patch_config.__enter__()
        clear_ai_settings_cache()

    def __exit__(self, exc_type, exc, tb):
        clear_ai_settings_cache()
        self._patch_config.__exit__(exc_type, exc, tb)
        self._patch_env.__exit__(exc_type, exc, tb)


if __name__ == "__main__":
    unittest.main()
