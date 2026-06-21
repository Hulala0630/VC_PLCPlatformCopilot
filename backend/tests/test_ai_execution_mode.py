from pathlib import Path
import sys
import unittest
from unittest.mock import Mock, patch


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.data import ECOSYSTEMS, PROJECT_WORKSPACES
from app.intelligence import service
from app.intelligence.models import (
    BenchmarkExplanationRequest,
    GlobalChatRequest,
    ProjectAnalysisRequest,
    ProjectChatRequest,
    ReportGenerationRequest,
    ReportSectionRewriteRequest,
)
from app.intelligence.openai_provider import ProviderCallError
from app.intelligence.provider import DeterministicPlaceholderProvider
from app.intelligence.provider_factory import ProviderSelection
from app.services import create_benchmark


PROJECT_ID = PROJECT_WORKSPACES[0].project.id
SECTION_ID = PROJECT_WORKSPACES[0].report.sections[0].id
PRIVATE_MODEL_ID = "private-model-id-that-must-not-leak"
FAKE_SECRET = "fake-secret-that-must-not-leak"


class SuccessfulProvider:
    def global_chat(self, request, platforms):
        baseline = DeterministicPlaceholderProvider().global_chat(request, platforms)
        return baseline.model_copy(
            update={
                "mode": "openai",
                "provider": "openai",
                "model_profile": "fast",
                "request_id": "safe-request-id",
                "ai_used": True,
            }
        )


class FailingProvider:
    def global_chat(self, request, platforms):
        raise ProviderCallError("timeout", "fast")


def selection(primary, *, fallback_enabled=True):
    placeholder = DeterministicPlaceholderProvider()
    return ProviderSelection(
        primary=primary,
        placeholder=placeholder,
        fallback_enabled=fallback_enabled,
        openai_active=True,
        configuration_valid=True,
    )


class RequestContractTests(unittest.TestCase):
    def test_use_ai_defaults_true_and_accepts_false(self) -> None:
        request_types = [
            (GlobalChatRequest, {"question": "Compare", "language": "en"}),
            (ProjectChatRequest, {"question": "Explain", "language": "en"}),
            (ProjectAnalysisRequest, {"language": "en"}),
            (BenchmarkExplanationRequest, {"language": "en"}),
            (ReportGenerationRequest, {"language": "en", "audience": "technical"}),
            (
                ReportSectionRewriteRequest,
                {"instruction": "Shorten", "language": "en", "audience": "technical"},
            ),
        ]
        for request_type, values in request_types:
            with self.subTest(request_type=request_type.__name__):
                self.assertTrue(request_type(**values).use_ai)
                self.assertFalse(request_type(**values, use_ai=False).use_ai)


class AIExecutionModeTests(unittest.TestCase):
    def test_ai_off_all_capabilities_bypass_provider_factory(self) -> None:
        workspace_before = PROJECT_WORKSPACES[0].model_dump()
        benchmark_before = [item.model_dump() for item in create_benchmark(PROJECT_WORKSPACES[0])]
        calls = [
            lambda: service.global_chat(
                GlobalChatRequest(question="Compare", language="en", use_ai=False)
            ),
            lambda: service.project_chat(
                PROJECT_ID,
                ProjectChatRequest(question="Explain", language="en", use_ai=False),
            ),
            lambda: service.analyze_project(
                PROJECT_ID,
                ProjectAnalysisRequest(language="en", use_ai=False),
            ),
            lambda: service.explain_benchmark(
                PROJECT_ID,
                BenchmarkExplanationRequest(language="en", use_ai=False),
            ),
            lambda: service.generate_report(
                PROJECT_ID,
                ReportGenerationRequest(language="en", audience="technical", use_ai=False),
            ),
            lambda: service.rewrite_report_section(
                PROJECT_ID,
                SECTION_ID,
                ReportSectionRewriteRequest(
                    instruction="Shorten",
                    language="en",
                    audience="technical",
                    use_ai=False,
                ),
            ),
        ]

        with patch(
            "app.intelligence.service.get_provider_selection",
            side_effect=AssertionError("AI provider factory must not be invoked"),
        ) as provider_factory:
            responses = [call() for call in calls]

        provider_factory.assert_not_called()
        for response in responses:
            self.assertEqual(response.mode, "deterministic_placeholder")
            self.assertEqual(response.provider, "placeholder")
            self.assertFalse(response.ai_used)
            self.assertIsNone(response.fallback_reason)
            self.assertIsNone(response.model_profile)

        self.assertEqual(PROJECT_WORKSPACES[0].model_dump(), workspace_before)
        self.assertEqual(
            [item.model_dump() for item in create_benchmark(PROJECT_WORKSPACES[0])],
            benchmark_before,
        )

    def test_ai_on_success_uses_configured_provider(self) -> None:
        configured = selection(SuccessfulProvider())
        with patch("app.intelligence.service.get_provider_selection", return_value=configured) as factory:
            response = service.global_chat(
                GlobalChatRequest(question="Compare", language="en", use_ai=True),
            )

        factory.assert_called_once_with()
        self.assertEqual(response.mode, "openai")
        self.assertEqual(response.provider, "openai")
        self.assertTrue(response.ai_used)
        serialized = response.model_dump_json()
        self.assertNotIn(PRIVATE_MODEL_ID, serialized)
        self.assertNotIn(FAKE_SECRET, serialized)

    def test_ai_on_provider_failure_uses_explicit_fallback(self) -> None:
        configured = selection(FailingProvider())
        with patch("app.intelligence.service.get_provider_selection", return_value=configured):
            response = service.global_chat(
                GlobalChatRequest(question="Compare", language="en", use_ai=True),
            )

        self.assertEqual(response.mode, "deterministic_fallback")
        self.assertEqual(response.provider, "placeholder")
        self.assertFalse(response.ai_used)
        self.assertEqual(response.fallback_reason, "timeout")
        self.assertEqual(response.model_profile, "fast")


if __name__ == "__main__":
    unittest.main()
