from pathlib import Path
import sys
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.intelligence import service
from app.intelligence.models import BenchmarkAnalysisRequest, ProjectSummaryRequest
from app.intelligence.openai_provider import ProviderCallError
from app.intelligence.provider import DeterministicPlaceholderProvider
from app.intelligence.provider_factory import ProviderSelection, build_provider_selection
from app.main import app
from app.services import create_benchmark
from tests.test_openai_provider import (
    FAKE_KEY,
    MODEL_IDS,
    FakeClient,
    FakeResponses,
    openai_settings,
    workspace_fixture,
)


def benchmark_analysis_output(platform_id: str) -> dict:
    return {
        "recommended_platform": platform_id,
        "ranking_rationale": {"zh": "AI 排序理由", "en": "AI ranking rationale"},
        "technical_fit_analysis": {"zh": "AI 技术适配", "en": "AI technical fit"},
        "preference_impact": {"zh": "AI 偏好影响", "en": "AI preference impact"},
        "risk_assessment": {"zh": "AI 风险评估", "en": "AI risk assessment"},
        "assumptions": [{"zh": "AI 假设", "en": "AI assumption"}],
        "uncertainty": [{"zh": "AI 不确定性", "en": "AI uncertainty"}],
        "next_actions": [{"zh": "AI 下一步", "en": "AI next action"}],
    }


def project_summary_output() -> dict:
    return {
        "summary": {"zh": "AI 项目总结", "en": "AI project summary"},
        "recommended_focus": [{"zh": "AI 关注重点", "en": "AI focus"}],
        "assumptions": [{"zh": "AI 总结假设", "en": "AI summary assumption"}],
        "uncertainty": [{"zh": "AI 总结不确定性", "en": "AI summary uncertainty"}],
        "next_actions": [{"zh": "AI 总结下一步", "en": "AI summary next action"}],
    }


class FailingBenchmarkSummaryProvider:
    def analyze_benchmark(self, request, workspace, benchmark):
        raise ProviderCallError("timeout", "balanced")

    def summarize_project(self, request, workspace, benchmark):
        raise ProviderCallError("timeout", "balanced")


def workflow_selection(primary) -> ProviderSelection:
    return ProviderSelection(
        primary=primary,
        placeholder=DeterministicPlaceholderProvider(),
        fallback_enabled=True,
        openai_active=True,
        configuration_valid=True,
    )


class BenchmarkSummaryStreamingTests(unittest.TestCase):
    def test_use_ai_false_returns_deterministic_benchmark_analysis_and_summary(self) -> None:
        workspace = workspace_fixture()
        benchmark_before = [item.model_dump() for item in create_benchmark(workspace)]

        with (
            patch("app.intelligence.service.get_workspace", return_value=workspace),
            patch(
                "app.intelligence.service.get_provider_selection",
                side_effect=AssertionError("Provider factory must not be called when use_ai is false"),
            ),
        ):
            analysis = service.analyze_benchmark(
                workspace.project.id,
                BenchmarkAnalysisRequest(language="en", use_ai=False),
            )
            summary = service.summarize_project(
                workspace.project.id,
                ProjectSummaryRequest(language="en", use_ai=False),
            )

        self.assertEqual(analysis.mode, "deterministic_placeholder")
        self.assertEqual(summary.mode, "deterministic_placeholder")
        self.assertFalse(analysis.ai_used)
        self.assertFalse(summary.ai_used)
        self.assertEqual(analysis.baseline, benchmark_before)
        self.assertIn("attachment contents are not read or parsed", summary.summary.en.lower())
        self.assertEqual([item.model_dump() for item in create_benchmark(workspace)], benchmark_before)

    def test_use_ai_true_success_returns_ai_analysis_without_changing_baseline(self) -> None:
        workspace = workspace_fixture()
        baseline = [item.model_dump() for item in create_benchmark(workspace)]
        lead = baseline[0]["platform_id"]
        responses = FakeResponses(
            parse_effects=[
                benchmark_analysis_output(lead),
                project_summary_output(),
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
            analysis = service.analyze_benchmark(workspace.project.id, BenchmarkAnalysisRequest(language="en"))
            summary = service.summarize_project(workspace.project.id, ProjectSummaryRequest(language="en"))

        self.assertEqual(analysis.mode, "openai")
        self.assertEqual(summary.mode, "openai")
        self.assertTrue(analysis.ai_used)
        self.assertTrue(summary.ai_used)
        self.assertEqual(analysis.recommended_platform, lead)
        self.assertEqual(analysis.baseline, baseline)
        prompt = responses.parse_calls[0]["input"]
        self.assertIn('"content_parsed":false', prompt)
        self.assertNotIn("file_content", prompt)
        serialized = analysis.model_dump_json() + summary.model_dump_json()
        self.assertNotIn(FAKE_KEY, serialized)
        for model_id in MODEL_IDS.values():
            self.assertNotIn(model_id, serialized)

    def test_ai_failure_returns_deterministic_fallback_with_business_value(self) -> None:
        workspace = workspace_fixture()
        selection = workflow_selection(FailingBenchmarkSummaryProvider())

        with (
            patch("app.intelligence.service.get_workspace", return_value=workspace),
            patch("app.intelligence.service.get_provider_selection", return_value=selection),
        ):
            analysis = service.analyze_benchmark(workspace.project.id, BenchmarkAnalysisRequest(language="en"))
            summary = service.summarize_project(workspace.project.id, ProjectSummaryRequest(language="en"))

        self.assertEqual(analysis.mode, "deterministic_fallback")
        self.assertEqual(summary.mode, "deterministic_fallback")
        self.assertEqual(analysis.execution_status, "ai_fallback")
        self.assertEqual(summary.execution_status, "ai_fallback")
        self.assertEqual(analysis.fallback_reason, "timeout")
        self.assertIn(analysis.recommended_platform, workspace.intake.candidate_platforms)
        self.assertTrue(summary.summary.en)
        combined_analysis = " ".join(
            [
                analysis.ranking_rationale.en,
                analysis.technical_fit_analysis.en,
                analysis.preference_impact.en,
                analysis.risk_assessment.en,
                " ".join(item.en for item in analysis.next_actions),
            ]
        ).lower()
        for term in (
            "recommendation",
            "why this platform",
            "alternative platform",
            "key risks",
            "preference impact",
            "missing confirmations",
            "decision next step",
        ):
            self.assertIn(term, combined_analysis)
        for user_text in [
            analysis.ranking_rationale.en,
            analysis.technical_fit_analysis.en,
            analysis.preference_impact.en,
            analysis.risk_assessment.en,
            summary.summary.en,
        ]:
            self.assertNotIn("provider", user_text.lower())
            self.assertNotIn("fallback", user_text.lower())
            self.assertNotIn("metadata", user_text.lower())
            self.assertNotIn("placeholder", user_text.lower())
            self.assertNotIn("deterministic", user_text.lower())
            self.assertNotIn("model id", user_text.lower())
            self.assertNotIn("api key", user_text.lower())

    def test_streaming_endpoints_emit_chunk_and_done_events(self) -> None:
        workspace = workspace_fixture()
        with (
            patch("app.intelligence.service.get_workspace", return_value=workspace),
            patch(
                "app.intelligence.service.get_provider_selection",
                side_effect=AssertionError("Provider factory must not be called when use_ai is false"),
            ),
            TestClient(app) as client,
        ):
            benchmark_response = client.post(
                f"/api/projects/{workspace.project.id}/intelligence/benchmark/stream",
                json={"language": "en", "use_ai": False},
            )
            summary_response = client.post(
                f"/api/projects/{workspace.project.id}/intelligence/summary/stream",
                json={"language": "en", "use_ai": False},
            )

        self.assertEqual(benchmark_response.status_code, 200)
        self.assertEqual(summary_response.status_code, 200)
        for body in [benchmark_response.text, summary_response.text]:
            self.assertIn("event: chunk", body)
            self.assertIn("event: done", body)
            self.assertIn('"done":true', body)

    def test_existing_deterministic_benchmark_baseline_remains_available(self) -> None:
        workspace = workspace_fixture()
        baseline = create_benchmark(workspace)

        self.assertGreaterEqual(len(baseline), 1)
        self.assertEqual(
            [item.platform_id for item in baseline],
            [item.platform_id for item in sorted(baseline, key=lambda item: item.weighted_score, reverse=True)],
        )


if __name__ == "__main__":
    unittest.main()
