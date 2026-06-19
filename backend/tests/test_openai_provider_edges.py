from pathlib import Path
import sys
import unittest
from unittest.mock import patch

import httpx
import openai


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.intelligence.models import GlobalChatRequest, ReportGenerationRequest
from app.intelligence.openai_provider import OpenAIProvider, ProviderCallError
from app.intelligence.provider_factory import build_provider_selection
from app.intelligence import service
from app.main import app
from app.services import create_benchmark
from fastapi.testclient import TestClient
from tests.test_openai_provider import (
    FakeClient,
    FakeResponses,
    intelligence_output,
    openai_settings,
    placeholder_settings,
    report_output,
    workspace_fixture,
)


def api_status_error(error_type, status_code: int, message: str):
    request = httpx.Request("POST", "https://example.invalid/v1/responses")
    response = httpx.Response(status_code, request=request)
    return error_type(message, response=response, body=None)


class ProviderRetryBoundaryTests(unittest.TestCase):
    def test_connection_test_uses_viable_output_budget(self) -> None:
        responses = FakeResponses()
        provider = OpenAIProvider(
            openai_settings(),
            client=FakeClient(responses),
            sleep_fn=lambda _: None,
        )

        result = provider.connection_test()

        self.assertTrue(result.connected)
        self.assertGreaterEqual(responses.create_calls[0]["max_output_tokens"], 64)

    def test_authentication_failure_is_not_retried(self) -> None:
        responses = FakeResponses(
            parse_effects=[api_status_error(openai.AuthenticationError, 401, "private auth detail")]
        )
        provider = OpenAIProvider(
            openai_settings(retries=2),
            client=FakeClient(responses),
            sleep_fn=lambda _: None,
        )

        with self.assertRaises(ProviderCallError) as raised:
            provider.global_chat(GlobalChatRequest(question="Compare", language="en"), [])

        self.assertEqual(raised.exception.category, "authentication")
        self.assertEqual(len(responses.parse_calls), 1)

    def test_unsupported_model_failure_is_not_retried(self) -> None:
        responses = FakeResponses(
            parse_effects=[api_status_error(openai.NotFoundError, 404, "private model detail")]
        )
        provider = OpenAIProvider(
            openai_settings(retries=2),
            client=FakeClient(responses),
            sleep_fn=lambda _: None,
        )

        with self.assertRaises(ProviderCallError) as raised:
            provider.global_chat(GlobalChatRequest(question="Compare", language="en"), [])

        self.assertEqual(raised.exception.category, "unsupported_model")
        self.assertEqual(len(responses.parse_calls), 1)

    def test_unsupported_structured_format_is_categorized_safely(self) -> None:
        request = httpx.Request("POST", "https://example.invalid/v1/responses")
        response = httpx.Response(400, request=request)
        error = openai.BadRequestError(
            "private structured-output detail",
            response=response,
            body={"type": "invalid_request_error", "param": "text.format"},
        )
        responses = FakeResponses(parse_effects=[error])
        provider = OpenAIProvider(
            openai_settings(retries=2),
            client=FakeClient(responses),
            sleep_fn=lambda _: None,
        )

        with self.assertRaises(ProviderCallError) as raised:
            provider.global_chat(GlobalChatRequest(question="Compare", language="en"), [])

        self.assertEqual(raised.exception.category, "unsupported_response_format")
        self.assertEqual(len(responses.parse_calls), 1)

    def test_provider_server_failure_is_retried(self) -> None:
        responses = FakeResponses(
            parse_effects=[
                api_status_error(openai.InternalServerError, 500, "private server detail"),
                intelligence_output("recovered"),
            ]
        )
        provider = OpenAIProvider(
            openai_settings(retries=1),
            client=FakeClient(responses),
            sleep_fn=lambda _: None,
        )

        result = provider.global_chat(GlobalChatRequest(question="Compare", language="en"), [])

        self.assertEqual(result.mode, "openai")
        self.assertEqual(len(responses.parse_calls), 2)


class StructuredOutputBoundaryTests(unittest.TestCase):
    def test_invalid_report_section_ids_trigger_explicit_fallback(self) -> None:
        workspace = workspace_fixture()
        invalid_report = report_output(workspace)
        invalid_report["sections"] = list(reversed(invalid_report["sections"]))
        responses = FakeResponses(parse_effects=[invalid_report])
        selection = build_provider_selection(
            openai_settings(fallback=True),
            client=FakeClient(responses),
            sleep_fn=lambda _: None,
        )
        before = workspace.model_dump()

        with (
            patch("app.intelligence.service.get_provider_selection", return_value=selection),
            patch("app.intelligence.service.get_workspace", return_value=workspace),
        ):
            result = service.generate_report(
                workspace.project.id,
                ReportGenerationRequest(language="en", audience="executive"),
            )

        self.assertEqual(result.mode, "deterministic_fallback")
        self.assertEqual(result.fallback_reason, "invalid_response")
        self.assertFalse(result.ai_used)
        self.assertEqual(workspace.model_dump(), before)


class IntelligenceRouteBoundaryTests(unittest.TestCase):
    def test_invalid_quality_profile_is_rejected_before_provider_call(self) -> None:
        with TestClient(app) as client:
            response = client.post(
                "/api/intelligence/global/chat",
                json={"question": "Compare", "language": "en", "quality": "maximum"},
            )

        self.assertEqual(response.status_code, 422)

    def test_placeholder_connection_test_has_safe_contract(self) -> None:
        selection = build_provider_selection(placeholder_settings())
        with patch("app.intelligence.service.get_provider_selection", return_value=selection):
            with TestClient(app) as client:
                response = client.post("/api/intelligence/connection-test")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "connected": False,
                "provider": "placeholder",
                "model_profile": None,
                "latency_ms": 0,
                "error_category": "configuration_error",
            },
        )


if __name__ == "__main__":
    unittest.main()
