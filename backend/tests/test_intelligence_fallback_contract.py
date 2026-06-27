from pathlib import Path
import sys
import unittest
from unittest.mock import patch


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from fastapi.testclient import TestClient

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
from app.intelligence.provider_factory import ProviderSelection, build_provider_selection
from app.main import app
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


BANNED_USER_TERMS = (
    "placeholder",
    "provider",
    "fallback",
    "deterministic_fallback",
    "deterministic",
    "deterministic service",
    "metadata",
    "mock",
    "internal",
    "dev wording",
    "developer wording",
    "model id",
    "model_id",
    "api key",
    "api_key",
    "authorization header",
    "secret key",
    "scoring logic",
    "deterministic scoring",
    "persistence",
    "persisted",
    "占位符",
    "确定性逻辑",
    "模型供应商",
    "内部实现",
    "回退",
    "元数据",
    "持久化",
)


class FailingProvider:
    def __init__(self, category="timeout") -> None:
        self.category = category

    def _fail(self, profile):
        raise ProviderCallError(self.category, profile)

    def global_chat(self, request, platforms):
        self._fail("fast")

    def project_chat(self, request, workspace, benchmark):
        self._fail("balanced")

    def analyze_project(self, request, workspace, benchmark):
        self._fail("balanced")

    def explain_benchmark(self, request, workspace, benchmark):
        self._fail("balanced")

    def generate_report(self, request, workspace, benchmark):
        self._fail("quality")

    def rewrite_report_section(self, request, workspace, section, benchmark):
        self._fail("quality")


def selection(primary, *, fallback_enabled=True, openai_active=True):
    placeholder = DeterministicPlaceholderProvider()
    return ProviderSelection(
        primary=primary,
        placeholder=placeholder,
        fallback_enabled=fallback_enabled,
        openai_active=openai_active,
        configuration_valid=openai_active,
    )


def six_calls(workspace, *, use_ai: bool):
    project_id = workspace.project.id
    section_id = workspace.report.sections[0].id
    return [
        lambda: service.global_chat(
            GlobalChatRequest(question="Compare platforms", language="en", use_ai=use_ai)
        ),
        lambda: service.project_chat(
            project_id,
            ProjectChatRequest(question="Summarize the decision", language="en", use_ai=use_ai),
        ),
        lambda: service.analyze_project(
            project_id,
            ProjectAnalysisRequest(
                language="en", focus="attachments", use_ai=use_ai
            ),
        ),
        lambda: service.explain_benchmark(
            project_id,
            BenchmarkExplanationRequest(language="en", use_ai=use_ai),
        ),
        lambda: service.generate_report(
            project_id,
            ReportGenerationRequest(
                language="en", audience="technical", use_ai=use_ai
            ),
        ),
        lambda: service.rewrite_report_section(
            project_id,
            section_id,
            ReportSectionRewriteRequest(
                instruction="Make concise",
                language="en",
                audience="technical",
                use_ai=use_ai,
            ),
        ),
    ]


def user_text(response) -> str:
    localized = []
    for field in ("answer", "suggested_body"):
        value = getattr(response, field, None)
        if value is not None:
            localized.append(value)
    for field in ("assumptions", "uncertainty", "missing_inputs", "follow_up_questions"):
        localized.extend(getattr(response, field, []))
    for section in getattr(response, "sections", []):
        localized.extend([section.title, section.draft_body])
    for source in getattr(response, "sources", []):
        localized.extend([source.label, source.detail])
    return "\n".join(f"{item.zh}\n{item.en}" for item in localized).lower()


class IntelligenceFallbackContractTests(unittest.TestCase):
    def test_ai_off_returns_basic_analysis_for_all_six_interfaces(self) -> None:
        workspace = workspace_fixture()
        before = workspace.model_dump()
        with (
            patch("app.intelligence.service.get_workspace", return_value=workspace),
            patch(
                "app.intelligence.service.get_provider_selection",
                side_effect=AssertionError("AI provider factory must not be invoked"),
            ) as factory,
        ):
            results = [call() for call in six_calls(workspace, use_ai=False)]

        factory.assert_not_called()
        for result in results:
            self.assertEqual(result.execution_status, "basic_analysis")
            self.assertIsNone(result.fallback_reason)
            self.assertFalse(result.retryable)
            self.assertTrue(result.request_id)
            self.assertFalse(result.ai_used)
            content = user_text(result)
            for term in BANNED_USER_TERMS:
                self.assertNotIn(term, content)
        self.assertEqual(workspace.model_dump(), before)

    def test_ai_success_returns_consistent_status_for_all_six_interfaces(self) -> None:
        workspace = workspace_fixture()
        effects = [
            intelligence_output("global"),
            intelligence_output("project"),
            intelligence_output("attachments"),
            intelligence_output("benchmark"),
            report_output(workspace),
            rewrite_output(workspace.report.sections[0]),
        ]
        configured = build_provider_selection(
            openai_settings(),
            client=FakeClient(FakeResponses(parse_effects=effects)),
            sleep_fn=lambda _: None,
        )
        with (
            patch("app.intelligence.service.get_workspace", return_value=workspace),
            patch("app.intelligence.service.get_provider_selection", return_value=configured),
        ):
            results = [call() for call in six_calls(workspace, use_ai=True)]

        for result in results:
            self.assertEqual(result.execution_status, "ai_success")
            self.assertIsNone(result.fallback_reason)
            self.assertFalse(result.retryable)
            self.assertTrue(result.request_id)
            self.assertTrue(result.ai_used)
            serialized = result.model_dump_json()
            self.assertNotIn(FAKE_KEY, serialized)
            for model_id in MODEL_IDS.values():
                self.assertNotIn(model_id, serialized)

    def test_ai_failure_returns_consistent_fallback_for_all_six_interfaces(self) -> None:
        workspace = workspace_fixture()
        before = workspace.model_dump()
        configured = selection(FailingProvider("timeout"))
        with (
            patch("app.intelligence.service.get_workspace", return_value=workspace),
            patch("app.intelligence.service.get_provider_selection", return_value=configured),
        ):
            results = [call() for call in six_calls(workspace, use_ai=True)]

        for result in results:
            self.assertEqual(result.execution_status, "ai_fallback")
            self.assertEqual(result.fallback_reason, "timeout")
            self.assertTrue(result.retryable)
            self.assertFalse(result.ai_used)
            self.assertTrue(result.request_id.startswith("fallback-"))
            content = user_text(result)
            for term in BANNED_USER_TERMS:
                self.assertNotIn(term, content)
        self.assertEqual(workspace.model_dump(), before)

    def test_public_reason_and_retryability_mapping(self) -> None:
        cases = [
            ("timeout", "timeout", True),
            ("rate_limit", "rate_limit", True),
            ("authentication", "authentication", False),
            ("unsupported_model", "unsupported_model", False),
            ("invalid_response", "invalid_response", True),
            ("provider_server_error", "provider_unavailable", True),
            ("configuration_error", "provider_unavailable", False),
        ]
        request = GlobalChatRequest(question="Compare", language="en")
        for internal, public, retryable in cases:
            with self.subTest(internal=internal):
                configured = (
                    selection(
                        DeterministicPlaceholderProvider(),
                        openai_active=False,
                    )
                    if internal == "configuration_error"
                    else selection(FailingProvider(internal))
                )
                with patch(
                    "app.intelligence.service.get_provider_selection",
                    return_value=configured,
                ):
                    result = service.global_chat(request)
                self.assertEqual(result.execution_status, "ai_fallback")
                self.assertEqual(result.fallback_reason, public)
                self.assertEqual(result.retryable, retryable)

    def test_complete_failure_uses_safe_structured_error(self) -> None:
        configured = selection(
            FailingProvider("rate_limit"),
            fallback_enabled=False,
        )
        raw_secret = "fake-raw-secret"
        with patch("app.intelligence.service.get_provider_selection", return_value=configured):
            with TestClient(app) as client:
                response = client.post(
                    "/api/intelligence/global/chat",
                    json={"question": raw_secret, "language": "en", "use_ai": True},
                )

        self.assertEqual(response.status_code, 502)
        detail = response.json()["detail"]
        self.assertEqual(detail["error"], "intelligence_request_failed")
        self.assertEqual(detail["fallback_reason"], "rate_limit")
        self.assertTrue(detail["retryable"])
        self.assertTrue(detail["request_id"].startswith("failed-"))
        self.assertNotIn(raw_secret, response.text)

    def test_ai_engineering_language_is_rejected_and_safely_falls_back(self) -> None:
        unsafe_answers = [
            "Provider metadata placeholder",
            "deterministic_fallback exposed",
            "deterministic baseline exposed",
            "model id and API key details",
            "deterministic scoring logic",
            "mock internal dev wording",
            "占位符 确定性逻辑 模型供应商 内部实现 回退",
        ]
        for unsafe_answer in unsafe_answers:
            with self.subTest(unsafe_answer=unsafe_answer):
                unsafe = intelligence_output(unsafe_answer)
                configured = build_provider_selection(
                    openai_settings(retries=1),
                    client=FakeClient(FakeResponses(parse_effects=[unsafe, unsafe])),
                    sleep_fn=lambda _: None,
                )
                with patch("app.intelligence.service.get_provider_selection", return_value=configured):
                    result = service.global_chat(
                        GlobalChatRequest(question="Compare", language="en", use_ai=True)
                    )

                self.assertEqual(result.execution_status, "ai_fallback")
                self.assertEqual(result.fallback_reason, "invalid_response")
                self.assertTrue(result.retryable)
                content = user_text(result)
                for term in BANNED_USER_TERMS:
                    self.assertNotIn(term, content)

    def test_openapi_exposes_execution_contract_on_all_response_shapes(self) -> None:
        with TestClient(app) as client:
            schemas = client.get("/openapi.json").json()["components"]["schemas"]
        for schema_name in (
            "IntelligenceResponse",
            "ReportGenerationResponse",
            "ReportSectionRewriteResponse",
        ):
            properties = schemas[schema_name]["properties"]
            for field in (
                "execution_status",
                "fallback_reason",
                "retryable",
                "request_id",
            ):
                self.assertIn(field, properties)


if __name__ == "__main__":
    unittest.main()
