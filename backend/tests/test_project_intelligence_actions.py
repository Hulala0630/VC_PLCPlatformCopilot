from pathlib import Path
import sys
import unittest
from unittest.mock import patch


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.intelligence import service
from app.intelligence.models import (
    BenchmarkExplanationRequest,
    ProjectAnalysisRequest,
    ReportGenerationRequest,
    ReportSectionRewriteRequest,
)
from app.intelligence.openai_provider import ProviderCallError
from app.intelligence.provider import DeterministicPlaceholderProvider
from app.intelligence.provider_factory import ProviderSelection, build_provider_selection
from app.services import create_benchmark
from tests.test_openai_provider import (
    FAKE_KEY,
    MODEL_IDS,
    FakeClient,
    FakeResponses,
    intelligence_output,
    openai_settings,
    report_output,
    rewrite_output,
    workspace_fixture,
)


class FailingWorkflowProvider:
    def analyze_project(self, request, workspace, benchmark):
        raise ProviderCallError("timeout", "balanced")

    def explain_benchmark(self, request, workspace, benchmark):
        raise ProviderCallError("timeout", "balanced")

    def generate_report(self, request, workspace, benchmark):
        raise ProviderCallError("timeout", "quality")

    def rewrite_report_section(self, request, workspace, section, benchmark):
        raise ProviderCallError("timeout", "quality")


def workflow_selection(primary) -> ProviderSelection:
    placeholder = DeterministicPlaceholderProvider()
    return ProviderSelection(
        primary=primary,
        placeholder=placeholder,
        fallback_enabled=True,
        openai_active=True,
        configuration_valid=True,
    )


def workflow_calls(workspace, *, use_ai: bool):
    project_id = workspace.project.id
    section_id = workspace.report.sections[0].id
    return [
        lambda: service.analyze_project(
            project_id,
            ProjectAnalysisRequest(language="en", focus="attachments", use_ai=use_ai),
        ),
        lambda: service.explain_benchmark(
            project_id,
            BenchmarkExplanationRequest(language="en", use_ai=use_ai),
        ),
        lambda: service.generate_report(
            project_id,
            ReportGenerationRequest(language="en", audience="technical", use_ai=use_ai),
        ),
        lambda: service.rewrite_report_section(
            project_id,
            section_id,
            ReportSectionRewriteRequest(
                instruction="Make the recommendation concise",
                language="en",
                audience="technical",
                use_ai=use_ai,
            ),
        ),
    ]


class ProjectIntelligenceActionTests(unittest.TestCase):
    def test_ai_off_bypasses_factory_and_preserves_project_and_benchmark(self) -> None:
        workspace = workspace_fixture()
        project_before = workspace.model_dump()
        benchmark_before = [item.model_dump() for item in create_benchmark(workspace)]

        with (
            patch("app.intelligence.service.get_workspace", return_value=workspace),
            patch(
                "app.intelligence.service.get_provider_selection",
                side_effect=AssertionError("AI provider factory must not be invoked"),
            ) as factory,
        ):
            results = [call() for call in workflow_calls(workspace, use_ai=False)]

        factory.assert_not_called()
        for result in results:
            self.assertEqual(result.mode, "deterministic_placeholder")
            self.assertEqual(result.provider, "placeholder")
            self.assertFalse(result.ai_used)
            self.assertIsNone(result.fallback_reason)
        attachment_analysis = results[0]
        self.assertIn("No file content was read or parsed", attachment_analysis.answer.en)
        self.assertTrue(attachment_analysis.follow_up_questions)
        self.assertEqual(results[3].section_id, workspace.report.sections[0].id)
        self.assertEqual(workspace.model_dump(), project_before)
        self.assertEqual(
            [item.model_dump() for item in create_benchmark(workspace)],
            benchmark_before,
        )

    def test_ai_on_uses_structured_outputs_without_persisting(self) -> None:
        workspace = workspace_fixture()
        project_before = workspace.model_dump()
        benchmark_before = [item.model_dump() for item in create_benchmark(workspace)]
        responses = FakeResponses(
            parse_effects=[
                intelligence_output("attachment analysis"),
                intelligence_output("benchmark explanation"),
                report_output(workspace),
                rewrite_output(workspace.report.sections[0]),
            ]
        )
        selection = build_provider_selection(
            openai_settings(),
            client=FakeClient(responses),
            sleep_fn=lambda _: None,
        )

        with (
            patch("app.intelligence.service.get_workspace", return_value=workspace),
            patch("app.intelligence.service.get_provider_selection", return_value=selection),
        ):
            results = [call() for call in workflow_calls(workspace, use_ai=True)]

        for result in results:
            self.assertEqual(result.mode, "openai")
            self.assertEqual(result.provider, "openai")
            self.assertTrue(result.ai_used)
            serialized = result.model_dump_json()
            self.assertNotIn(FAKE_KEY, serialized)
            for model_id in MODEL_IDS.values():
                self.assertNotIn(model_id, serialized)
        attachment_prompt = responses.parse_calls[0]["input"]
        self.assertIn('"content_parsed":false', attachment_prompt)
        self.assertNotIn("file_content", attachment_prompt)
        self.assertEqual(
            [item.section_id for item in results[2].sections],
            [item.id for item in workspace.report.sections],
        )
        self.assertEqual(results[3].section_id, workspace.report.sections[0].id)
        self.assertEqual(workspace.model_dump(), project_before)
        self.assertEqual(
            [item.model_dump() for item in create_benchmark(workspace)],
            benchmark_before,
        )

    def test_provider_failure_falls_back_explicitly_for_all_workflows(self) -> None:
        workspace = workspace_fixture()
        project_before = workspace.model_dump()
        selection = workflow_selection(FailingWorkflowProvider())

        with (
            patch("app.intelligence.service.get_workspace", return_value=workspace),
            patch("app.intelligence.service.get_provider_selection", return_value=selection),
        ):
            results = [call() for call in workflow_calls(workspace, use_ai=True)]

        for result in results:
            self.assertEqual(result.mode, "deterministic_fallback")
            self.assertEqual(result.provider, "placeholder")
            self.assertFalse(result.ai_used)
            self.assertEqual(result.fallback_reason, "timeout")
        self.assertEqual(workspace.model_dump(), project_before)

    def test_rewrite_rejects_a_different_section_id_and_falls_back(self) -> None:
        workspace = workspace_fixture()
        invalid = rewrite_output(workspace.report.sections[0])
        invalid["section_id"] = "another-section"
        selection = build_provider_selection(
            openai_settings(),
            client=FakeClient(FakeResponses(parse_effects=[invalid])),
            sleep_fn=lambda _: None,
        )

        with (
            patch("app.intelligence.service.get_workspace", return_value=workspace),
            patch("app.intelligence.service.get_provider_selection", return_value=selection),
        ):
            result = service.rewrite_report_section(
                workspace.project.id,
                workspace.report.sections[0].id,
                ReportSectionRewriteRequest(
                    instruction="Shorten",
                    language="en",
                    audience="technical",
                ),
            )

        self.assertEqual(result.mode, "deterministic_fallback")
        self.assertEqual(result.fallback_reason, "invalid_response")
        self.assertEqual(result.section_id, workspace.report.sections[0].id)


if __name__ == "__main__":
    unittest.main()
