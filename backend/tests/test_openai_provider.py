import os
from pathlib import Path
from types import SimpleNamespace
import sys
import unittest
from unittest.mock import patch

import httpx
import openai


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.data import ECOSYSTEMS, PROJECT_WORKSPACES
from app.intelligence.config import AISettings
from app.intelligence.model_router import DEFAULT_MODEL_PROFILES, ModelRouter
from app.intelligence.models import (
    BenchmarkExplanationRequest,
    GlobalChatRequest,
    ProjectAnalysisRequest,
    ProjectChatRequest,
    ReportGenerationRequest,
    ReportSectionRewriteRequest,
)
from app.intelligence.openai_provider import OpenAIProvider
from app.intelligence.provider import DeterministicPlaceholderProvider
from app.intelligence.provider_factory import ProviderSelection, build_provider_selection
from app.intelligence import service
from app.main import app
from app.services import compute_project_readiness, create_benchmark
from fastapi.testclient import TestClient


FAKE_KEY = "fake-phase-two-key"
MODEL_IDS = {
    "fast": "private-fast-model-id",
    "balanced": "private-balanced-model-id",
    "quality": "private-quality-model-id",
}


def openai_settings(*, fallback: bool = True, retries: int = 2) -> AISettings:
    values = {
        "AI_PROVIDER": "openai",
        "OPENAI_API_KEY": FAKE_KEY,
        "OPENAI_BASE_URL": "https://example.invalid/v1",
        "AI_MODEL_FAST": MODEL_IDS["fast"],
        "AI_MODEL_BALANCED": MODEL_IDS["balanced"],
        "AI_MODEL_QUALITY": MODEL_IDS["quality"],
        "AI_REQUEST_TIMEOUT_SECONDS": "30",
        "AI_MAX_RETRIES": str(retries),
        "AI_FALLBACK_ENABLED": "true" if fallback else "false",
    }
    with patch.dict(os.environ, values, clear=True):
        return AISettings(_env_file=None)


def placeholder_settings() -> AISettings:
    with patch.dict(os.environ, {"AI_PROVIDER": "placeholder"}, clear=True):
        return AISettings(_env_file=None)


def workspace_fixture():
    workspace = PROJECT_WORKSPACES[0].model_copy(deep=True)
    readiness = compute_project_readiness(workspace)
    return workspace.model_copy(update={"readiness": readiness})


def intelligence_output(answer: str = "Structured answer") -> dict:
    return {
        "answer": {"zh": f"{answer} 中文", "en": answer},
        "assumptions": [{"zh": "结构化假设", "en": "Structured assumption"}],
        "uncertainty": [{"zh": "结构化不确定性", "en": "Structured uncertainty"}],
        "follow_up_questions": [{"zh": "下一步？", "en": "What next?"}],
    }


def report_output(workspace) -> dict:
    return {
        "sections": [
            {
                "section_id": section.id,
                "draft_body": {
                    "zh": f"{section.id} 建议稿",
                    "en": f"{section.id} draft suggestion",
                },
            }
            for section in workspace.report.sections
        ],
        "assumptions": [{"zh": "报告假设", "en": "Report assumption"}],
        "uncertainty": [{"zh": "报告不确定性", "en": "Report uncertainty"}],
    }


class FakeResponses:
    def __init__(self, *, parse_effects=None, create_effects=None) -> None:
        self.parse_effects = list(parse_effects or [])
        self.create_effects = list(create_effects or [])
        self.parse_calls: list[dict] = []
        self.create_calls: list[dict] = []

    def parse(self, **kwargs):
        self.parse_calls.append(kwargs)
        effect = self.parse_effects.pop(0)
        if isinstance(effect, Exception):
            raise effect
        return SimpleNamespace(
            output_parsed=effect,
            _request_id=f"request-{len(self.parse_calls)}",
            id=f"response-{len(self.parse_calls)}",
        )

    def create(self, **kwargs):
        self.create_calls.append(kwargs)
        effect = self.create_effects.pop(0) if self.create_effects else SimpleNamespace(id="connection")
        if isinstance(effect, Exception):
            raise effect
        return effect


class FakeClient:
    def __init__(self, responses: FakeResponses) -> None:
        self.responses = responses


def timeout_error() -> openai.APITimeoutError:
    return openai.APITimeoutError(httpx.Request("POST", "https://example.invalid/v1/responses"))


def rate_limit_error(raw_message: str = "raw provider detail") -> openai.RateLimitError:
    request = httpx.Request("POST", "https://example.invalid/v1/responses")
    response = httpx.Response(429, request=request)
    return openai.RateLimitError(raw_message, response=response, body=None)


class ProviderFactoryAndRoutingTests(unittest.TestCase):
    def test_provider_factory_selection(self) -> None:
        placeholder = build_provider_selection(placeholder_settings())
        self.assertIsInstance(placeholder.primary, DeterministicPlaceholderProvider)
        self.assertFalse(placeholder.openai_active)

        fake_client = FakeClient(FakeResponses())
        selected = build_provider_selection(openai_settings(), client=fake_client)
        self.assertIsInstance(selected.primary, OpenAIProvider)
        self.assertTrue(selected.openai_active)

        values = {
            "AI_PROVIDER": "openai",
            "OPENAI_API_KEY": FAKE_KEY,
            "AI_MODEL_FAST": "",
            "AI_MODEL_BALANCED": "",
            "AI_MODEL_QUALITY": "",
        }
        with patch.dict(os.environ, values, clear=True):
            incomplete = build_provider_selection(AISettings(_env_file=None))
        self.assertIsInstance(incomplete.primary, DeterministicPlaceholderProvider)
        self.assertFalse(incomplete.openai_active)
        self.assertFalse(incomplete.configuration_valid)

    def test_model_routing_defaults_and_override(self) -> None:
        router = ModelRouter(openai_settings())
        expected = {
            "global_chat": "fast",
            "project_chat": "balanced",
            "project_analysis": "balanced",
            "benchmark_explanation": "balanced",
            "report_generation": "quality",
            "report_section_rewrite": "quality",
            "connection_test": "fast",
        }
        self.assertEqual(DEFAULT_MODEL_PROFILES, expected)
        for capability, profile in expected.items():
            with self.subTest(capability=capability):
                self.assertEqual(router.profile_for(capability), profile)
        self.assertEqual(router.profile_for("global_chat", "quality"), "quality")
        self.assertEqual(router.model_for("quality"), MODEL_IDS["quality"])


class OpenAIProviderTests(unittest.TestCase):
    def test_all_capabilities_use_structured_responses_and_default_profiles(self) -> None:
        workspace = workspace_fixture()
        benchmark = create_benchmark(workspace)
        effects = [
            intelligence_output("global"),
            intelligence_output("project"),
            intelligence_output("analysis"),
            intelligence_output("benchmark"),
            report_output(workspace),
            intelligence_output("rewrite"),
        ]
        responses = FakeResponses(parse_effects=effects)
        provider = OpenAIProvider(openai_settings(), client=FakeClient(responses), sleep_fn=lambda _: None)

        results = [
            provider.global_chat(GlobalChatRequest(question="Compare", language="en"), ECOSYSTEMS[:2]),
            provider.project_chat(ProjectChatRequest(question="Why?", language="en"), workspace, benchmark),
            provider.analyze_project(ProjectAnalysisRequest(language="zh"), workspace, benchmark),
            provider.explain_benchmark(BenchmarkExplanationRequest(language="en"), workspace, benchmark),
            provider.generate_report(ReportGenerationRequest(language="en", audience="executive"), workspace, benchmark),
            provider.rewrite_report_section(
                ReportSectionRewriteRequest(instruction="Shorten", language="en", audience="executive"),
                workspace,
                workspace.report.sections[0],
                benchmark,
            ),
        ]

        self.assertEqual(
            [item.model_profile for item in results],
            ["fast", "balanced", "balanced", "balanced", "quality", "quality"],
        )
        for item in results:
            self.assertEqual(item.mode, "openai")
            self.assertEqual(item.provider, "openai")
            self.assertTrue(item.ai_used)
            self.assertFalse(item.document_parsing_used)
            serialized = item.model_dump_json()
            self.assertNotIn(FAKE_KEY, serialized)
            for model_id in MODEL_IDS.values():
                self.assertNotIn(model_id, serialized)

        generated = results[4]
        self.assertEqual(
            [item.section_id for item in generated.sections],
            [item.id for item in workspace.report.sections],
        )
        self.assertEqual(
            [item.title for item in generated.sections],
            [item.title for item in workspace.report.sections],
        )

    def test_quality_override_uses_requested_profile_without_exposing_model_id(self) -> None:
        responses = FakeResponses(parse_effects=[intelligence_output()])
        provider = OpenAIProvider(openai_settings(), client=FakeClient(responses), sleep_fn=lambda _: None)
        result = provider.global_chat(
            GlobalChatRequest(question="Compare", language="en", quality="quality"),
            ECOSYSTEMS[:2],
        )
        self.assertEqual(result.model_profile, "quality")
        self.assertEqual(responses.parse_calls[0]["model"], MODEL_IDS["quality"])
        self.assertNotIn(MODEL_IDS["quality"], result.model_dump_json())

    def test_timeout_and_rate_limit_are_retried(self) -> None:
        for first_error in [timeout_error(), rate_limit_error()]:
            with self.subTest(error=type(first_error).__name__):
                responses = FakeResponses(parse_effects=[first_error, intelligence_output()])
                provider = OpenAIProvider(
                    openai_settings(retries=1),
                    client=FakeClient(responses),
                    sleep_fn=lambda _: None,
                )
                result = provider.global_chat(
                    GlobalChatRequest(question="Compare", language="en"),
                    ECOSYSTEMS[:2],
                )
                self.assertEqual(result.mode, "openai")
                self.assertEqual(len(responses.parse_calls), 2)

    def test_attachment_context_is_metadata_only(self) -> None:
        workspace = workspace_fixture()
        responses = FakeResponses(parse_effects=[intelligence_output()])
        provider = OpenAIProvider(openai_settings(), client=FakeClient(responses), sleep_fn=lambda _: None)
        provider.project_chat(
            ProjectChatRequest(question="Review attachments", language="en"),
            workspace,
            create_benchmark(workspace),
        )
        prompt_input = responses.parse_calls[0]["input"]
        self.assertIn('"content_parsed":false', prompt_input)
        self.assertIn(workspace.attachments[0].file_name, prompt_input)
        self.assertNotIn("file_content", prompt_input)

    def test_report_rewrite_isolated_and_workspace_is_not_mutated(self) -> None:
        workspace = workspace_fixture()
        before = workspace.model_dump()
        responses = FakeResponses(parse_effects=[intelligence_output("rewrite only")])
        provider = OpenAIProvider(openai_settings(), client=FakeClient(responses), sleep_fn=lambda _: None)
        result = provider.rewrite_report_section(
            ReportSectionRewriteRequest(instruction="Shorten", language="en", audience="technical"),
            workspace,
            workspace.report.sections[0],
            create_benchmark(workspace),
        )
        self.assertEqual(workspace.model_dump(), before)
        prompt_input = responses.parse_calls[0]["input"]
        self.assertIn(workspace.report.sections[0].id, prompt_input)
        if len(workspace.report.sections) > 1:
            self.assertNotIn(workspace.report.sections[1].id, prompt_input)
        self.assertEqual(result.scope, "report_section")

    def test_connection_test_success_and_failure(self) -> None:
        success_responses = FakeResponses(create_effects=[SimpleNamespace(id="ok")])
        ticks = iter([1.0, 1.025])
        success = OpenAIProvider(
            openai_settings(),
            client=FakeClient(success_responses),
            sleep_fn=lambda _: None,
            clock=lambda: next(ticks),
        ).connection_test()
        self.assertTrue(success.connected)
        self.assertEqual(success.model_profile, "fast")
        self.assertEqual(success.latency_ms, 25)
        self.assertNotIn(MODEL_IDS["fast"], success.model_dump_json())

        failure_responses = FakeResponses(create_effects=[timeout_error(), timeout_error(), timeout_error()])
        failure = OpenAIProvider(
            openai_settings(retries=2),
            client=FakeClient(failure_responses),
            sleep_fn=lambda _: None,
            clock=lambda: 1.0,
        ).connection_test()
        self.assertFalse(failure.connected)
        self.assertEqual(failure.error_category, "timeout")
        self.assertEqual(len(failure_responses.create_calls), 3)


class FallbackAndRouteTests(unittest.TestCase):
    def selection(self, *, fallback: bool, effects) -> ProviderSelection:
        responses = FakeResponses(parse_effects=effects)
        settings = openai_settings(fallback=fallback, retries=1)
        return build_provider_selection(settings, client=FakeClient(responses), sleep_fn=lambda _: None)

    def test_fallback_enabled_is_explicit(self) -> None:
        selection = self.selection(fallback=True, effects=[timeout_error(), timeout_error()])
        with patch("app.intelligence.service.get_provider_selection", return_value=selection):
            result = service.global_chat(GlobalChatRequest(question="Compare", language="en"))
        self.assertEqual(result.mode, "deterministic_fallback")
        self.assertEqual(result.provider, "placeholder")
        self.assertEqual(result.model_profile, "fast")
        self.assertEqual(result.fallback_reason, "timeout")
        self.assertFalse(result.ai_used)

    def test_fallback_disabled_returns_sanitized_api_error(self) -> None:
        raw_error = "raw detail with fake-phase-two-key and private-fast-model-id"
        selection = self.selection(fallback=False, effects=[rate_limit_error(raw_error), rate_limit_error(raw_error)])
        with patch("app.intelligence.service.get_provider_selection", return_value=selection):
            with TestClient(app) as client:
                response = client.post(
                    "/api/intelligence/global/chat",
                    json={"question": "Compare", "language": "en", "platform_ids": []},
                )
        self.assertEqual(response.status_code, 502)
        self.assertEqual(response.json(), {"detail": {"error_category": "rate_limit"}})
        self.assertNotIn(FAKE_KEY, response.text)
        self.assertNotIn(MODEL_IDS["fast"], response.text)
        self.assertNotIn(raw_error, response.text)

    def test_invalid_structured_response_falls_back(self) -> None:
        selection = self.selection(fallback=True, effects=[None, None])
        with patch("app.intelligence.service.get_provider_selection", return_value=selection):
            result = service.global_chat(GlobalChatRequest(question="Compare", language="en"))
        self.assertEqual(result.mode, "deterministic_fallback")
        self.assertEqual(result.fallback_reason, "invalid_response")

    def test_connection_endpoint_returns_safe_shape(self) -> None:
        responses = FakeResponses(create_effects=[SimpleNamespace(id="ok")])
        selection = build_provider_selection(openai_settings(), client=FakeClient(responses), sleep_fn=lambda _: None)
        with patch("app.intelligence.service.get_provider_selection", return_value=selection):
            with TestClient(app) as client:
                response = client.post("/api/intelligence/connection-test")
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(set(body), {"connected", "provider", "model_profile", "latency_ms", "error_category"})
        self.assertTrue(body["connected"])
        self.assertEqual(body["model_profile"], "fast")
        self.assertNotIn(FAKE_KEY, response.text)
        for model_id in MODEL_IDS.values():
            self.assertNotIn(model_id, response.text)


if __name__ == "__main__":
    unittest.main()
